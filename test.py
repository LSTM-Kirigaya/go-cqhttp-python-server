from qq_server.util import write_yaml, read_yaml


obj = {
    'name': '达瓦哒哒哒',
    'path': './adwada',
    'objs' : [
        {'a': '啊伟大巫毒娃娃的', 'b': '啊伟大巫毒娃娃的'},
        {'a': '啊伟大巫毒娃娃的', 'b': '啊伟大巫毒娃娃的'},
        {'a': '啊伟大巫毒娃娃的', 'b': '啊伟大巫毒娃娃的'},
        {'a': '啊伟大巫毒娃娃的', 'b': '啊伟大巫毒娃娃的'}
    ]
}

print(read_yaml('./test.yml'))

write_yaml('./test.yml', obj)