class Defaults:
    go_cqhttp_config = './config.yml'
    python_server_config = './server.yml'
    talk_pool_config = {
        'max_length': 10,
        'memory_path': './qq_server_data/memory.yml',
        'save_time_interval': 600
    }
    stop_words = set([',', '.', '，', '。', '?', '!', '？', '！', ':', '：'])
    openai_max_repeat_times = 3
    context_max_length = 300