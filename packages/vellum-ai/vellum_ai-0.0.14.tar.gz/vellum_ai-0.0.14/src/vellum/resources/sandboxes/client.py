# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

import httpx
import pydantic

from ...core.api_error import ApiError
from ...core.jsonable_encoder import jsonable_encoder
from ...core.remove_none_from_headers import remove_none_from_headers
from ...environment import VellumEnvironment
from ...types.sandbox_metric_input_params_request import SandboxMetricInputParamsRequest
from ...types.sandbox_scenario import SandboxScenario
from ...types.scenario_input_request import ScenarioInputRequest

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class SandboxesClient:
    def __init__(self, *, environment: VellumEnvironment = VellumEnvironment.PRODUCTION, api_key: str):
        self._environment = environment
        self.api_key = api_key

    def upsert_sandbox_scenario(
        self,
        id: str,
        *,
        label: typing.Optional[str] = OMIT,
        inputs: typing.List[ScenarioInputRequest],
        scenario_id: typing.Optional[str] = OMIT,
        metric_input_params: typing.Optional[SandboxMetricInputParamsRequest] = OMIT,
    ) -> SandboxScenario:
        _request: typing.Dict[str, typing.Any] = {"inputs": inputs}
        if label is not OMIT:
            _request["label"] = label
        if scenario_id is not OMIT:
            _request["scenario_id"] = scenario_id
        if metric_input_params is not OMIT:
            _request["metric_input_params"] = metric_input_params
        _response = httpx.request(
            "POST",
            urllib.parse.urljoin(f"{self._environment.default}/", f"v1/sandboxes/{id}/scenarios"),
            json=jsonable_encoder(_request),
            headers=remove_none_from_headers({"X_API_KEY": self.api_key}),
            timeout=None,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(SandboxScenario, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncSandboxesClient:
    def __init__(self, *, environment: VellumEnvironment = VellumEnvironment.PRODUCTION, api_key: str):
        self._environment = environment
        self.api_key = api_key

    async def upsert_sandbox_scenario(
        self,
        id: str,
        *,
        label: typing.Optional[str] = OMIT,
        inputs: typing.List[ScenarioInputRequest],
        scenario_id: typing.Optional[str] = OMIT,
        metric_input_params: typing.Optional[SandboxMetricInputParamsRequest] = OMIT,
    ) -> SandboxScenario:
        _request: typing.Dict[str, typing.Any] = {"inputs": inputs}
        if label is not OMIT:
            _request["label"] = label
        if scenario_id is not OMIT:
            _request["scenario_id"] = scenario_id
        if metric_input_params is not OMIT:
            _request["metric_input_params"] = metric_input_params
        async with httpx.AsyncClient() as _client:
            _response = await _client.request(
                "POST",
                urllib.parse.urljoin(f"{self._environment.default}/", f"v1/sandboxes/{id}/scenarios"),
                json=jsonable_encoder(_request),
                headers=remove_none_from_headers({"X_API_KEY": self.api_key}),
                timeout=None,
            )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(SandboxScenario, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
