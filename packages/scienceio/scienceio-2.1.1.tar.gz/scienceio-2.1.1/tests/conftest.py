import enum
import pytest
import requests_mock

from typing import NamedTuple

from src.scienceio import Model, ScienceIO

STRUCTURE_INPUT_TEXT = (
    "The COVID-19 pandemic has shown a markedly low proportion of cases among "
    "children 1-4. Age disparities in observed cases could be explained by "
    "children having lower susceptibility to infection, lower propensity to "
    "show clinical symptoms or both."
)
PHI_INPUT_TEXT = (
    "Romeo Santos made an appointment with Dr. Geoffrey Royce on December 21, "
    "2020. Mr. Santos was complaining of symptoms of alcohol overdose, and "
    "showed signs of possible Capgras delusion."
)


class ModelTestCase(NamedTuple):
    model: Model
    input_text: str


MODEL_TEST_CASES = tuple(
    ModelTestCase(
        model=m,
        input_text=STRUCTURE_INPUT_TEXT if m is Model.STRUCTURE else PHI_INPUT_TEXT,
    )
    for m in Model
)

MODEL_TEST_CASE_IDS = tuple(mtc.model.name.lower() for mtc in MODEL_TEST_CASES)

DUMMY_REQUEST_ID = "DUMMY_REQUEST_ID"


class HttpCall(enum.Enum):
    SUBMIT = enum.auto()
    POLL = enum.auto()


class ErrorTestCase(NamedTuple):
    test_case_id_stub: str
    http_call: HttpCall
    status_code: int
    json_payload: dict

    @property
    def test_case_id(self) -> str:
        return f"{self.test_case_id_stub}_{self.http_call.name.lower()}"

    def patch_requests_mocker(
        self, requests_mocker: requests_mock.Mocker, api_url: str
    ):
        submit_status_code = 200
        submit_json_payload = {
            "request_id": DUMMY_REQUEST_ID,
        }

        poll_status_code = 200
        poll_json_payload = {
            "annotations": [],
        }

        if self.http_call is HttpCall.SUBMIT:
            submit_status_code = self.status_code
            submit_json_payload = self.json_payload
        elif self.http_call is HttpCall.POLL:
            poll_status_code = self.status_code
            poll_json_payload = self.json_payload

        requests_mocker.register_uri(
            "POST",
            f"{api_url}/structure",
            status_code=submit_status_code,
            json=submit_json_payload,
        )

        requests_mocker.register_uri(
            "GET",
            f"{api_url}/structure/{DUMMY_REQUEST_ID}",
            status_code=poll_status_code,
            json=poll_json_payload,
        )


ERROR_TEST_CASES = (
    ErrorTestCase(
        test_case_id_stub="unknown_api_key",
        http_call=HttpCall.SUBMIT,
        status_code=404,
        json_payload={"detail": "API key not found"},
    ),
    ErrorTestCase(
        test_case_id_stub="invalid_api_key_too_short",
        http_call=HttpCall.SUBMIT,
        status_code=400,
        json_payload={
            "detail": {
                "message": "Invalid request",
                "errors": {
                    "api_id": [
                        "ensure this value has at least 20 characters",
                    ],
                },
            },
        },
    ),
    ErrorTestCase(
        test_case_id_stub="invalid_api_secret",
        http_call=HttpCall.SUBMIT,
        status_code=400,
        json_payload={
            "detail": {
                "message": "Invalid request",
                "errors": {
                    "api_secret": ["value is not a valid uuid"],
                },
            },
        },
    ),
    ErrorTestCase(
        test_case_id_stub="lambda_cold_start_timeout",
        http_call=HttpCall.SUBMIT,
        status_code=503,
        json_payload={
            "message": "Service Unavailable",
        },
    ),
    ErrorTestCase(
        test_case_id_stub="expired_request_id",
        http_call=HttpCall.POLL,
        status_code=410,
        json_payload={
            "request_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "inference_result": None,
            "model_type": "structure",
            "inference_status": "EXPIRED",
            "message": "Your inference results have expired. Please submit a new request.",
        },
    ),
    ErrorTestCase(
        test_case_id_stub="unknown_request_id",
        http_call=HttpCall.POLL,
        status_code=404,
        json_payload={
            "detail": "Request id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx not found",
        },
    ),
    ErrorTestCase(
        test_case_id_stub="blocked_api_user",
        http_call=HttpCall.SUBMIT,
        status_code=403,
        json_payload={
            "detail": "Your free trial has ended. Please upgrade your plan by visiting science.io/pricing to proceed",
        },
    ),
)

ERROR_TEST_CASE_IDS = tuple(etc.test_case_id for etc in ERROR_TEST_CASES)


def exclude_floats(*, prop, path) -> bool:
    return isinstance(prop, str) and prop in {"score_id", "score_type"}


@pytest.fixture(scope="session", autouse=True)
def scio():
    yield ScienceIO()
