from klu.common.errors import BaseKluError


class UnknownModelProviderError(BaseKluError):
    model_provider: int

    def __init__(self, model_provider):
        self.model_provider = model_provider
        self.message = (
            f"An unknown model provider {self.model_provider} was used. "
            "Supported providers are [OpenAI, HuggingFace, NLPCloud, GooseAI, AI21 & Anthropic]"
        )
        super().__init__(self.message)
