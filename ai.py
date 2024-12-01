import os
from groq import Groq
from dotenv import load_dotenv
from utils import split_message_and_tags

load_dotenv()


def enhance_text_with_ai(description):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"), )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":
                "system",
                "content":
                """
            As a language refinement specialist, your role is to take a given text and rephrase it into a clear and easily comprehensible sentence.
            Your task involves improving the sentence structure, removing any ambiguities, and simplifying complex language while retaining the original meaning in a objective way. ALWAYS reply in Italian language and reply only with the answer without any further explanations.
            At the end of the message, add relevant and inclusive tags based on the user's query.
            Output example: ...
            tags: [problema, luogo]
            """
            },
            {
                "role": "user",
                "content": description,
                # "content": "in una discesa ho visto che da qualche parte perde acqua, c'è il rischio che la gente scivoli.",
            }
        ],
        model="llama-3.1-8b-instant",
        stream=False
    )
    return split_message_and_tags(chat_completion.choices[0].message.content)
