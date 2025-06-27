from pathlib import Path

prompt_path = "service/AI/prompts/"

def load_system_prompt(name: str) -> str:
    with open(f"{prompt_path}/{name}.txt", 'r', encoding='UTF-8') as f:
        return f.read()

class prompts:
    system: str = load_system_prompt('system')

    note: str = ''
    review: str = ''

    @staticmethod
    def load_prompt(name: str) -> str:
        with open(f"{prompt_path}/{name}.txt", 'r', encoding='UTF-8') as f:
            return prompts.system + f.read()
        
prompts.note = prompts.load_prompt('daily_note')
prompts.review = prompts.load_prompt('review')