import copy
import logging
import os
import sys
import threading
import warnings
from concurrent.futures import as_completed
from pathlib import Path
from typing import List, Optional

if sys.version_info.minor < 8:
    from typing_extensions import Literal
else:
    from typing import Literal

import requests
from requests_futures.sessions import FuturesSession
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm

from nemollm.error import (
    ApiKeyNotSetError,
    AuthorizationError,
    ClientSideError,
    IncorrectParamsError,
    ModelOrCustomizationNotFoundError,
    ServerSideError,
    TooManyRequestsError,
)
from nemollm.version import __version__

MAX_CONNECTION_RETRIES = 3
REQUESTS_TIMEOUT_SECS = 600

# used by generate_future and generate_multiple only
MAX_CONCURRENT_HTTP_REQUESTS = 3

# make sure all sessions on single thread to minimize TCP reconnections
_thread_context = threading.local()


def create_session():
    """
    Create session so that TCP connection does not reset, reducing handshake latency
    """
    session = requests.Session()
    session.mount(
        "https://", requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES),
    )
    return session


def create_generate_future_session():
    """
    Generate needs to be called with multiple concurrent request, hence create new session for generate_future 
    """
    session = requests.Session()
    session.mount(
        "https://", requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES),
    )
    future_session = FuturesSession(session=session, max_workers=MAX_CONCURRENT_HTTP_REQUESTS)
    return future_session


class NemoLLM:
    """
    Make calls to NemoLLM API server using a wrapper around requests library
    """

    def __init__(self, api_key=None, org_id=None, api_host=None):
        self.api_key = api_key if api_key is not None else os.getenv('NGC_API_KEY')
        if not self.api_key:
            raise ApiKeyNotSetError(
                "API KEY is not set. Please pass api_key when instantiating NemoLLM or do 'export NGC_API_KEY=<your_ngc_api_key>'"
            )

        self.org_id = org_id if org_id is not None else os.getenv('NGC_ORG_ID')
        if not self.org_id:
            warnings.warn(
                "ORG ID is not set. Organization id is required if you are in multiple LLM enabled organizations. org_id can be set when instantiating NemoLLM or set with environment variable 'export NGC_ORG_ID=<your_ngc_org_id>'"
            )

        self.api_host = api_host if api_host is not None else "https://api.llm.ngc.nvidia.com/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}", 'User-Agent': f'python-client:{__version__}'}
        if self.org_id:
            self.headers["Organization-ID"] = self.org_id

    @staticmethod
    def handle_response(response, stream=False):
        status_code = response.status_code

        is_binary_content = (
            'content-disposition' in response.headers
            and response.headers['content-disposition'].startswith('attachment')
            or response.headers.get('content-type') == 'application/octet-stream'
        )
        # only set streaming content when success, else raise error to users
        if stream and status_code < 400:
            decoded_content = 'Streaming content'
        elif is_binary_content:
            decoded_content = 'Binary content'
        else:
            decoded_content = response.content.decode()
        # successful
        if status_code < 400:

            logging.info(
                f"Request succeeded with HTTP Status Code {status_code} {response.reason} Full response: {decoded_content}"
            )

        # client_side errors
        elif status_code < 500:
            if status_code == 400:
                raise IncorrectParamsError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code in [401, 403]:
                raise AuthorizationError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code == 404:
                raise ModelOrCustomizationNotFoundError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code == 429:
                raise TooManyRequestsError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            else:
                raise ClientSideError(status_code=status_code, reason=response.reason, decoded_content=decoded_content)

        # server side errors
        else:
            raise ServerSideError(status_code=status_code, reason=response.reason, decoded_content=decoded_content)

    def list_models(self):
        url = f"{self.api_host}/models"

        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()

        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def create_customization(
        self,
        model: str,
        training_dataset_file_id: str,
        name: str,
        validation_dataset_file_id: Optional[str] = None,
        batch_size: Optional[int] = None,
        epochs: Optional[int] = None,
        learning_rate: Optional[float] = None,
        num_virtual_tokens: Optional[int] = None,
    ):
        url = f"{self.api_host}/models/{model}/customizations"

        data = {"name": name, "training_dataset_file_id": training_dataset_file_id}

        # do not set explicit default params for training,
        # instead, set param only when set by user, otherwise depending on API defaults
        # this reduces need to sync with API when API defaults change
        if validation_dataset_file_id is not None:
            data["validation_dataset_file_id"] = validation_dataset_file_id
        if batch_size is not None:
            data["batch_size"] = batch_size
        if epochs is not None:
            data["epochs"] = epochs
        if epochs is not None:
            data["learning_rate"] = learning_rate
        if num_virtual_tokens is not None:
            data["additional_hyperparameters"] = {}
            data["additional_hyperparameters"]["num_virtual_tokens"] = num_virtual_tokens

        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.post(url, headers=self.headers, json=data, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def generate(
        self,
        model: str,
        prompt: str,
        customization_id: str = None,
        return_type: Literal['json', 'text', 'stream', 'future', 'async'] = 'json',
        tokens_to_generate: Optional[int] = None,
        logprobs: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        beam_search_diversity_rate: Optional[float] = None,
        beam_width: Optional[int] = None,
        length_penalty: Optional[float] = None,
        disable_logging: bool = False,
    ):
        """
        Beyond API configurations, 
        
        Allow users to choose the type of response they would want using return_type

        1. json: JSON representation of the API response content
        2. text: STR using only the 'text' field of the API response json
        3. stream: ITER of lines with each line being of json structure containing one token that can be used with json.loads(line) 
        4. future: FUTURE object based on https://github.com/ross/requests-futures and concurrent.futures.Future. To get json response, use future.result()
        5. async: alias to future

        """
        if customization_id is None:
            url = f"{self.api_host}/models/{model}/completions"
        else:
            url = f"{self.api_host}/models/{model}/customizations/{customization_id}/completions"

        data = {"prompt": prompt}

        # do not set explicit default params for training,
        # instead, set param only when set by user, otherwise depending on API defaults
        # this reduces need to sync with API when API defaults change

        if tokens_to_generate is not None:
            data["tokens_to_generate"] = tokens_to_generate
        if logprobs is not None:
            data["logprobs"] = logprobs
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if top_k is not None:
            data["top_k"] = top_k
        if stop is not None:
            data["stop"] = stop
        if random_seed is not None:
            data["random_seed"] = random_seed
        if repetition_penalty is not None:
            data["repetition_penalty"] = repetition_penalty
        if beam_search_diversity_rate is not None:
            data["beam_search_diversity_rate"] = beam_search_diversity_rate
        if beam_width is not None:
            data["beam_width"] = beam_width
        if length_penalty is not None:
            data["length_penalty"] = length_penalty

        if return_type not in ['async', 'future'] and not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()

        if return_type in ['async', 'future'] and not hasattr(_thread_context, 'generate_future_session'):
            _thread_context.generate_future_session = create_generate_future_session()

        headers = copy.copy(self.headers)
        if disable_logging:
            headers["x-disable-logging"] = 'true'
        if return_type == 'stream':
            headers["x-stream"] = 'true'

        if return_type in ['async', 'future']:
            response = _thread_context.generate_future_session.post(
                url, headers=headers, json=data, timeout=REQUESTS_TIMEOUT_SECS
            )
        else:
            response = _thread_context.session.post(
                url, headers=headers, json=data, timeout=REQUESTS_TIMEOUT_SECS, stream=(return_type == 'stream')
            )

        if return_type == 'stream':
            NemoLLM.handle_response(response, stream=True)
            return response.iter_lines()
        elif return_type in ['async', 'future']:
            return response
        elif return_type == 'text':
            NemoLLM.handle_response(response)
            return NemoLLM.post_process_generate_response(response, True)
        else:
            NemoLLM.handle_response(response)
            return NemoLLM.post_process_generate_response(response, False)

    @staticmethod
    def post_process_generate_response(response, return_text_completion_only):
        if response.ok:
            response_json = response.json()
        else:
            response_json = {"status": "fail", "msg": str(response.content.decode())}

        if return_text_completion_only:
            return response_json['text'] if 'text' in response_json else ''
        return response_json

    def generate_multiple(
        self,
        model: str,
        prompts: List[str],
        customization_id: str = None,
        return_type: Literal['json', 'text'] = 'json',
        tokens_to_generate: Optional[bool] = None,
        logprobs: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        beam_search_diversity_rate: Optional[float] = None,
        beam_width: Optional[int] = None,
        length_penalty: Optional[int] = None,
        disable_logging: bool = False,
    ):
        futures = []
        for i, prompt in enumerate(prompts):
            future = self.generate(
                model,
                prompt,
                return_type='future',
                customization_id=customization_id,
                tokens_to_generate=tokens_to_generate,
                logprobs=logprobs,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop=stop,
                random_seed=random_seed,
                repetition_penalty=repetition_penalty,
                beam_search_diversity_rate=beam_search_diversity_rate,
                beam_width=beam_width,
                length_penalty=length_penalty,
                disable_logging=disable_logging,
            )
            # ensure order of responses follows order of prompts
            future.i = i
            futures.append(future)

        responses_json = [None] * len(prompts)
        for future in as_completed(futures):
            response = future.result()
            NemoLLM.handle_response(response)
            responses_json[future.i] = NemoLLM.post_process_generate_response(response, return_type == "text")
        return responses_json

    def upload(self, filepath, progress_bar: bool = False):
        """
        Allows monitoring of upload progress via tqdm for large files

        Requires requests toolbelt
        """
        url = f"{self.api_host}/files"

        path = Path(filepath)
        total_size = path.stat().st_size
        filename = path.name
        fields = {}

        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()

        with tqdm(
            desc=filename, total=total_size, unit="B", unit_scale=True, unit_divisor=1024, disable=not progress_bar
        ) as bar:
            with open(filepath, "rb") as f:
                fields["file"] = (filepath, f)
                fields["format"] = "jsonl"
                e = MultipartEncoder(fields=fields)
                m = MultipartEncoderMonitor(e, lambda monitor: bar.update(monitor.bytes_read - bar.n))
                headers = copy.copy(self.headers)
                headers["Content-Type"] = m.content_type
                response = _thread_context.session.post(url, data=m, headers=headers, timeout=REQUESTS_TIMEOUT_SECS)
                NemoLLM.handle_response(response)
        return response.json()

    def list_customizations(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        shared: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
    ):
        url = f"{self.api_host}/customizations"

        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()

        params = {}

        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if shared is not None:
            params["shared"] = shared
        if sort_by is not None:
            params["sort_by"] = sort_by
        if order is not None:
            params["order"] = order
        response = _thread_context.session.get(url, headers=self.headers, params=params, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def list_files(self):
        url = f"{self.api_host}/files"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def delete_file(self, file_id):
        url = f"{self.api_host}/files/{file_id}"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.delete(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return f"File {file_id} has{'' if response.ok else ' not'} been deleted"

    def get_info_customization(self, model, customization_id):
        url = f"{self.api_host}/models/{model}/customizations/{customization_id}"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def delete_customization(self, model, customization_id):
        url = f"{self.api_host}/models/{model}/customizations/{customization_id}"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.delete(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return f"Customization {customization_id} for model {model} has{'' if response.ok else ' not'} been deleted"

    def download_customization(self, model, customization_id, save_filename):
        url = f"{self.api_host}/models/{model}/customizations/{customization_id}/fetch"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)

        NemoLLM.handle_response(response)

        if os.path.dirname(save_filename):
            os.makedirs(os.path.dirname(save_filename), exist_ok=True)
        with open(save_filename, "wb") as fw:
            fw.write(response.content)
        return f"Customization {customization_id} for model {model} has{'' if response.ok else ' not'} been saved at {save_filename}"

    def get_info_file(self, file_id):
        url = f"{self.api_host}/files/{file_id}"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()

    def get_customization_training_metrics(self, model, customization_id):
        url = f"https://api.llm.ngc.nvidia.com/v1/models/{model}/customizations/{customization_id}/metrics"
        if not hasattr(_thread_context, 'session'):
            _thread_context.session = create_session()
        response = _thread_context.session.get(url, headers=self.headers, timeout=REQUESTS_TIMEOUT_SECS)
        NemoLLM.handle_response(response)
        return response.json()


class Connection(NemoLLM):
    def __init__(self, access_token=None, host=None):
        warnings.warn(
            f'{self.__class__.__name__} will be deprecated in version 0.4.0. Please use NemoLLM instead',
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(api_key=access_token, api_host=host)

    def generate_completion(
        self,
        model_id: str,
        prompt: str,
        tokens_to_generate: Optional[bool] = None,
        logprobs: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        beam_search_diversity_rate: Optional[float] = None,
        beam_width: Optional[int] = None,
        length_penalty: Optional[int] = None,
    ):
        warnings.warn(
            'This method will be deprecated in version 0.4.0. Please use NemoLLM().generate instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.generate(
            model=model_id,
            prompt=prompt,
            tokens_to_generate=tokens_to_generate,
            logprobs=logprobs,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            random_seed=random_seed,
            repetition_penalty=repetition_penalty,
            beam_search_diversity_rate=beam_search_diversity_rate,
            beam_width=beam_width,
            length_penalty=length_penalty,
        )

    def generate_customization_completion(
        self,
        model_id: str,
        prompt: str,
        customization_id: str = None,
        tokens_to_generate: Optional[bool] = None,
        logprobs: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        beam_search_diversity_rate: Optional[float] = None,
        beam_width: Optional[int] = None,
        length_penalty: Optional[int] = None,
    ):
        warnings.warn(
            'This method will be deprecated in version 0.4.0. Please use NemoLLM().generate instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.generate(
            model=model_id,
            prompt=prompt,
            customization_id=customization_id,
            tokens_to_generate=tokens_to_generate,
            logprobs=logprobs,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            random_seed=random_seed,
            repetition_penalty=repetition_penalty,
            beam_search_diversity_rate=beam_search_diversity_rate,
            beam_width=beam_width,
            length_penalty=length_penalty,
        )
