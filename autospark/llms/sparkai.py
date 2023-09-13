from autospark.config.config import get_config
from autospark.lib.logger import logger
from autospark.llms.base_llm import BaseLlm

from sparkai.api_resources import *
from sparkai.api_resources.chat_completion import *
from sparkai.schema import ChatMessage
from sparkai.models.chat import ChatBody, ChatResponse


class SparkAI(BaseLlm):
    def __init__(self, api_key, api_secret, app_id, model="spark-2.1", temperature=0.6,
                 max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        """
        Args:
            api_key (str): The OpenAI API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
            frequency_penalty (float): The frequency penalty.
            presence_penalty (float): The presence penalty.
            number_of_results (int): The number of results.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.number_of_results = number_of_results
        self.api_key = api_key
        api_base = get_config("SPARK_AI_API_BASE", "wss://spark-api.xf-yun.com/v2.1/chat")
        if not api_key or not api_base or not api_secret or not app_id:
            logger.error("wrong Config With Spark Creds")
        self.ws = SparkOnceWebsocket(api_key=api_key, api_secret=api_secret, app_id=app_id, api_base=api_base)
        # messages = [
        #    {'role': 'user', 'content': '请帮我完成目标:\n\n帮我生成一个 2到2000的随机数\n\n'}, {'role': 'assistant',
        #                                                                      'content': '{\n\n"thoughts": {\n\n"text": "Generate a random number between 2 and 2000.",\n\n"reasoning": "To complete this task, I will need to access the internet for information gathering.",\n\n"plan": "I will use the random_number command with the min and max arguments set to 2 and 2000, respectively.",\n\n"criticism": "",\n\n"speak": "The random number generated is: 1587."\n\n},\n\n"command": {\n\n"name": "random_number",\n\n"args": {\n\n"min": "2",\n\n"max": "2000"\n\n}\n\n}\n\n}'},
        #    {'role': 'user', 'content': '\n请帮我完成目标:\n\n帮我把这个随机数 发给 ybyang7@iflytek.com 并告诉他这个随机数很重要\n\n'}]

        # c.send_messages(messages)

    def get_source(self):
        return "iflytek"

    def get_api_key(self):
        """
        Returns:
            str: The API key.
        """
        return self.api_key

    def get_model(self):
        """
        Returns:
            str: The model.
        """
        return self.model

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):
        """
        Call the SparkAI chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            # response = openai.ChatCompletion.create(
            #     n=self.number_of_results,
            #     model=self.model,
            #     messages=messages,
            #     temperature=self.temperature,
            #     max_tokens=max_tokens,
            #     top_p=self.top_p,
            #     frequency_penalty=self.frequency_penalty,
            #     presence_penalty=self.presence_penalty
            # )
            new_messages = []
            for m in messages:
                if m['role'] == 'system':
                    m['role'] = 'user'
                new_messages.append(m)
            code, response = self.ws.send_messages(new_messages)
            # content = response.choices[0].message["content"]
            return {"response": response, "content": response}
        except Exception as exception:
            logger.info("SparkAI Exception:", exception)
            return {"error": "ERROR_SPARK", "message": "Spark exception"}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            # todo
            # models = openai.Model.list()
            return True
        except Exception as exception:
            logger.info("SPARK Exception:", exception)
            return False

    def get_models(self):
        """
        Get the models.

        Returns:
            list: The models.
        """
        try:
            models = ['spark-2.1']
            models_supported = ['spark-2.1']
            print("CHECK THIS1", models)
            models = [model for model in models if model in models_supported]
            return models
        except Exception as exception:
            logger.info("SPARKAI Exception:", exception)
            return []
