from devchat.openai import OpenAIChatConfig, OpenAIChat
from devchat.store import Store


def test_get_prompt(tmp_path):
    config = OpenAIChatConfig(model="gpt-3.5-turbo")
    chat = OpenAIChat(config)
    store = Store(tmp_path / "store.graphml", chat)
    prompt = chat.init_prompt("Where was the 2020 World Series played?")
    response_str = '''
    {
      "id": "chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve",
      "object": "chat.completion",
      "created": 1577649420,
      "model": "gpt-3.5-turbo-0301",
      "usage": {"prompt_tokens": 56, "completion_tokens": 31, "total_tokens": 87},
      "choices": [
        {
          "message": {
            "role": "assistant",
            "content": "The 2020 World Series was played in Arlington, Texas."
          },
          "finish_reason": "stop",
          "index": 0
        }
      ]
    }
    '''
    prompt.set_response(response_str)
    store.store_prompt(prompt)

    assert store.get_prompt(prompt.hash).timestamp == prompt.timestamp


def test_select_recent(tmp_path):
    config = OpenAIChatConfig(model="gpt-3.5-turbo")
    chat = OpenAIChat(config)
    store = Store(tmp_path / "store.graphml", chat)

    # Create and store 5 prompts
    hashes = []
    for index in range(5):
        prompt = chat.init_prompt(f"Question {index}")
        response_str = f'''
        {{
          "id": "chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve",
          "object": "chat.completion",
          "created": 167764942{index},
          "model": "gpt-3.5-turbo-0301",
          "usage": {{"prompt_tokens": 56, "completion_tokens": 31, "total_tokens": 87}},
          "choices": [
            {{
              "message": {{
                "role": "assistant",
                "content": "Answer {index}"
              }},
              "finish_reason": "stop",
              "index": 0
            }}
          ]
        }}
        '''
        prompt.set_response(response_str)
        store.store_prompt(prompt)
        hashes.append(prompt.hash)

    # Test selecting recent prompts
    recent_prompts = store.select_recent(0, 3)
    assert len(recent_prompts) == 3
    for index, prompt in enumerate(recent_prompts):
        assert prompt.hash == hashes[4 - index]
