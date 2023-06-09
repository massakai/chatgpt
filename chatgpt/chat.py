import os
from enum import StrEnum
from logging import getLogger, NullHandler
from typing import Generator, Self, Sequence, Type

import openai

logger = getLogger(__name__)
logger.addHandler(NullHandler())

openai.api_key = os.getenv("OPENAI_API_KEY")


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    @classmethod
    def of(cls: Type[Self], value: str) -> Self:
        for role in Role:
            role: Role
            if role.value == value:
                return role
        raise ValueError(f"No such value: {value}")


class Chat:
    def __init__(self,
                 model: str = "gpt-3.5-turbo",
                 system_messages: Sequence[str] | None = None):
        self._model = model
        if system_messages:
            self._messages = [Chat._create_message(Role.SYSTEM, message) for message in system_messages]
        else:
            self._messages = []

    def send(self, content: str, stream: bool = False) -> str | Generator[str, None, None]:
        self._append_message(Role.USER, content)

        response = openai.ChatCompletion.create(
            model=self._model,
            messages=self._messages,
            stream=stream
        )

        if stream:
            return self._send_generator()
        else:
            message = response["choices"][0]["message"]
            self._append_message(Role.of(message["role"]), message["content"])
            return message["content"]

    def _send_generator(self) -> Generator[str, None, None]:
        response = openai.ChatCompletion.create(
            model=self._model,
            messages=self._messages,
            stream=True
        )
        role = None
        chunks = []
        for chunk in response:
            message = chunk["choices"][0]["delta"]
            if 'role' in message:
                role = Role.of(message["role"])
            if "content" in message:
                content = message["content"]
                chunks.append(content)
                yield content
        self._append_message(role, "".join(chunks))

    @staticmethod
    def _create_message(role: Role, content: str):
        return {"role": role.value, "content": content}

    def _append_message(self, role: Role, content: str) -> None:
        self._messages.append(Chat._create_message(role, content))


def main():
    chat = Chat()

    while True:
        content = input("user: ")
        if not content.strip():
            break

        reply = chat.send(content)
        print(f"assistant: {reply}")


if __name__ == "__main__":
    main()
