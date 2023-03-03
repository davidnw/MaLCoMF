# This service manages ONE conversation turn with the LLM
# 

import logging
from uuid import uuid4
import json
from conversation_turn.utterance_cache import UtteranceCache
from conversation_turn.conversation_turn_messaging_proxy import ConversationTurnMessagingProxy
from common.openai_llm_proxy import OpenAILLMProxy

import re

class ConversationTurnService:
	def __init__(self,broker_config):

		self.llm_proxy = OpenAILLMProxy()
		self.utterance_cache = UtteranceCache()
		self.ctm_proxy = ConversationTurnMessagingProxy(
			broker_config, 
			self.process_conversational_turn_request,
			self.process_utterance_data,
			'Conversation Turn Service')

	def process_conversational_turn_request(self, body):
		logging.info(f'request recieved {body}')
		# Use the context in the body to request the utterace elements for this conversation turn
		try:
			# Check if this service is responsible for the missing data
			request_data = json.loads(body.decode('utf-8'))
			requester_id = request_data['requester_id']  # used to route back response
			context = request_data['context']

			# TODO WHAT TO "BUILD IS SPOOFED"
			logging.warning('The converation request turn function is incomplete')

			utterance_id = self.utterance_cache.create()

			self.utterance_cache.add_requester_id(utterance_id, requester_id)

			logging.info(f"CONTEXT: {context} type: {type(context)}")

			self.utterance_cache.add_context(utterance_id, context)

			requested_elements=['conversation_utterance_structure']
			self.ctm_proxy.request_utterance_elements(utterance_id,requested_elements,context)
			self.utterance_cache.mark_requested(utterance_id,requested_elements)


		except Exception as e:
			logging.warning(f'Error processing conversation turn request', exc_info=True)	


	def extract_sub_elements(self,text):
	    pattern = r'<{(.+?)}>'
	    tokens = re.findall(pattern, text)
	    return tokens

	def process_utterance_data(self, body):
		logging.info(f'utterance data received {body}')

		try:
			# Check if this service is responsible for the missing data
			request_data = json.loads(body.decode('utf-8'))

			# Mark the utterance elements recieved
			utterance_id = request_data['utterance_id']
			self.utterance_cache.add_recieved_data(utterance_id, request_data['utterance_data'])

			# TODO UTTERANCE CONTEXT SHOULD BE CACHED NOT PASSED BACK WITH DATA
			context = request_data['context']
			
			# check if the recieved elements need any other elements and if we have them
			# if not request them
			element_data = self.utterance_cache.recieved_element_data(utterance_id)
			required_elements = []
			for key, data in element_data.items():
				required_elements += self.extract_sub_elements(data)

			# check if we have recieved everything
			received_elements = self.utterance_cache.received_elements(utterance_id)
			missing_elements = set(required_elements) - set(received_elements)

			logging.info(f'missing sub_elements {missing_elements}')

			if len(missing_elements) != 0:
				# check if we've already requested then
				unrequested_missing_elements = missing_elements - set(self.utterance_cache.requested_elements(utterance_id))
				logging.info(f'unrequested {unrequested_missing_elements}')

				# request them...
				self.ctm_proxy.request_utterance_elements(utterance_id,list(unrequested_missing_elements),context)
				self.utterance_cache.mark_requested(utterance_id,list(unrequested_missing_elements))
				
			# if we have everything we need - build and sent the utterance to the LLM
			outstanding_requested = self.utterance_cache.requested_elements(utterance_id)
			if len(outstanding_requested) == 0:
				logging.info(f'All utterance elenents received for id {utterance_id}')
				completed_utterance = self.build_complete_utterance(utterance_id)
				self.send_utterance_and_process_response(utterance_id, completed_utterance)
			else:
				logging.info(f'waiting for {outstanding_requested} for id {utterance_id}')

		except Exception as e:
			logging.warning(f'Error processing utterance data message', exc_info=True)	

	def resolve_tokens(self, strings, max_depth=10):
		unresolved_tokens = set(re.findall(r'<\{(\w+)\}>', ' '.join(strings.values())))
		missing_tokens = set(unresolved_tokens) - set(strings.keys())
		if len(missing_tokens) > 0:
			raise ValueError(f'Missing tokens in data set: {missing_tokens}')

		processed_strings = strings
		depth_count = 0
		while unresolved_tokens:

			depth_count += 1

			# build a dictionary of the replacement tokens and the associated strings
			# the associated strings are the strings with the substitutions we have made so far
			replacement_dict = {'<{' + k + '}>': v for k, v in processed_strings.items()}

			# pass throught the strings making the substitutions
			for token, current_value in processed_strings.items():
				new_value = current_value

				# replace all tokens in the current string
				for token_to_replace, replacement_string in replacement_dict.items():
					new_value = new_value.replace(token_to_replace, replacement_string)
		
				processed_strings[token] = new_value

			# update the unresolved tokens list
			unresolved_tokens = set(re.findall(r'<\{(\w+)\}>', ' '.join(processed_strings.values())))

			if unresolved_tokens and depth_count == max_depth:
				raise ValueError(f'Max depth exceeded, possible circular dependencies, remaining unresolved tokens: {unresolved_tokens}')

		return processed_strings
 
	def build_complete_utterance(self,utterance_id):
		# get all the utterance 
		recieved_data_elements = self.utterance_cache.recieved_element_data(utterance_id)

		# replace the tags in each element with the other elements...
		replaced = self.resolve_tokens(recieved_data_elements)

		# TODO - IDENTIFY MAIN UTTERANCES
		logging.info(f'Utterance elements with tokens resolved {replaced}')
		return replaced['conversation_utterance_structure']

	def send_utterance_and_process_response(self, utterance_id, utterance_text):
		response = self.llm_proxy.get_completion(utterance_text)

		# send the reponse back to the queue that requested this conversation turn...
		context = self.utterance_cache.get_context(utterance_id)
		requester_id = self.utterance_cache.get_requester_id(utterance_id)

		self.ctm_proxy.respond_to_requester(requester_id, context, utterance_text, response)

		# all done so remove from cache
		self.utterance_cache.delete(utterance_id)

	def run(self):
		self.ctm_proxy.start_listening()


		

		


