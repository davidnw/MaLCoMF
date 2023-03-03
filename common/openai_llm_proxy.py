# A simple wrapper around the openai API 
# 
# This allows consistent management of the API and potential substitutions for other LLM in the future
# 
import logging
import openai
from api_keys import openai_apikey

# define a retry decorator to manage rate limits
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.error.RateLimitError,),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper

def get_embedding(text, engine='text-embedding-ada-002'):
    response = embeddings_with_backoff(input=text,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector

	# define a function for embeddings with the back off function
@retry_with_exponential_backoff
def embeddings_with_backoff(**kwargs):
    return openai.Embedding.create(**kwargs)

@retry_with_exponential_backoff
def completions_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)    

# The default values can be set at init at a class level and, if desired, overwritten on each functional call
class OpenAILLMProxy:
	def __init__(self, 
			default_embeddings_engine='text-embedding-ada-002',
			default_completion_engine='text-davinci-003',
			default_temp=0.3,
			default_top_p=1.0,
			default_tokens=500,
			default_freq_pen=0.25,
			default_pres_pen = 0.0
			):

		self.default_embeddings_engine = default_embeddings_engine
		self.default_completion_engine = default_completion_engine
		self.default_temp = default_temp
		self.default_top_p = default_top_p
		self.default_tokens = default_tokens
		self.default_freq_pen = default_freq_pen
		self.default_pres_pen = default_pres_pen

		openai.api_key = openai_apikey
		

	def get_embedding(self, text, **kwargs):
		embedding_engine = kwargs.get('embedding_engine', self.default_embeddings_engine)
		response = embeddings_with_backoff(input=text, engine=embedding_engine)
		
		logging.info('Embedding response: {response}')

		return response['data'][0]['embedding']

	def get_completion(self, text, **kwargs): 

		completion_engine=kwargs.get('completion_engine',self.default_completion_engine)
		temp=kwargs.get('temperature',self.default_temp)
		top_p=kwargs.get('top_p',self.default_top_p)
		tokens=kwargs.get('max_tokens',self.default_tokens)
		freq_pen=kwargs.get('frequency_penalty',self.default_freq_pen)
		pres_pen=kwargs.get('presence_penalty',self.default_pres_pen)

		response = completions_with_backoff(
                        engine=completion_engine,
                        prompt=text,
                        temperature=temp,
                        max_tokens=tokens,
                        top_p=top_p,
                        frequency_penalty=freq_pen,
                        presence_penalty=pres_pen)

		logging.info(f'Completion response: {response}')

		return response['choices'][0]['text']




