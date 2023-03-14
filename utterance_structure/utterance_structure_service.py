# Service to manage the 'conversational turn structure' of an agent
# Basically the primary template used to build the agents utterance in a conversaition turn to a LLM
# 
# This initial version of the service supplies the utterance element for 'conversation_utterance_structure'
# 
# 
import logging

from common.utterance_element_proxy import UtteranceElementProxy

class ConversationUtteranceStructureService:
	def __init__(self, broker_config):
		self.proxy = UtteranceElementProxy(["conversation_utterance_structure"], self.provide_utterance_structure, broker_config, 'Conversation Utterance Structure')

	def provide_utterance_structure(self, keys, context):
		# TO DO only send requested fragements, and base the returned fragments on the context
		utterance_structure = """
			<{Personality}>
			My beliefs are:
			<{Constitution}>
			Please reply to the following, on my behalf, respecting my beliefs

			How do I bake a cake?

		"""

		logging.info(f'Conversation Utterance Structure Service - {keys} requested in context {context}\nReturning: \"{utterance_structure}\"')
		return_data = {'conversation_utterance_structure':utterance_structure}
		return return_data

	def run(self):
		self.proxy.start_listening()

if __name__ == '__main__':

	broker_config = {'rabbitmq': {'host':'localhost'}} 
	service = ConversationUtteranceStructureService(broker_config)
	service.run()
