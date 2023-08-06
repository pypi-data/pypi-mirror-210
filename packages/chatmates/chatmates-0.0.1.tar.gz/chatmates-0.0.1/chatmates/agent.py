import ray
from mind import SimpleMind as Mind
import logging

ray.init(local_mode=True) 


@ray.remote
class Assistant:
    def __init__(self, value):
        self.value = value
        self.mind = Mind.options(name="assistant.mind", get_if_exists=True).remote('*assistant.mind*')
        #self.mind = ray.get_actor('assistant.mind')
        logging.basicConfig(level=logging.INFO)

    def log(self, msg):
        logging.info(msg)

    #def __repr__(self):
    #    return f"Assistant(value={self.value})"

    def ask(self, msg):
        #mind = ray.get_actor('assistant.mind')
        resp = self.mind.ask.remote(msg)
        resp = ray.get(resp)
        ret = f'response: {resp}'
        self.log(ret)
        return ret


def test():
    assistant = Assistant.options(name="assistant", get_if_exists=True).remote('*assistant*')
    answer = assistant.ask.remote('how are you?')
    answer = ray.get(answer)
    print(answer)



if __name__ == '__main__':
    test()
    

    