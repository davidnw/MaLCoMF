import unittest

from group_conversation.conversation_sequencer import ConversationSequencer
from group_conversation.conversation_participant import ConversationParticipant

class TestConversationSequencer(unittest.TestCase):
	def setUp(self):
		self.cs = ConversationSequencer()
		self.group1_name = 'group 1'
		self.group1_size = 5
		self.participant_group1 = [ConversationParticipant(f'{self.group1_name} participant {n}') for n in range(self.group1_size)]
		self.group2_name = 'group 2'
		self.group2_size = 7
		self.participant_group2 = [ConversationParticipant(f'{self.group2_name} participant {n}') for n in range(self.group2_size)]

	def test_round_robin_group_sequence(self):

		# twice round the group
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='round_robin', count=10)
		gs_iter = iter(gs)
		iterations = 0
		for n, participant in enumerate(gs_iter):
			p, conv_type, conv_stage = participant
			iterations += 1
			self.assertEqual(p.participant_name, f'{self.group1_name} participant {n%self.group1_size}')
			self.assertIsInstance(p, ConversationParticipant)

		self.assertEqual(iterations,10)


		# twice round the group starting at 3
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='round_robin', count=10, start_participant=3)
		gs_iter = iter(gs)
		iterations = 0
		for n, participant in enumerate(gs_iter):
			p, conv_type, conv_stage = participant
			iterations += 1
			self.assertEqual(p.participant_name, f'{self.group1_name} participant {(n+3)%self.group1_size}')
			self.assertIsInstance(p, ConversationParticipant)

		self.assertEqual(iterations,10)
		
	def test_no_replace_sample(self):

		required_samples = 10
		# check we get non repeating samlpes
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='no_replace_sample', count=required_samples, start_participant=3)
		gs_iter = iter(gs)
		seen = set()
		seen_count = 0
		for i, p in enumerate(gs_iter):
			if i < self.group1_size:
				self.assertTrue(p not in seen)
				seen.add(p)
			else:
				self.assertTrue(p in seen)

	def test_no_replace_sample_no_two_in_a_row(self):

		required_samples = 1000
		# check we get non repeating samlpes
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='no_replace_sample', count=required_samples, start_participant=3)
		gs_iter = iter(gs)

		last_p = None
		for p in gs:
			self.assertNotEqual(p, last_p)
			last_p = p


	def test_no_replace_sample_two_in_a_row(self):

		required_samples = 1000
		# check we get non repeating samlpes
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='no_replace_sample', no_twice_in_a_row=False, count=required_samples, start_participant=3)
		gs_iter = iter(gs)

		last_p = None
		found = False
		for p in gs:
			if p == last_p:
				found = True
				break
			last_p = p

		self.assertTrue(found)
			

	def test_replace_sample(self):

		required_samples = 10
		# check we get random samlpes
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='replace_sample', count=required_samples, start_participant=3)
		gs_iter = iter(gs)
		seen = set()
		
		# We should eventually see a previously returned participant before all others have been returned...
		seen_before = False
		for i, p in enumerate(gs_iter):
			if p in seen:
				seen_before = True
				break

			if i%self.group1_size == 0:
				seen = set()

			seen.add(p)
			
		self.assertTrue(seen_before)

	def test_replace_sample_no_two_in_a_row(self):

		required_samples = 1000
		# check we get non repeating samlpes
		gs = self.cs.GroupSequence(self.participant_group1, 
			sequence_type='replace_sample', 
			count=required_samples, 
			no_twice_in_a_row=True,
			start_participant=3)
		gs_iter = iter(gs)

		last_p = None
		for p in gs:
			self.assertNotEqual(p, last_p)
			last_p = p

	def test_replace_sample_two_in_a_row(self):

		required_samples = 1000
		# check we get non repeating samlpes
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='replace_sample', no_twice_in_a_row=False, count=required_samples, start_participant=3)
		gs_iter = iter(gs)

		last_p = None
		found = False
		for p in gs:
			if p == last_p:
				found = True
				break
			last_p = p

		self.assertTrue(found)

	def test_parallel_sequence(self):
		required_samples = 10 # should give the list of participants this many times...
		gs = self.cs.GroupSequence(self.participant_group1, sequence_type='parallel', no_twice_in_a_row=False, count=required_samples, start_participant=3)
		for ind,x in enumerate(gs):
			p, conv_type, conv_stage = x
			self.assertIsInstance(p, type([]))
			self.assertEqual(len(p),self.group1_size)
		self.assertEqual(ind+1,required_samples)

	def test_conversation_sequencer(self):
		gs1 = self.cs.GroupSequence(self.participant_group1, sequence_type='round_robin')
		gs2 = self.cs.GroupSequence(self.participant_group2, sequence_type='round_robin')

		self.cs.add_sequence(gs1)
		self.cs.add_sequence(gs2)

		total = 0
		for p in self.cs:
			total += 1

		# check we've seen the expected number...
		self.assertEqual(total, len(self.participant_group1) + len(self.participant_group2))

		gs3 = self.cs.GroupSequence(self.participant_group2, sequence_type='no_replace_sample', count=100)
		self.cs.add_sequence(gs3)
		total = 0
		for p in self.cs:
			total += 1

		# check we've seen the expected number...
		self.assertEqual(total, len(self.participant_group1) + len(self.participant_group2) + 100)

	def test_multi_loop_scenario(self):
			# Participants
		p1 = ConversationParticipant('David')
		p1.personality = 'a huge Star Wars fan, who knows everything about the franchise and thinks its the greatest, has a great sence of humour and is sarcastic about other franchises'

		p2 = ConversationParticipant('Sally')
		p2.personality = 'a huge Marvel fan, loves super heros and has seen every film, likes winding up fans of other franchises'

		p3 = ConversationParticipant('Louise')
		p3.personality = """a well respecteed and balanced discussion facilitator with no particular point of view on the theory-of-mind, who summerises key points of the conversation so far
										and then asks a brief insightful question of the other participants"""	

		# Sequence Groups
		sequencer = ConversationSequencer()
		g1 = sequencer.GroupSequence([p1, p2], sequence_type='round_robin', count=6)
		g2 = sequencer.GroupSequence([p3], sequence_type='round_robin', count=1)

		# Overall sequence
		sequencer.add_sequence(g1)
		sequencer.add_sequence(g2)
		sequencer.add_sequence(g1)
		sequencer.add_sequence(g1)
		sequencer.add_sequence(g2)
		
		full_list = []
		for p, conv_type, conv_stage in sequencer:
			full_list.append(p.participant_name)
			self.assertEqual(conv_type,'default_conversation')
			self.assertEqual(conv_stage,'default_stage')


		expected_list = ['David', 'Sally', 'David', 'Sally','David', 'Sally', 
						 'Louise',
						 'David', 'Sally', 'David', 'Sally','David', 'Sally',
						 'David', 'Sally', 'David', 'Sally','David', 'Sally',
						 'Louise']


		self.assertEqual(full_list,expected_list)

	def test_llm_brief(self):
		p1 = ConversationParticipant('David')
		p1.add_llm_briefing('a', 'b', 'c')

		sequencer = ConversationSequencer()
		s1 = sequencer.GroupSequence([p1],sequence_type='round_robin', conversation_type='a', conversation_stage='b', count=1)

		sequencer.add_sequence(s1)

		for stage in sequencer:
			participant, conv_type, conv_stage = stage
			self.assertEqual(participant.participant_name,'David')
			self.assertEqual(conv_type,'a')
			self.assertEqual(conv_stage,'b')

			brief = participant.get_llm_briefing(conv_type,conv_stage)
			self.assertEqual(brief,'c')


