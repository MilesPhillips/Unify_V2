import os


class LLMConfigurationError(RuntimeError):
    pass


class LLMService:
    def __init__(self) -> None:
        api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUD_API_TOKEN')
        if not api_key:
            raise LLMConfigurationError(
                'LLM is not configured. Set ANTHROPIC_API_KEY in your .env file.'
            )

        try:
            from anthropic import Anthropic
        except ModuleNotFoundError as exc:
            raise LLMConfigurationError(
                'The anthropic package is not installed. Add it to your environment first.'
            ) from exc

        self.client = Anthropic(api_key=api_key)
        self.model = os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-haiku-20241022')
        self.max_tokens = int(os.environ.get('ANTHROPIC_MAX_TOKENS', '512'))
        self.system_prompt = os.environ.get(
            'LLM_SYSTEM_PROMPT',
            (
                'You are Unify, a supportive assistant inside a chat app. '
                'Reply clearly, directly, and briefly unless the user asks for more depth.'
            ),
        )

    def chat(self, history: list[dict[str, str]], message: str) -> str:
        messages = [
            {'role': item['role'], 'content': item['content']}
            for item in history
            if item.get('role') in {'user', 'assistant'} and item.get('content')
        ]
        messages.append({'role': 'user', 'content': message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=messages,
        )

        text_parts: list[str] = []
        for block in response.content:
            text = getattr(block, 'text', None)
            if text:
                text_parts.append(text)

        reply = ''.join(text_parts).strip()
        if not reply:
            raise RuntimeError('The LLM returned an empty response.')

        return reply
