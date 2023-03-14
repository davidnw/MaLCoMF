# Class to configure the sequencing of the prticipants in the conversation
# Based on participants being in groups with the algorythm for selection
# from and sequencing being configurable.
# 

import random

class ConversationSequencer:
	def __init__(self):

		# The full sequence is made up from a number of sequences (e.g. a group sequence)
		self.sequences = []

	def add_sequence(self, sequence):
		self.sequences.append(sequence)

		# we iterate over all the sub-sequences in order
	def __iter__(self):
		self.currently_itterating_sequence_idx = 0
		self.current_iterator = iter(self.sequences[self.currently_itterating_sequence_idx])		
		return self

	def __next__(self):
		if not self.sequences:
			raise StopIteration # nothing to iterate

		if not self.current_iterator:
			self.current_iterator = iter(self.sequences[0])
			self.currently_iterating_sequence_idx = 0		

		try:
			return next(self.current_iterator)
		except StopIteration:
			if self.currently_itterating_sequence_idx == len(self.sequences) - 1:
				raise StopIteration
			else:
				self.currently_itterating_sequence_idx += 1
				self.current_iterator = iter(self.sequences[self.currently_itterating_sequence_idx])
				return next(self)

	class GroupSequence:
		def __init__(self, 
				participants, 
				sequence_type, 
				count=-1, 
				start_participant=0, 
				no_twice_in_a_row=True,
				conversation_type='default_conversation',
				conversation_stage='default_stage'):

			self.participants = participants

			if count == -1:
				count = len(self.participants)

			self.max_iter=count
			self.sequence_type = sequence_type
			self.conversation_type=conversation_type
			self.conversation_stage=conversation_stage

			self.start_participant = start_participant
			
			self.no_twice_in_a_row = no_twice_in_a_row
			self.last_participant=-1

		def __iter__(self):
			self.iter_count = 0
			self.next_participant=self.start_participant
			self.sampled_set = set()
			return self

		# returns a LIST of participants to request next utterances from - usually this is JUST ONE
		# but may be more if participant are to be asked in paralle
		def __next__(self):
			if self.iter_count < self.max_iter:

				if self.sequence_type == 'round_robin':
					if self.next_participant > len(self.participants) - 1:
						self.next_participant = 0
					p = self.participants[self.next_participant]
					self.last_participant = self.next_participant
					self.next_participant +=1

				if self.sequence_type == 'no_replace_sample':
					while True:
						# reset if we've used all the samples
						if len(self.sampled_set) == len(self.participants):
							self.sampled_set = set()
						idx = random.randint(0, len(self.participants)-1)
						p = self.participants[idx]
						if p  not in self.sampled_set: 
							if not self.no_twice_in_a_row or (self.no_twice_in_a_row and (idx != self.last_participant)):
								self.sampled_set.add(p)
								self.last_participant = idx
								break

				if self.sequence_type == 'replace_sample':
					while True:
						idx = random.randint(0, len(self.participants)-1)
						p = self.participants[idx]
						if not self.no_twice_in_a_row or (self.no_twice_in_a_row and (idx != self.last_participant)):
							self.last_participant = idx
							break

				if self.sequence_type == 'parallel':
					p = self.participants

				self.iter_count += 1
				return p, self.conversation_type, self.conversation_stage
			else:
				raise StopIteration		

