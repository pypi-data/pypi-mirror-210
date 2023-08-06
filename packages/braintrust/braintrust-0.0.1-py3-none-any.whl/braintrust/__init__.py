import atexit
import datetime
import json
import logging
import os
import queue
import threading
import traceback
import urllib.parse
import uuid
from functools import cache as _cache
from getpass import getpass
from typing import Any

import git
import openai
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .cache import API_INFO_PATH, CACHE_PATH
from .oai import run_cached_request


# XXX Refactor this to use some kind of documentable dataclass
class BrainTrustState:
    def __init__(self):
        self.current_project = None
        self.current_experiment = None


_state = BrainTrustState()


def urljoin(*parts):
    return "/".join([x.lstrip("/") for x in parts])


API_URL = None
ORG_ID = None
LOG_URL = None


class HTTPConnection:
    def __init__(self, base_url=API_URL):
        self.session = requests.Session()
        self.base_url = base_url

        # Following a suggestion in https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        retry = Retry(connect=10, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def set_token(self, token):
        token = token.rstrip("\n")
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, path, *args, **kwargs):
        return self.session.get(urljoin(self.base_url, path), *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.session.post(urljoin(self.base_url, path), *args, **kwargs)


@_cache
def api_conn():
    return HTTPConnection(LOG_URL)  # TODO: Fix to use global install


def api_get(object_type, args=None):
    resp = api_conn().get(f"/{object_type}", params=args)
    assert resp.ok, resp.text
    return resp.json()


def api_insert(object_type, args):
    resp = api_conn().post(
        f"/{object_type}",
        json=args,
    )
    assert resp.ok, resp.text
    return resp.json()


class ModelWrapper:
    _ENDPOINT = None

    def __getattr__(self, name: str) -> Any:
        return self.data[name]


@_cache
def _user_info():
    return api_get("ping")


class Project(ModelWrapper):
    _ENDPOINT = "projects"

    def __init__(self, name):
        unique_key, insert_args = {"name": name}, {"org_id": _user_info()["organizations"][0]["id"]}

        # Can we have an upsert (or insert if not exists) method instead?
        existing = []
        if unique_key:
            existing = api_get(self._ENDPOINT, unique_key)

        if not existing:
            insert_args.update(unique_key)
            existing = api_insert(self._ENDPOINT, insert_args)

        if existing:
            self.data = existing[0]
        else:
            assert False, "Unable to find record in " + self._ENDPOINT


def guess_notebook_block_name():
    try:
        import IPython

        ipython = IPython.get_ipython()

        cell_text = "\n".join(reversed([ipython.history_manager.get_tail(i + 1)[0][2] for i in range(3)]))
    except Exception:
        return None

    return [
        {
            "role": "system",
            "content": """\
You can generate two word summaries for machine learning experiment names, based
on the last 3 blocks of code in your notebook.
The experiment name should be exactly two words, concatenated with a hyphen, all lowercase.
The input format is recently executed python code. For example, "foo-bar" is valid but
"foo-bar-baz" is not.""",
        },
        {
            "role": "user",
            "content": f"{cell_text[:4096]}",
        },
    ]


def guess_git_experiment_name():
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None

    branch = repo.active_branch.name
    diff = repo.git.diff(repo.head.commit.tree)
    if not diff and len(repo.head.commit.parents) > 0:
        diff = repo.head.commit.message + "\n" + repo.git.diff(repo.head.commit.tree, repo.head.commit.parents[0].tree)

    return [
        {
            "role": "system",
            "content": """\
You can generate two word summaries for machine learning experiment names, based
on the branch name and an optional "diff" of the experiment's code on top of the branch.
The experiment name should be exactly two words, concatenated with a hyphen, all lowercase.
The input format is the output of "git diff". For example, "foo-bar" is valid but
"foo-bar-baz" is not.""",
        },
        {
            "role": "user",
            "content": f"Branch: {branch}" + (f"\n\nDiff:\n{diff[:4096]}" if diff else ""),
        },
    ]


def guess_experiment_name():
    if openai.api_key is None:
        return None

    messages = guess_notebook_block_name()
    if not messages:
        messages = guess_git_experiment_name()

    if not messages:
        return None

    resp = run_cached_request(
        Completion=openai.ChatCompletion,
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=128,
        temperature=0.7,
    )

    name = None
    if len(resp["choices"]) > 0:
        name = "-".join(resp["choices"][0]["message"]["content"].split("-")[:2])
        # Strip punctuation and whitespace from the prefix and suffix
        name = name.strip(" .,;:!?-")
    return name


class _LogThread:
    def __init__(self, name=None):
        self.thread = threading.Thread(target=self._publisher, daemon=True)
        self.started = False

        log_namespace = "braintrust"
        if name:
            log_namespace += f" [{name}]"

        self.logger = logging.getLogger(log_namespace)

        try:
            queue_size = int(os.environ.get("BRAINTRUST_QUEUE_SIZE"))
        except Exception:
            queue_size = 1000
        self.queue = queue.Queue(maxsize=queue_size)

        atexit.register(self._finalize)

    def log(self, *args):
        self._start()
        for event in args:
            self.queue.put(event)

    def _start(self):
        if not self.started:
            self.thread.start()
            self.started = True

    def _finalize(self):
        self.logger.info("Flushing final log events...")
        self._flush()

    def _publisher(self, batch_size=None):
        kwargs = {}
        if batch_size is not None:
            kwargs["batch_size"] = batch_size

        while True:
            try:
                item = self.queue.get()
            except queue.Empty:
                continue

            try:
                self._flush(initial_items=[item], **kwargs)
            except Exception:
                traceback.print_exc()

    def _flush(self, initial_items=None, batch_size=100):
        items = initial_items or []
        while True:
            while len(items) < batch_size:
                try:
                    items.append(self.queue.get_nowait())
                except queue.Empty:
                    break

            api_insert("logs", items)

            if len(items) < batch_size:
                break

            items.clear()


class Experiment(ModelWrapper):
    def __init__(self, project, name=None, description=None):
        self.project = project
        args = {"project_id": project.id}

        if not name:
            name = guess_experiment_name()

        if name:
            args["name"] = name

        if description:
            args["description"] = description

        self.data = api_insert("register-experiment", args)[0]
        self.logger = _LogThread(name=name)

    def log(self, inputs, output, expected=None, scores=None, metadata=None):
        user_id = _user_info()["id"]
        args = {
            "id": str(uuid.uuid4()),
            "inputs": inputs,
            "output": json.dumps(output),
            "project_id": self.project.id,
            "experiment_id": self.id,
            "user_id": user_id,
            "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        if expected:
            args["expected"] = json.dumps(expected)
        if scores:
            args["scores"] = scores
        if metadata:
            args["metadata"] = metadata

        # TODO: We should queue this up in the background
        self.logger.log(args)
        return args["id"]

    def summarize(self):
        # TODO: Show results so far here as well
        org_name = _user_info()["organizations"][0]["name"]

        project_url = f"{API_URL}/app/{urllib.parse.quote(org_name)}/{urllib.parse.quote(self.project.name)}"
        experiment_url = f"{project_url}/{urllib.parse.quote(self.name)}"

        print(f"See results for all experiments in {self.project.name} at {project_url}")
        print(f"See results for {self.name} at {experiment_url}")


def login(api_url=os.environ.get("BRAINTRUST_API_URL", "https://www.braintrustdata.com")):
    global API_URL, ORG_ID, LOG_URL

    API_URL = api_url

    os.makedirs(CACHE_PATH, exist_ok=True)

    api_info = None
    ping_ok = False
    if os.path.exists(API_INFO_PATH):
        with open(API_INFO_PATH) as f:
            api_info = json.load(f)

        LOG_URL = api_info.get("log_url")
        ORG_ID = api_info.get("org_id")
        conn = api_conn()

        token = api_info.get("token")
        if token is not None:
            conn.set_token(token)

        ping_resp = conn.get("ping")
        ping_ok = ping_resp.ok

    if not ping_ok:
        print(f"Please copy your API token from {API_URL}/app/token")
        temp_token = getpass("Token: ")

        resp = requests.post(urljoin(API_URL, "/api/id-token"), json={"token": temp_token})
        assert resp.ok, f"Failed to acquire token: {resp.text}"
        info = resp.json()
        token, ORG_ID, LOG_URL = info["token"], info["org_info"][0]["id"], info["org_info"][0]["api_url"]

        with open(API_INFO_PATH, "w") as f:
            json.dump({"token": token, "org_id": ORG_ID, "log_url": LOG_URL}, f)

        conn = api_conn()
        conn.set_token(token)

    assert conn, "Conn should be set at this point (a bug)"
    resp = conn.get("ping")
    assert resp.ok, "Invalid token: " + resp.text


def init(project, api_url=None, experiment=None, description=None):
    kwargs = {}
    if api_url:
        kwargs["api_url"] = api_url
    login(**kwargs)

    _state.current_project = Project(project)
    _state.current_experiment = Experiment(_state.current_project, name=experiment, description=description)
    return _state.current_experiment


def log(inputs, output, expected=None, scores=None, metadata=None):
    # XXX Fix with proper exception
    assert _state.current_experiment, "not initialized"
    return _state.current_experiment.log(
        inputs=inputs, output=output, expected=expected, scores=scores, metadata=metadata
    )


__all__ = ["init", "log"]
