import os
from pprint import pprint

import openai
from openai.openai_object import OpenAIObject

openai.api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    def print_message(role: str, content: str):
        print(f"{role}: {content}")


    messages = []

    while True:
        content = input("user: ")
        if not content.strip():
            break

        messages.append({"role": "user", "content": content})

        response: OpenAIObject = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        messages.append({"role": response.choices[0].message.role,
                         "content": response.choices[0].message.content})
        print_message(response.choices[0].message.role, response.choices[0].message.content)
