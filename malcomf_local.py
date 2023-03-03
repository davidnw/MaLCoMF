#  This manages the running of multiple MaLCoMF microservices on a single machine
#  
#  This is to simplify developement, demonstration and debugging
#  
#  Services are connected via RabbitMQ so could normally be distributed using containers or similar techniques
#  
#  Here we just run each microservice in a separate thread
#  
import logging
import threading


from constitution.constitution_service import ConstitutionService
from personality.personality_service import PersonalityService
from conversation_turn.conversation_turn_service import ConversationTurnService
from conversation_turn.conversation_turn_structure_service import ConversationUtteranceStructureService

if __name__ == '__main__':
	
	# Configure logging to write to a file
	log_file = "malcomf_local.log"
	file_handler = logging.FileHandler(log_file)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(process)d %(filename)s:%(lineno)d %(threadName)s: %(message)s'))
	root_logger = logging.getLogger()
	root_logger.addHandler(file_handler)
	root_logger.setLevel(logging.INFO)
	
	def start_service_in_thread(service, thread_name):
		thread = threading.Thread(target=service.run)
		thread.name = thread_name
		thread.start()

	# create and start services
	# TO_DO : The service and number of instances shoud be configurable in a config file
	# For now we'll use a list of dicts with the class and the number of instances required
	# Note the Class is used in the dict not the class name
	
	# Only use own_process:False for now! i.e. threadded in one process
	microservice_list = [
		{'service_class':ConstitutionService, 'own_process':False, 'count':1},
		{'service_class':PersonalityService, 'own_process':False, 'count':1},
		{'service_class':ConversationTurnService, 'own_process':False, 'count':1},
		{'service_class':ConversationUtteranceStructureService, 'own_process':False, 'count':1}
	]
	
	broker_config = {'rabbitmq': {'host':'localhost'}} 

	for service in microservice_list:
		if not service['own_process']:
			for instance_number in range(service['count']):
				instance = service['service_class'](broker_config)
				start_service_in_thread(instance, f'{instance.__class__.__name__}_{instance_number}')

