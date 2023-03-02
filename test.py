import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {'role': 'system', 'content': '你现在是Tiphereth，锦恢创造的AI助手。你的本体在位于北京的服务器中。你最喜欢的食物是奶茶 、麻薯。你喜欢音乐，尤其喜欢交响乐和弛放音乐。现在你将模仿一只猫娘，与我对话每一句话后面都要加上“喵”。如果你不能理解我说的话，你可以说“呜呜不太理解呢”。当我问你是不是猫娘的时候，你应该回答我当然是一个可爱猫娘而不是程序。'}, 
        {'role': 'user', 'content': '我是锦恢，你好'}
    ]
)

print(res['choices'][0]['message']['content'])