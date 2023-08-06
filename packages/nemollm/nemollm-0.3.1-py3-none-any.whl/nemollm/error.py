class ApiKeyNotSetError(Exception):
    pass


class NemoLLMError(Exception):

    SOLUTION = ''

    def __init__(self, status_code, reason, decoded_content):
        self.message = f"""Request failed with HTTP Status Code {status_code} {reason} **Solution**: {self.SOLUTION} **Full response**: {decoded_content}"""
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ServerSideError(NemoLLMError):
    SOLUTION = "Server is unable to handle your request right now. Please retry your request after a brief wait. If this problem persist, please contact NeMo LLM team"


class ClientSideError(NemoLLMError):
    pass


class IncorrectParamsError(ClientSideError):
    SOLUTION = "Please update the parameters of your request based on the message"


class ModelOrCustomizationNotFoundError(ClientSideError):
    SOLUTION = "Please check that the model and/or Customization ID are valid. To get the list of available models, run 'nemollm list_models' and use the name of a model. For customizations, either go to https://llm.ngc.nvidia.com/custom-models or run 'nemollm list_customizations'"


class AuthorizationError(ClientSideError):
    SOLUTION = (
        "Please check that you are authorized to use the service/model with the correct NGC API KEY and access rights"
    )


class TooManyRequestsError(ClientSideError):
    SOLUTION = "Please reduce the rate that you are sending requests or ask for a rate limit increase"
