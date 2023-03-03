import logging
from uuid import uuid4

class UtteranceCache:
	# {
	# 	utterance_key: {
	# 	  [
	# 	  	{'element_name': '', 'element_data': '', 'element_status': ''},
	# 	  	{'element_name': '', 'element_data': '', 'element_status': ''},
	# 	  	{'element_name': '', 'element_data': '', 'element_status': ''}
	# 	  ]
	# 	}
	# }
	# Where status is 'requested', 'not requested', 'recieved' etc.

	def __init__(self):
		self.data = {}
		self.meta_data = {}

	def create(self, utterance_elements=[]):
		id = str(uuid4())
		initial_element_list = [{'element_name':e['element_name'], 
								'element_data':e['element_data'], 
								'element_status':'not_requested'} for e in utterance_elements]
		self.data[id] = initial_element_list
		return id

	def mark_requested(self, utterance_id, element_names):
		if utterance_id not in self.data:
			logging.warning(f"utterance_id {utterance_id} not found in cache during mark requested")
		else:
			elements_list = self.data[utterance_id]
			for req_elemnent_name in element_names:
				maked = False	
				for e in elements_list:
					if e['element_name'] == req_elemnent_name:
						e['element_status'] = 'requested'
						maked = True
				if not maked:
					new_element = {'element_name':req_elemnent_name, 'element_status':'requested'}
					elements_list.append(new_element)


	def delete(self, utterance_id):
		if utterance_id not in self.data:
			logging.warning(f"utterance_id {utterance_id} not found in cache during delete")
		else:
			self.data.pop(utterance_id)
			self.delete_meta(utterance_id)

	def add_recieved_data(self, utterance_id, new_data):
		if utterance_id not in self.data:
			logging.warning(f"utterance_id {utterance_id} not found in cache during adding received")
		else:
			elements_list = self.data[utterance_id]

			# find each element entry and update it
			for key, value in new_data.items():
				key_found = False
				for e in elements_list:
					if e['element_name'] == key:
						e['element_data'] = value
						e['element_status'] = 'received'
						key_found = True
						break
				# If the element was not in the element list add it to the list
				if not key_found:
					new_e = {'element_name':key,'element_data':value,'element_status':'received'}
					elements_list.append(new_e)
			
	
	def unrequested_elements(self,utterance_id):
		return [e['element_name'] for e in self.data[utterance_id] if e['element_status'] == 'not_requested']

	def requested_elements(self,utterance_id):
		return [e['element_name'] for e in self.data[utterance_id] if e['element_status'] == 'requested']

	def received_elements(self,utterance_id):
		return [e['element_name'] for e in self.data[utterance_id] if e['element_status'] == 'received']

	def recieved_element_data(self,utterance_id,requested_names=[]):
		return_data = {}
		if utterance_id not in self.data:
			logging.warning(f"utterance_id {utterance_id} not found in cache during getting element data")
		else:
			elements_list = self.data[utterance_id]
			for e in elements_list:
				if e['element_status'] == 'received' and (e['element_name'] in requested_names or len(requested_names) == 0):
					return_data[e['element_name']] = e['element_data']
		return return_data


# Methods to manage meta data associated with the utterance

	def add_requester_id(self, utterance_id, requester_id):
		if utterance_id not in self.meta_data:
			utterance_meta = {'requester_id':requester_id}
			self.meta_data[utterance_id] = utterance_meta
		else:
			utterance_meta = self.meta_data[utterance_id]
			utterance_meta['requester_id'] = requester_id

	def add_context(self, utterance_id, context):
		if utterance_id not in self.meta_data:
			utterance_meta = {'context':context}
			self.meta_data[utterance_id] = utterance_meta
		else:
			utterance_meta = self.meta_data[utterance_id]
			utterance_meta['context'] = context

	def get_requester_id(self, utterance_id):
		if utterance_id not in self.meta_data:
			logging.warning(f'unavailable meta_data being requested for {utterance_id}')
		else:
			return self.meta_data[utterance_id]['requester_id']	

	def get_context(self, utterance_id):
		if utterance_id not in self.meta_data:
			logging.warning(f'unavailable meta_data being requested for {utterance_id}')
		else:
			return self.meta_data[utterance_id]['context']	

	def delete_meta(self,utterance_id):
		if utterance_id not in self.meta_data:
			logging.warning(f'trying to delete non-existing meta_data being requested for {utterance_id}')
		else:
			return self.meta_data.pop(utterance_id)


