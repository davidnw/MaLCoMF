#  This manages the running of multiple MaLCoMF microservices on a single machine
#  
#  This is to simplify developement, demonstration and debugging
#  
#  Services are connected via RabbitMQ so could normally be distributed using containers or similar techniques
#  
#  Here we just run each microservice in a separate thread
#  
#  THIS FILE IS EXPERIMENTAL !!!
#  
import logging
import threading

import time


from multiprocessing import Process


from constitution_service.constitution_service import ConstitutionService
from personality_service.personality_service import PersonalityService


class fred:
	def __init__(self,ignore):
		None
	def run(self):
		while True:
		  print('hello from fred')
		  logging.info('Fred says hello')
		  time.sleep(5)


class jim:
	def __init__(self,ignore):
		None
	def run(self):
		while True:
		 print('hello from jim')
		 logging.info('Jim says hello')
		 time.sleep(10)

if __name__ == '__main__':
	
	# Configure logging to write to a file
	log_file = "malcomf_local.log"
	file_handler = logging.FileHandler(log_file)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(process)d %(threadName)s: %(message)s'))
	root_logger = logging.getLogger()
	root_logger.addHandler(file_handler)
	root_logger.setLevel(logging.INFO)

	def start_service_in_process(service, process_name):
		process = Process(target=service.run)
		process.name = process_name
		process.start()

	# create and start services
	# TO_DO : The service and number of instances shoud be configurable in a config file
	# For now we'll use a list of dicts with the class and the number of instances required
	# Note the Class is used in the dict not the class name
	
	microservice_list = [
		{'service_class':fred, 'own_process':True,  'count':3},
		{'service_class':jim,  'own_process':True, 'count':3},
		{'service_class':ConstitutionService,  'own_process':True, 'count':3}
	]
	
	broker_config = {'rabbitmq': {'host':'localhost'}} 

	for service in microservice_list:
		if service['own_process']:
			for instance_number in range(service['count']):
				instance = service['service_class'](broker_config)
				start_service_in_process(instance, f'{instance.__class__.__name__}_{instance_number}' )

