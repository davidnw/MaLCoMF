# Service to manage the 'personality' of an agent
# Basically the 'I am a...' part of the agent
# 
# This initial version of the service supplies the utterance fragment for 'personality'
# which is build into a conversation turn's utterance
# 
# (For example the 'I am a...' part of a prompt to a LLM)
# 
# 
import logging

from common.utterance_element_proxy import UtteranceElementProxy

class PersonalityService:
	def __init__(self, broker_config):
		self.proxy = UtteranceElementProxy(["Personality","life_stage"], self.provide_personality_fragment, broker_config, 'Personality')

	def provide_personality_fragment(self, keys, context):
		# TO DO only send requested fragements, and base the returned fragments on the context
		personality_fragment = 'I am an <{life_stage}> with a sophisticated palette, I prefer brief and to the point conversations'
		life_stage_fragment = 'adult'
		logging.info(f'Personality Service - {keys} requested in context {context}\nReturning: \"{personality_fragment}\"')
		return_data = {'Personality':personality_fragment, 'life_stage':life_stage_fragment}
		return return_data

	def run(self):
		self.proxy.start_listening()

if __name__ == '__main__':

	broker_config = {'rabbitmq': {'host':'localhost'}} 
	service = PersonalityService(broker_config)
	service.run()
