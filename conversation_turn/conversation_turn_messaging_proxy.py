# A proxy for the RabbitMQ messaging in the conversation turn service

import pika
import logging
import json

class ConversationTurnMessagingProxy:
	def __init__(self, broker_config, conversation_request_received_function, utterance_element_recieved_function, service_name):

		# This exchange and q names should probably be declared globaly as they are duplicated accross services!
		self.utterance_element_response_exchange_name = 'utterance_elements_response'
		self.uttance_element_request_exchange_name = 'utterance_element_request'

		# These are shared be all instances of the service
		self.converation_turn_request_exchange_name = 'conversation_turn_request_exchange'
		self.converation_turn_response_exchange_name = 'conversation_turn_response_exchange'
		self.converation_turn_request_queue_name = 'conversation_turn_request_queue'

		# This is specific to the instance of the service
		self.instance_id = id(self)
		self.return_route_name = f'conversational_turn_return_route_{self.instance_id}'

		self.utterance_element_recieved_function = utterance_element_recieved_function
		self.converation_request_recieved_function = conversation_request_received_function
		self.broker_config = broker_config
		self.service_name = service_name

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
		channel.basic_consume(queue=self.converation_turn_request_queue_name, on_message_callback=self.on_conversation_turn_request_message, auto_ack=True)

		# This is where I send my responses from the LLM for the conversation turn...
		channel.exchange_declare(exchange=self.converation_turn_response_exchange_name, exchange_type='direct')

		# This is where I publish my requests for utterance elements
		channel.exchange_declare(exchange=self.uttance_element_request_exchange_name, exchange_type='fanout')
		
		# This is where I listen on my own q for returning utterance elements
		result = channel.queue_declare(queue='', exclusive=True)
		channel.queue_bind(queue=result.method.queue, exchange=self.utterance_element_response_exchange_name, routing_key=self.return_route_name)
		channel.basic_consume(queue=result.method.queue, on_message_callback=self.on_utterance_data_message, auto_ack=True)

		self.channel = channel

	def on_utterance_data_message(self, channel, method, properties, body):
		self.utterance_element_recieved_function(body)

	def on_conversation_turn_request_message(self, channel, method, properties, body):
		self.converation_request_recieved_function(body)

	def request_utterance_elements(self,utterance_id,element_list,context):
		message_body = {
				'utterance_id':utterance_id,
				'data_requested':element_list,
				'context':context,
				'return_route_name':self.return_route_name
			}
		self.channel.basic_publish(exchange=self.uttance_element_request_exchange_name, routing_key='', body=json.dumps(message_body))

	def respond_to_requester(self, requester_id, context, our_utterance, response_text):
		body = {
			'context':context,
			'our_utterance':our_utterance,
			'response':response_text
		}

		self.channel.basic_publish(exchange=self.converation_turn_response_exchange_name, routing_key=requester_id, body=json.dumps(body))

	def start_listening(self):
		logging.info(f'{self.service_name} begining listening')
		self.channel.start_consuming()


