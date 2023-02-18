from qq_server.openai_api import make_openai_completion_request

res = make_openai_completion_request('你好')
print(res)