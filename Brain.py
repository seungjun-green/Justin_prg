import openai
engine = "text-davinci-002"
from Resources import keys
openai.api_key = keys.ai_key
class Brain:
    def create_response(self, order, stop):
        result = ""
        count = 0
        while True:
            response = openai.Completion.create(
                engine=engine,
                prompt=order,
                temperature=0.5,
                max_tokens=60,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0,
                stop=stop
            )

            count += 1
            result += response['choices'][0]['text']
            order += response['choices'][0]['text']
            if count == 3 or response['choices'][0]['text'] == '':
                break

        return result