# This service provides a collaboration environment for multiple agents
# 
# Basically it contains a group conversation and a group context for the agents
# 
# It does not have any agency itself. e.g. it does not talk to a LLM or independently add to the 
# conversation or the context of the group.
# 
# It expects the agents themselves to do this 
# (e.g. a lead agent (say a project manager agent) may set the approach for the group)
# 
# The messaging is, as usual done through a proxy to allow swap outs for other messageing architectures later
# 

from agent_group.rabbitmq_agent_group_proxy import AgentGroupProxy
import json
import time

class AgentGroup:

	def __init__(self, broker_config):

		# A list of all groups conversation
		self.conversation_history = []

		# A dictionary that any agent can read and write to
		self.group_context = {}

		# The agents in this group.  A dictionary of dictionaries indexed by the agents_id
		self.agents = {}

		self.group_proxy = AgentGroupProxy(broker_config, incoming_utterance)

				

	def incoming_utterance(self, body):
		logging.info(f'utterance recieved {body}')
		# Use the context in the body to request the utterace elements for this conversation turn
		try:
			# Check if this service is responsible for the missing data
			data = json.loads(body.decode('utf-8'))
			agent_id = request_data['agent_id']  # unique - used to route back response
			agent_name = data['agent_name'] # used as name within the conversations
			utterance = request_data['utterance']

			# Store the utterance
			self.conversation_history.append({'timestamp':time.time(), 'agent_name':agent_name, 'utterance':utterance})
			
			# Broadcast to all member agents
			self.group_proxy.send_conversation_history(self.conversation_history)
			
			
		except Exception as e:
			logging.warning(f'Error processing conversation utterance', exc_info=True)	

	# Basic in memory storage...
	# TODO should probably be persistant and stored so service can be stateless
	# TODO agents should be able to access this context data via messaging

	def get_from_group_context(self, key):
		return self.group_context[key]

	def update_group_context(self, key, value):
		self.group_context[key] = value
