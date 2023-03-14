#  Receives and sends messaged to/from an agent group using rabbitmq
#  
#  Calls the passed in functions to deal with messages it has recieved
#  


import pika
import logging
import json

class AgentGroupProxy:
	def __init__(self, broker_config, incoming_converation_utterance_function, service_instance_name):
		self.config = broker_config
		self.incoming_converation_utterance_function = incoming_converation_utterance_function
		self.service_instance_name = service_instance_name

		self.utterance_broadcast_to_group_exchange_name = f'utterance_broadcast_to_agents_for_{service_instance_name}'
		self.utterance_receive_from_agent_exchange_name = f'utterance_from_agent_to_group'
		self.group_routhing_key = f'agent_group_{service_instance_name}'

		self.setup_event_queues()

	def setup_event_queues(self):

		# Set up the connection parameters for RabbitMQ
		connection_params = pika.ConnectionParameters(host=self.broker_config['rabbitmq']['host'])
		connection = pika.BlockingConnection(connection_params)

		# Set up a channel to communicate with RabbitMQ
		channel = connection.channel()

		# cerate an exchange and a q to recieve conversation utterances...
		channel.exchange_declare(exchange=self.utterance_receive_from_agent_exchange_name, exchange_type='direct')
		result = channel.queue_declare(queue='', exclusive=True)
		channel.queue_bind(queue=result.method.queue, exchange=self.utterance_receive_from_agent_exchange_name, routing_key=self.group_routhing_key)
		channel.basic_consume(queue=result.method.queue, on_message_callback=self.on_utterance_from_agent, auto_ack=True)

		# create an exchange to transmit the conversation to all agents...
		channel.exchange_declare(exchange=self.utterance_broadcast_to_group_exchange_name, exchange_type='fanout')

		self.channel = channel

		def on_utterance_from_agent(self, channel, method, properties, body):
			self.incoming_converation_utterance_function(body)

	def start_listening(self):
		logging.info(f'{self.service_name} begining listening')
		self.channel.start_consuming()

	def send_conversation_history(self, history):
		message_body = {
				send_conversation_history:history
			}
		self.channel.basic_publish(exchange=self.utterance_broadcast_to_group_exchange_name, routing_key='', body=json.dumps(message_body))




