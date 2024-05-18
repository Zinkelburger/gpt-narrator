# https://platform.openai.com/docs/api-reference
# https://platform.openai.com/docs/api-reference/streaming
# also keep track of everything that has been typed, so
from openai import OpenAI

# openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

# https://platform.openai.com/docs/quickstart
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."},
#     {"role": "assistant", "content": "previously generated promp"}
#   ]
# )

# print(completion.choices[0].message)