import asyncio
import httpx
import platform
import json # For logging bodies, Pydantic handles main ser/de
from typing import Optional, Callable, Awaitable, TypeVar, Dict, Any, Union, Type, cast, List
import logging

from pydantic import BaseModel, ValidationError, HttpUrl

from .types import HttpOpts # HttpOpts is now a Pydantic model
from .errors import (
    GranolaAPIError, GranolaAuthError, GranolaRateLimitError,
    GranolaTimeoutError, GranolaValidationError
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel) # Response model type
P = TypeVar('P', bound=BaseModel) # Payload model type

class HttpClient:
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Union[str, HttpUrl] = "https://api.granola.ai", # Default from ClientOpts
        opts: Optional[HttpOpts] = None, # HttpOpts is Pydantic model
    ):
        # If opts is None, create a default HttpOpts instance
        # If opts is a dict, Pydantic will parse it
        parsed_opts = HttpOpts.model_validate(opts if opts is not None else {})

        self._token: Optional[str] = token
        self.base_url_str: str = str(base_url).rstrip("/") # base_url from ClientOpts is HttpUrl
        self.timeout_ms: int = cast(int, parsed_opts.timeout)
        self.retries: int = cast(int, parsed_opts.retries)

        self.app_version: str = cast(str, parsed_opts.app_version)
        self.client_type: str = cast(str, parsed_opts.client_type)

        self.client_platform: str = parsed_opts.client_platform or platform.system().lower()
        self.client_architecture: str = parsed_opts.client_architecture or platform.machine().lower()
        self.electron_version: str = cast(str, parsed_opts.electron_version)
        self.chrome_version: str = cast(str, parsed_opts.chrome_version)
        self.node_version: str = cast(str, parsed_opts.node_version)

        os_ver = platform.release()
        if self.client_platform == "darwin":
            os_ver = platform.mac_ver()[0]
        elif self.client_platform == "win32": # platform.system() returns 'Windows'
            self.client_platform = "windows" # align with common usage
            os_ver = platform.win32_ver()[0]

        self.os_version: str = parsed_opts.os_version or os_ver
        self.os_build: str = parsed_opts.os_build or "" # Still hard to get reliably

        self.client_headers: Dict[str, str] = cast(Dict[str,str], parsed_opts.client_headers)

        self._token_provider: Optional[Callable[[], Awaitable[str]]] = None
        self._token_fetch_lock = asyncio.Lock()

        self._client: httpx.AsyncClient = httpx.AsyncClient(timeout=self.timeout_ms / 1000.0)

    def set_token(self, token: str) -> None:
        self._token = token

    def set_token_provider(self, provider: Callable[[], Awaitable[str]]) -> None:
        self._token_provider = provider

    async def _ensure_token(self) -> None:
        if self._token:
            return
        if not self._token_provider:
            logger.warning("No API token set and no token provider configured.")
            return

        async with self._token_fetch_lock:
            if self._token: return
            try:
                logger.info("Fetching API token using provider.")
                self._token = await self._token_provider()
                if not self._token:
                    raise GranolaAuthError("Token provider returned an empty token.")
                logger.info("API token successfully fetched and set.")
            except Exception as e:
                logger.error(f"Error fetching token via provider: {e}", exc_info=True)
                raise GranolaAuthError(f"Failed to retrieve authentication token via provider: {e}") from e

    def _get_backoff_delay(self, attempt: int, retry_after_header: Optional[str] = None) -> float:
        if retry_after_header:
            try: return float(retry_after_header)
            except ValueError: pass
        return 0.25 * (2 ** attempt)

    async def _request_raw(
        self, method: str, path: str, body_data: Optional[Union[Dict[str, Any], List[Any], str]] = None
    ) -> httpx.Response:
        await self._ensure_token()
        url = f"{self.base_url_str}{path}"

        headers: Dict[str, str] = {
            "X-App-Version": self.app_version,
            "User-Agent": f"Granola/{self.app_version} Electron/{self.electron_version} Chrome/{self.chrome_version} Node/{self.node_version} ({self.client_platform} {self.os_version}; {self.os_build})".strip(),
            "X-Client-Type": self.client_type,
            "X-Client-Platform": self.client_platform,
            "X-Client-Architecture": self.client_architecture,
            "X-Client-Id": f"granola-{self.client_type}-{self.app_version}",
            **self.client_headers,
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        is_json_body = isinstance(body_data, (dict, list))
        if is_json_body:
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json" # Usually expect JSON back for JSON posts
        elif isinstance(body_data, str): # Assuming raw text body
            headers["Content-Type"] = "text/plain" # Or other appropriate type
            # Accept might still be JSON or text depending on endpoint
        else: # No body
             headers["Accept"] = "application/json" # Default accept for GET or bodiless POST

        last_error: Optional[Exception] = None

        for attempt in range(self.retries + 1):
            try:
                logger.debug(f"Request: {method} {url}, Attempt: {attempt + 1}/{self.retries + 1}")
                if body_data: logger.debug(f"Request Body: {json.dumps(body_data) if is_json_body else str(body_data)[:200]}")

                res = await self._client.request(
                    method, url,
                    content=json.dumps(body_data) if is_json_body else body_data, # Use content for bytes/str, json for dict/list
                    headers=headers,
                )

                logger.debug(f"Response: {res.status_code}, Headers: {res.headers}")

                if res.status_code == 429:
                    retry_after = res.headers.get("Retry-After")
                    delay = self._get_backoff_delay(attempt, retry_after)
                    err_text = await res.atext()
                    last_error = GranolaRateLimitError(
                        f"Rate limited. Retry after {retry_after or f'{delay}s'}.",
                        status_code=res.status_code, response_text=err_text,
                        retry_after=int(delay) if retry_after else None
                    )
                    if attempt < self.retries:
                        logger.warning(f"Rate limited. Retrying in {delay:.2f} seconds...")
                        await asyncio.sleep(delay); continue
                    raise last_error

                res.raise_for_status()
                return res

            except httpx.TimeoutException as e:
                last_error = GranolaTimeoutError(f"Request to {url} timed out after {self.timeout_ms}ms.")
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}. Error: {e}")
                if attempt < self.retries: await asyncio.sleep(self._get_backoff_delay(attempt)); continue
                raise last_error
            except httpx.HTTPStatusError as e:
                err_text = e.response.text
                logger.error(f"HTTP Error: {e.response.status_code} for {url}. Response: {err_text}. Error: {e}")
                if e.response.status_code >= 500 and attempt < self.retries:
                    delay = self._get_backoff_delay(attempt, e.response.headers.get("Retry-After"))
                    logger.warning(f"Server error {e.response.status_code}. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay); continue
                last_error = GranolaAPIError(
                    f"HTTP {e.response.status_code}: {err_text}",
                    status_code=e.response.status_code, response_text=err_text
                )
                raise last_error
            except httpx.RequestError as e:
                last_error = GranolaAPIError(f"Request failed: {e}")
                logger.warning(f"Request error on attempt {attempt + 1} for {url}. Error: {e}")
                if attempt < self.retries: await asyncio.sleep(self._get_backoff_delay(attempt)); continue
                raise last_error
            except Exception as e:
                last_error = GranolaAPIError(f"An unexpected error occurred: {e}")
                logger.error(f"Unexpected error: {e}", exc_info=True); raise last_error

        assert last_error is not None
        raise last_error

    async def _request_model(
        self, method: str, path: str,
        response_model: Type[T],
        payload_model: Optional[P] = None, # Pydantic model for request body
        payload_dict: Optional[Dict[str, Any]] = None # Raw dict for request body
    ) -> T:
        body_to_send: Optional[Dict[str, Any]] = None
        if payload_model:
            body_to_send = payload_model.model_dump(by_alias=True, exclude_none=True)
        elif payload_dict:
            body_to_send = payload_dict

        response = await self._request_raw(method, path, body_data=body_to_send)

        try:
            # Ensure we read the content before trying to parse, especially if streamed.
            # For httpx, .json() handles this.
            # We use model_validate_json for Pydantic.
            response_content = await response.aread() # Read content bytes
            if not response_content: # Handle empty response if model allows (e.g. Optional fields)
                # This case is tricky. If response_model expects data, empty content is an error.
                # If response_model can be valid with all defaults / Optionals, it might pass.
                # Pydantic will raise ValidationError if required fields are missing.
                logger.warning(f"Empty response content received for {method} {path}")

            return response_model.model_validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(response.encoding or 'utf-8', errors='replace') if response_content else "(empty response)"
            logger.error(f"Pydantic validation error for {method} {path}. Errors: {e.errors()}. Response: {err_text[:500]}")
            raise GranolaValidationError(str(e), validation_errors=e.errors(), response_text=err_text) from e
        except json.JSONDecodeError as e: # If response is not even JSON
            err_text = response_content.decode(response.encoding or 'utf-8', errors='replace') if response_content else "(empty response)"
            logger.error(f"JSON decode error for {method} {path}. Error: {e}. Response: {err_text[:500]}")
            raise GranolaAPIError(f"Failed to decode JSON response: {e.msg}", response_text=err_text)

    async def _request_void(
        self, method: str, path: str,
        payload_model: Optional[P] = None,
        payload_dict: Optional[Dict[str, Any]] = None
    ) -> None:
        body_to_send: Optional[Dict[str, Any]] = None
        if payload_model:
            body_to_send = payload_model.model_dump(by_alias=True, exclude_none=True)
        elif payload_dict:
            body_to_send = payload_dict

        response = await self._request_raw(method, path, body_data=body_to_send)
        # For void methods, we typically expect 204 No Content or 200/201 with empty/ignorable body.
        # raise_for_status() in _request_raw already checks for >=400 errors.
        # We might want to consume the response body to free resources, though httpx might do this.
        await response.aread()
        return None

    async def get_text(self, path: str) -> str:
        response = await self._request_raw("GET", path)
        return await response.aread().then(lambda b: b.decode(response.encoding or 'utf-8'))


    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
