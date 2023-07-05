import os
import openai
import asyncio
from aiohttp import ClientSession


def get_account_key() -> str:
    with open(os.path.expanduser(f"~/.api/openAIapi"), encoding="utf-8") as file:
        key = file.read().rstrip("\n")
    return key


# openai.organization = "Personal"
openai.api_key = get_account_key()

# print(openai.api_key)


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


async def review_review(input_para: str):
    """Doc string here."""

    openai.api_key = get_account_key()
    chat_completion_response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful, if slightly sardonic, reviewer of film reviews. You're not the biggest fan of pretentiousness, but you are slightly pretentious yourself. Nevertheless, you have a deep-found appreciation for the reviews that you critique. You try to be subtle, and not too wordy. ",
            },
            {
                "role": "user",
                "content": f"""I'm going to give you some film reviews (delimited by < >), and I want you to review them. I'd like your reviews to be as witty as possible. In particular, you're looking out for things that are unnecessarily complicated or pretentious sounding. Your reviews should take the format:
                               [number from 0 to 10 / 10]. [body of your review paragraph]. 
                               To be clear, your only task is to judge how pretentious sounding / posh these reviews are. 
                               Feel free to use examples / quotes from the provided paragraph to supplement your 
                               critique. Do you understand your task? """,
            },
            {
                "role": "assistant",
                "content": """Absolutely! I understand your task. You'd like me to review the film reviews you provide, and I should focus on identifying unnecessary complexity and pretentiousness in the writing. I'll provide my reviews in a witty and entertaining manner, using the format you specified. Please go ahead and share the reviews you'd like me to critique!""",
            },
            {
                "role": "user",
                "content": """Here's your first review:
                              <le cinéma d’hyper-cool français. an immensely satisfying celebration of minimalism and urban slick with such an impressive commitment to iconography, generating icons, that the protagonist is jeopardised because he loves his hat/coat combo that much. even the overriding, shrugging air of doomed futility is cool (see the self-admitting studio artifice of the ending). drops gasp-inducing imagery every 5 minutes and is so cool that it doesn’t care; Melville wants his audience to enjoy themselves, yearning for Paris, while dragging a cigarette, beating a bad guy to the draw and saying “je m’en fous, c’est quoi cinema quand même?”. the crooning, swooning height of 60s euro-pulp.>
            """,
            },
            {
                "role": "assistant",
                "content": "3/10. The epitome of pretentiousness dressed in hyperbole. This review sets out on a mission to impress rather than inform, with its convoluted sentences and gratuitous French phrases. The reviewer seems to believe that the more adjectives and foreign terms they use, the cooler and more sophisticated their analysis becomes. But alas, it's all smoke and mirrors. Buried beneath the layers of self-indulgence, there's little substance to be found. The film may be a celebration of minimalism, but this review is anything but.",
            },
            {
                "role": "user",
                "content": """Excellent answer, I particularly liked the joke about minimalism. Now, how about this one:

                            <I like it when it's fun.>
                    """,
            },
            {
                "role": "assistant",
                "content": """9/10. Brevity at its finest! This review gets straight to the point with an admirably concise statement. "I like it when it's fun." Well, don't we all? There's something refreshing about the straightforwardness of this review, devoid of unnecessary embellishments or attempts at intellectual prowess. It's a sentiment that speaks to our innate desire for enjoyment and entertainment. While the review may lack in depth or specific analysis, it cuts through the noise and reminds us of the simple pleasure that cinema can bring. Kudos to the reviewer for capturing the essence of a joyful cinematic experience with just a few words.""",
            },
            {
                "role": "user",
                "content": f"""Great stuff, now how about this one:
            <{input_para}>""",
            },
        ],
        max_tokens=200,  # how long the response will be
        temperature=0.8,  # more random
    )
    # print(chat_completion_response)
    return chat_completion_response["choices"][0]["message"]["content"]


test = """number of screening walkouts: 4 (including our entire row)
deeply silly, often quite tedious psychosexual vortex/Freudian soup. an indulgent essay in neurotic turbo-emasculation with a chucklesome pay-off.
masters the art of squirming cope humour - an all-timer shared cinema experience of uncomfortable laughter and bemused croaks; all self-consciousness dropped after about halfway
“professor marvellous: final exam”"""


async def main(input_para: str):
    openai.aiosession.set(ClientSession())
    review_of_review = await review_review(input_para)
    print(review_of_review)
    await openai.aiosession.get().close()


asyncio.run(main(test))
