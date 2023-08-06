import ray
import abc
import logging

class AbstractMind(metaclass=abc.ABCMeta):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def log(self, msg):
        logging.info(msg)

    @abc.abstractmethod
    def ask(self, msg):
        pass

@ray.remote
class SimpleMind(AbstractMind):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def ask(self, msg):
        ret = f'({self.value} {msg})'
        self.log(ret)
        return ret

def call_api(json_data, url):
    import requests
    print('\ncall_api: ', json_data)

    response = requests.post(
        f"{url}/v1/chat/completions",
        json=json_data
    )
    response.raise_for_status()
    completion = response.json()
    #print('completion: ', completion)
    ret = (completion['choices'][0]['message']['content'])
    print('\n>> LM response:\n', ret)
    print('\n>> over LM response.\n', flush=True)
    return ret

class VicunaMind(AbstractMind):
    def __init__(self, model_id='7B'):
        self.model_id= model_id
        self.url = 'http://127.0.0.1:8000'
        
        #from fastchat import client as fsclient #async issues #pip install fschat

    def build_query(self, prompt_msg, stop=None):
        msg = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt_msg}],
            "temperature": 0, "max_new_tokens": 256, 
        }
        if stop:
            msg["stop"] = stop
        return msg
    
    def ask(self, query, stop=None):
        query = self.build_query(query, stop=stop)
        ret = call_api(query, self.url)
        return ret

from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
class VicunaLLM(LLM, VicunaMind):        
    @property
    def _llm_type(self) -> str:
        return "vicuna"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return self.ask(prompt, stop=stop)
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            'name': 'vicunallm'
        }
'''
TEST

curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "7B",
    "messages": [{"role": "user", "content": "Hello! What is your name?"}]
  }'
'''

  #from logging_utils import persistent_lru_cache
#@persistent_lru_cache(maxsize=1000)

def _OpenAIChatAPI(messages):
    '''
    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]'''

    messages = [dict(d) for d in messages]

    import openai
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    '''  temperature=0,
        max_tokens=150,
        top_p=0.5,
        stream=True,
        frequency_penalty=0,
        presence_penalty=0
    '''
    return res['choices'][0]['message']['content']


def OpenAIChatAPI(messages):
    msgs = tuple(tuple(sorted(d.items())) for d in messages)
    return _OpenAIChatAPI(msgs)