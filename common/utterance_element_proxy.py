# This a common class to listen for and send messages to the message broker
# It abstracts the message broker from the data (utterance element) provider
# It should be included in the data provide microservice by composition

import pika
import json
import logging

class UtteranceElementProxy:
	
	def __init__(self, prompt_tags, utterance_element_request_function, broker_config, service_name):
		self.prompt_tags = prompt_tags
		self.utterance_element_request_function = utterance_element_request_function
		self.broker_config =  broker_config
		self.service_name = service_name

		# Define the names of the queues and exchanges
		# All Utterance Proxies Listen on the same exchange
		# All instances of a service type using a proxy use the same q (appended with _service name)
		self.uttance_element_request_exchange_name = 'utterance_element_request'		 # Exchange used for conversations
		self.receive_queue_name = f'utterance_elements_requests_for_{service_name}' # Listen here for requests for utterance elements
		
		# Exchange to send responses back to - the routing_key is use to route to requesters specific q (included in the request message)
		self.utterance_element_response_exchange_name = 'utterance_elements_response'

		self.setup_event_queues()

		logging.info(f'Proxy for {service_name} set up')

	def setup_event_queues(self):
		# Set up the connection parameters for RabbitMQ
		connection_params = pika.ConnectionParameters(host=self.broker_config['rabbitmq']['host'])
		connection = pika.BlockingConnection(connection_params)

		# Set up a channel to communicate with RabbitMQ
		channel = connection.channel()

		# The queue to listen on.  The exchange fans the messages to all utterance element provider Qs
		# there's one for each service type - and all instances of a service listen on the same q
		channel.exchange_declare(exchange=self.uttance_element_request_exchange_name, exchange_type='fanout')
		channel.queue_declare(queue=self.receive_queue_name)
		channel.queue_bind(exchange=self.uttance_element_request_exchange_name, queue=self.receive_queue_name)

		# Listen for messages on the request queue
		channel.basic_consume(queue=self.receive_queue_name, on_message_callback=self.on_element_request_message, auto_ack=True)

		# Set up the exchange (to send messages out to)
		channel.exchange_declare(exchange=self.utterance_element_response_exchange_name, exchange_type='direct')

		self.channel = channel

	def on_element_request_message(self, channel, method, properties, body):

		try:
			# Check if this service is responsible for the missing data
			request_data = json.loads(body.decode('utf-8'))

			# split out the expected elements
			data_requested = request_data['data_requested']
			context = request_data['context']
			return_route_name = request_data['return_route_name']
			utterance_id = request_data['utterance_id']

			print(f'Element Request Message Recieved: {request_data}')

			# Find all the missing data keys that I am responsible for:
			print(f'Checking if {self.prompt_tags} are in {data_requested}')
			my_missing_keys = list(set(self.prompt_tags).intersection(data_requested))
			if len(my_missing_keys) > 0:
				# Provide the missing data in a message to the originator...
				utterance_data = self.utterance_element_request_function(my_missing_keys, context)

				# build the response - note TO_DO the full context might not need returning just an id from it
				return_data = {'utterance_data':utterance_data, 'context':context, 'utterance_id':utterance_id}

				# Publish the updated element fragment back to the source of the request
				channel.basic_publish(exchange=self.utterance_element_response_exchange_name, routing_key=return_route_name, body=json.dumps(return_data))
		
		except Exception as e:
			logging.warning(f'Error processing utterance fragment request', exc_info=True)	

	def start_listening(self):
		logging.info(f'{self.service_name} begining listening on {self.receive_queue_name}')
		self.channel.start_consuming()
		
	
# Tiny test prgram...
def main():
	def provide_elements(requested_element_fragment_keys, context):

		fragments = {}
		for k in requested_element_fragment_keys:
			fragments[k] = f'some data for {k}'

		print(f'Providing the following data {fragments} for context {context}')

		return fragments

	elements_fragments_I_manage = {"Personality", "Favorite Colour"}


	broker_config = {'rabbitmq': {'host':'localhost'}}
	proxy = UtteranceElementProxy(elements_fragments_I_manage, provide_elements, broker_config)
	proxy.start_listening()


if __name__ == "__main__":
	main()