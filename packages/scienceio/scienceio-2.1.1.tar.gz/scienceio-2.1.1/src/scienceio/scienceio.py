import configparser
import enum
import json
import os
import requests
import time

from http import HTTPStatus
from pathlib import Path
from typing import Optional

API_URL: str = "https://api.aws.science.io/v2"
HELP_EMAIL: str = "api_support@science.io"
SETTINGS_DIR: Path = Path.home() / ".scienceio"
BASE_DELAY_SEC: float = 1
BACKOFF_FACTOR: float = 2
MAX_RETRY_ATTEMPTS: int = 8
DEFAULT_ERROR_MESSAGE = f"An error occured, please email {HELP_EMAIL} for assistance."
RETRY_AFTER_HEADER = "retry-after"


class Model(str, enum.Enum):
    STRUCTURE = "structure"
    IDENTIFY_PHI = "identify-phi"
    REDACT_PHI = "redact-phi"

    @property
    def input_text_key_name(self) -> str:
        if self is Model.IDENTIFY_PHI or self is Model.REDACT_PHI:
            return "input_text"

        return "text"


class ScienceIOError(Exception):
    """Base class for all exceptions that are raised by the ScienceIO SDK."""


class HTTPError(ScienceIOError):
    """Raised when an HTTP error occurs when using the ScienceIO SDK."""

    def __init__(self, status_code: int, message: str, headers: dict):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers


class TimeoutError(ScienceIOError):
    """Raised when a call to the ScienceIO API times out."""

    def __init__(self, msg):
        self.msg = msg


class ScienceIO(object):
    def __init__(self, enable_rate_limit_retry: bool = True):
        """Initializer for the ScienceIO client. The client will attempt to
        configure itself by trying to read from environment variables, if set.
        If unable to, the config values will be read from the ScienceIO config
        file.
        """

        # Create a persistent session across requests.
        # https://docs.python-requests.org/en/master/user/advanced/
        self.session = requests.Session()
        self.session.params = {}
        self._enable_rate_limit_retry = enable_rate_limit_retry

        # Lazy loading of configuration (no need to try and load the settings if user specifies
        # their own API ID and secret). Also, this prevents breakage when in envs with no
        # settings file, such as test environments or hosted Jupyter notebooks.
        config = None

        def get_config_value(key: str) -> str:
            nonlocal config
            if config is None:
                config = configparser.RawConfigParser()
                config.read(SETTINGS_DIR / "config")

            return config["SETTINGS"][key].strip("\"'")

        # Handles config values from user arguments, config file, and user
        # input, in that order from most to least preferred.
        write_out_conf = False

        def get_value(initial: Optional[str], key: str, human_name: str) -> str:
            nonlocal write_out_conf
            if initial is None:
                try:
                    return get_config_value(key)
                except KeyError:
                    user_input = str(
                        input(f"Please provide your ScienceIO API key {human_name}: ")
                    )

                    # User input was collected, flag the config file for rewriting.
                    write_out_conf = True
                    return user_input

            return initial

        # API endpoints to use.
        self.api_url = os.environ.get("SCIENCEIO_API_URL", API_URL)

        # API key and secret (with extra handling for env vars, config file, and user prompts).
        self.api_id = get_value(os.environ.get("SCIENCEIO_KEY_ID"), "KEY_ID", "id")
        self.api_secret = get_value(
            os.environ.get("SCIENCEIO_KEY_SECRET"), "KEY_SECRET", "secret"
        )

        # Construct the headers.
        self.headers = {
            "Content-Type": "application/json",
            "x-api-id": self.api_id,
            "x-api-secret": self.api_secret,
        }

        # Write out the API key ID and secret if either or both of those values
        # needed user input.
        if write_out_conf:
            # Create a new `ConfigParser` to hold the configuration we want to
            # write to the config file.
            new_conf = configparser.ConfigParser()
            new_conf["SETTINGS"] = {
                "KEY_ID": self.api_id,
                "KEY_SECRET": self.api_secret,
            }

            # Create the config directory (and any parents) if it does not
            # already exist.
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

            # Write out the new config.
            with (SETTINGS_DIR / "config").open("w") as fp:
                new_conf.write(fp)

    def _construct_submit_url(self, model: Model) -> str:
        """Helper method to construct a submit URL for a given model."""
        return f"{self.api_url}/{model.value}"

    def _construct_poll_url(self, request_id: str, model: Model) -> str:
        """Helper method to construct a polling URL for a given model and request id."""
        return f"{self.api_url}/{model.value}/{request_id}"

    def _process(self, text: str, model: Model) -> dict:
        request_id = self._submit_request(text=text, model=model)

        curr_delay = BASE_DELAY_SEC
        for i in range(MAX_RETRY_ATTEMPTS):
            if i > 0:
                # Delay before attempting to retrieve results, if not on the first loop.
                time.sleep(curr_delay)
                curr_delay *= BACKOFF_FACTOR

            payload = self._poll_response(request_id=request_id, model=model)

            if payload is not None:
                return payload

        # Here, we've exhausted all of our retry attempts, so fail.
        raise TimeoutError(f"{model.value} request timed out, try again later")

    def _submit_request(self, text: str, model: Model) -> str:
        submit_url = self._construct_submit_url(model)
        key_name = model.input_text_key_name

        response = self.session.post(
            submit_url,
            json={key_name: text},
            headers=self.headers,
        )

        if (
            self._enable_rate_limit_retry
            and response.status_code == HTTPStatus.TOO_MANY_REQUESTS
        ):
            retry_after = int(response.headers.get(RETRY_AFTER_HEADER, 0))
            time.sleep(retry_after)
            return self._submit_request(text, model)

        payload = _response_handler(response)

        request_id = payload["request_id"]

        return request_id

    def _poll_response(self, request_id: str, model: Model) -> Optional[dict]:
        poll_url = self._construct_poll_url(request_id=request_id, model=model)

        response = self.session.get(
            poll_url,
            headers=self.headers,
        )

        if (
            self._enable_rate_limit_retry
            and response.status_code == HTTPStatus.TOO_MANY_REQUESTS
        ):
            retry_after = int(response.headers.get(RETRY_AFTER_HEADER, 0))
            time.sleep(retry_after)
            return self._poll_response(request_id, model)

        payload = _response_handler(response)

        return _poll_payload_handler(payload)


def _response_handler(response: requests.Response) -> dict:
    status_code = response.status_code
    payload = response.json()

    if 400 <= status_code <= 599:
        error_payload = payload.get("detail", DEFAULT_ERROR_MESSAGE)

        error_json_str = json.dumps(error_payload)

        raise HTTPError(
            status_code=status_code, message=error_json_str, headers=response.headers
        )

    return payload


def _poll_payload_handler(payload: dict) -> Optional[dict]:
    status = payload["inference_status"]
    if status == "ERRORED" or status == "EXPIRED":
        raise ScienceIOError(payload["message"])
    elif status == "COMPLETED":
        return payload["inference_result"]
    elif status == "SUBMITTED":
        return None
    else:
        raise ScienceIOError("unknown status")


# Dynamically generate pre-baked methods for known model types.
# This needs to be split out into a separate method because of closures and how
# they work in Python.
# See: https://code.activestate.com/recipes/502271-these-nasty-closures-caveats-for-the-closure-enthu
def _make_pre_baked_methods(model: Model):
    # Convert the model name into a identifier-friendly lowercase form.
    model_ident = model.name.lower()

    def x(self, text: str) -> dict:
        return self._process(text=text, model=model)

    x.__doc__ = "\n".join(
        (
            f"Make a {model.value} request to the ScienceIO API, and returns the result when completed.",
            "",
            "Args:",
            f"    text (str): The input text to process using the {model.value} model.",
            "",
            "Returns:",
            f"    dict: The output of the {model.value} API call with the given input text.",
        )
    )

    def submit_x_request(self, text: str) -> str:
        return self._submit_request(text=text, model=model)

    submit_x_request.__doc__ = "\n".join(
        (
            f"Submits a {model.value} request to the ScienceIO API, and returns a request id to fetch results at a later time.",
            "",
            "Args:",
            f"    text (str): The input text to process using the {model.value} model.",
            "",
            "Returns:",
            f"    str: The id for this request, usable with `get_{model_ident}_response`.",
        )
    )

    def poll_x_response(self, request_id: str) -> Optional[dict]:
        return self._poll_response(request_id=request_id, model=model)

    poll_x_response.__doc__ = "\n".join(
        (
            f"Fetches the results of a previous {model.value} request to the ScienceIO API.",
            "",
            "Args:",
            f"    request_id (str): The id for the request, as returned by `submit_{model_ident}_request`.",
            "",
            "Returns:",
            f"    Optional[dict]: The output of the {model.value} API call with the given input text, if the request is completed. Otherwise, `None`.",
        )
    )

    return {
        f"{model_ident}": x,
        f"submit_{model_ident}_request": submit_x_request,
        f"poll_{model_ident}_response": poll_x_response,
    }


for model in Model:
    pre_baked_methods = _make_pre_baked_methods(model)

    # Actually attach the new methods to the class.
    for name, method in pre_baked_methods.items():
        setattr(ScienceIO, name, method)
