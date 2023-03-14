# A simple facard to an LLM model that injects a personality into the prompts
# 

import logging

from common.openai_llm_proxy import OpenAILLMProxy

class ConversationParticipant:
	def __init__(self, participant_name):
		self.llm_proxy = OpenAILLMProxy()
		self.participant_name = participant_name

		# The participant is configured with a 'llm breifing' telling it how to brief the LLM for each type of 
		# conversation and the stage it its at.  
		# 
		# If nothing specific is found for the conversation stage, the default for the conversation is used
		# If nothing specific is found fot the conversation type, the default is used
		# 
		# The briefing string will be python formatted, so '{name}' may be used to insert the participants name
		# into the llm brifing string, {personaility} maybe used to insert the personality into the briefing string
		
		self.llm_briefing = {'default_conversation':{'default_stage':"""
		You are {name}. You are participting in the above conversation.
		You are {personality}.
		Add one contribution to the conversation as {name}.
		{name}:
		"""}
		}

		# set the default personality
		self.personality = 'a helpful and consise assistent, who replys to the best of your capability, but isn\'t affraid to say "I don\'t know" if necessary' 

	def utterance_for_conversation(self, conversation, conversation_type='default_conversation', conversation_stage='default_stage'):

		# buid the llm briefing string..
		name = self.participant_name
		personality = self.personality

		llm_briefing = self.get_llm_briefing(conversation_type, conversation_stage)
		llm_briefing = llm_briefing.format(**locals())

		to_llm = conversation + '/n' + llm_briefing + '/n'

		response = self.llm_proxy.get_chat_completion(to_llm)
		
		logging.info(f'{self.participant_name} adding "{response}"" to conversation')

		return response, llm_briefing

	def add_llm_briefing(self, conversation_type, conversation_stage, llm_briefing):
		if conversation_type in self.llm_briefing:
			self.llm_briefing[conversation_type][conversation_stage] = llm_briefing
		else:
			self.llm_briefing[conversation_type] = {conversation_stage: llm_briefing}

	def get_llm_briefing(self, conversation_type,conversation_stage):
		default = self.llm_briefing.get('default_conversation', {}).get('default_stage')
		return self.llm_briefing.get(conversation_type, {}).get(conversation_stage, default)


    