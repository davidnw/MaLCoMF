# This service manages ONE conversation turn with the LLM
# 
import pika
import logging

class ConversationTurnService:
	def __init__(self,broker_config):
		self.instance_id = id(self)

		# This exchange and q names should probably be declared globaly as they are duplicated accross services!
		self.utterance_element_response_exchange_name = 'utterance_elements_response'
		self.uttance_element_request_exchange_name = 'utterance_element_request'

		# These are shared be all instances of the service
		self.converation_turn_request_exchange_name = 'conversation_turn_request_exchange'
		self.converation_turn_request_queue_name = 'conversation_turn_request_queue'

		# This is specific to the instance of the service
		self.return_route_name = f'conversational_turn_return_route_{self.instance_id}'

		self.broker_config =broker_config
		self.setup_event_queues()
	
	def setup_event_queues(self):
		# Set up the connection parameters for RabbitMQ
		connection_params = pika.ConnectionParameters(host=self.broker_config['rabbitmq']['host'])
		connection = pika.BlockingConnection(connection_params)

		# Set up a channel to communicate with RabbitMQ
		channel = connection.channel()

		# This is where I listen for requests for new conversational turns
		channel.exchange_declare(exchange=self.converation_turn_request_exchange_name, exchange_type='fanout')
		channel.queue_declare(queue=self.converation_turn_request_queue_name)
		channel.queue_bind(exchange=self.converation_turn_request_exchange_name, queue=self.converation_turn_request_queue_name)
		channel.basic_consume(queue=self.converation_turn_request_queue_name, on_message_callback=self.on_conversational_turn_request_message, auto_ack=True)

		# This is where I publish my requests for utterance elements
		channel.exchange_declare(exchange=self.uttance_element_request_exchange_name, exchange_type='fanout')
		
		# This is where I listen on my own q for returning utterance elements
		result = channel.queue_declare(queue='', exclusive=True)
		channel.queue_bind(queue=result.method.queue, exchange=self.utterance_element_response_exchange_name, routing_key=self.return_route_name)
		channel.basic_consume(queue=result.method.queue, on_message_callback=self.on_utterance_data_message, auto_ack=True)

		self.channel = channel	

	def on_conversational_turn_request_message(self, channel, method, properties, body):
		logging.info(f'request recieved {body}')

	def on_utterance_data_message(self, channel, method, properties, body):
		logging.info(f'utterance data received {body}')

	def run(self):
		logging.info(f'Conversation Turn Service Started Listening')
		self.channel.start_consuming()
		


