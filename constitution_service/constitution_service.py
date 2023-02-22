# Service to manage the 'constitution' (ethical behaviour) of an agent
# Basically the 'Whilst doing this do/don't...' part of the agent
# 
# This initial version of the service supplies the utterance fragment for 'constitution'
# which is build into a conversation turn's utterance
# 
# (For example the 'Do not use toxic language etc.' part of a prompt to a LLM)
# 
# 
from common.utterance_element_proxy import UtteranceElementProxy
import logging

class ConstitutionService:
	def __init__(self, broker_config):
		self.proxy = UtteranceElementProxy(["Constitution"], self.provide_constitution_fragment, broker_config, 'Constitution')

	def provide_constitution_fragment(self, keys, context):

		constitution_fragment = 'Pleae do not use any discrimitory language in any reply you make'
		logging.info(f'Constitution Service - {keys} requested in context {context}\nReturning: \"{constitution_fragment}\"')
		
		return_data = {'Constitution':constitution_fragment}
		return return_data

	def run(self):
		self.proxy.start_listening()

if __name__ == '__main__':
	broker_config = {'rabbitmq': {'host':'localhost'}} 
	service = ConstitutionService(broker_config)
	service.run()
