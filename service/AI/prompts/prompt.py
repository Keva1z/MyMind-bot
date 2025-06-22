from pathlib import Path

prompt_path = "service/AI/prompts/"

def load_prompt(name: str) -> str:
    with open(f"{prompt_path}/{name}.txt", 'r', encoding='UTF-8') as f:
        return f.read()

class prompts:
    note: str = load_prompt('daily_note')
    review: str = load_prompt('review')
    system: str = load_prompt('system')