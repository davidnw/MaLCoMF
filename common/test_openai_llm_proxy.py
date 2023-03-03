import unittest

from common.openai_llm_proxy import OpenAILLMProxy

class TestOpenAILLMProxy(unittest.TestCase):
	def setUp(self):
		self.oaip = OpenAILLMProxy()

	def test_get_embedding(self):
		text = 'This is the voice of Colossus'
		embedding = self.oaip.get_embedding(text)

		self.assertEqual(len(embedding), 1536)

	def test_get_completion(self):
		text = 'A good chocolate cake recipe is: '

		completion = self.oaip.get_completion(text)

		print(completion)

		self.assertIsInstance(completion, type(''))


