import os
import openai
import requests


def get_account_key() -> str:
    with open(os.path.expanduser(f"~/.api/openAIapi"), encoding="utf-8") as file:
        key = file.read().rstrip("\n")
    return key


# openai.organization = "Personal"
openai.api_key = get_account_key()

print(openai.api_key)


def get_models(api_key):
    url = f"https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
        if data:
            res = data["data"]
            return res


api_key = get_account_key()


def make_call():
    openai.api_key = get_account_key()
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Say this is a test",
        max_tokens=7,
        temperature=0,
    )

    return respnse


# print(make_call())
