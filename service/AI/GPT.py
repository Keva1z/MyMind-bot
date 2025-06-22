from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, Free2GPT, FreeGpt, LegacyLMArena

from service.AI.prompts.prompt import prompts

client = AsyncClient(provider=RetryProvider([Free2GPT, FreeGpt, LegacyLMArena], shuffle=False))
model = "gemini-1.5-flash"


async def generate(prompt: str):
    response = await client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": prompts.system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


