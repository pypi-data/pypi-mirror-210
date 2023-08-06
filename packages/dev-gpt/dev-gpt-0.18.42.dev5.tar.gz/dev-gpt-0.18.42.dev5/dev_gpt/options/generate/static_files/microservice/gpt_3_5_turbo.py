import os
import openai


openai.api_key = os.getenv("OPENAI_API_KEY")


class GPT_3_5_Turbo:
    def __init__(self, system_string: str = ''):
        self.system = system_string

    def __call__(self, prompt_string: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": 'system',
                "content": self.system
            }, {
                "role": 'user',
                "content": prompt_string
            }]
        )
        return response.choices[0]['message']['content']

