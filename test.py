import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

if __name__ == '__main__':
    question = input('enter your question:')
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    choices = response['choices']
    first_item = choices[0]
    answer: str = first_item['text']
    print('> ', answer.strip())