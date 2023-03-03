import unittest
import conversation_turn.conversation_turn_service as cts       


class TestConversionTurnService(unittest.TestCase):
	def setUp(self):
		broker_config = {'rabbitmq': {'host':'localhost'}} 
		self.cts = cts.ConversationTurnService(broker_config)





	def test_build_complete_utterance(self):

		utterance_id = self.cts.utterance_cache.create()

		# test basic substitutions
		utterance_elements = {'main':'Main utterance element with <{personality}> and <{query}>',
							  'personality':'I am a <{life_stage}> clown',
							  'query':'What is the best drink for a <{life_stage}>',
							  'life_stage':'adult'}

		self.cts.utterance_cache.add_recieved_data(utterance_id,utterance_elements)

		utterance = self.cts.build_complete_utterance(utterance_id)
		print(utterance)
		self.assertEqual(utterance, 'Main utterance element with I am a adult clown and What is the best drink for a adult')

		# test missing substitutions
		utterance_elements = {'main':'Main utterance element with <{personality}> and <{query}>',
							  'personality':'I am a <{life_stage}> clown',
							  'query':'What is the best drink for a <{life_stage}>',
							  'life_stage':'adult of sex <{sex}>'}

		self.cts.utterance_cache.add_recieved_data(utterance_id,utterance_elements)

		with self.assertRaises(ValueError) as ve:
			utterance = self.cts.build_complete_utterance(utterance_id)
		self.assertEqual("Missing tokens in data set: {'sex'}", str(ve.exception))

		# test circular references
		utterance_elements = {'main':'Main utterance element with <{personality}> and <{query}>',
							  'personality':'I am a <{life_stage}> clown',
							  'query':'What is the best drink for a <{life_stage}>',
							  'life_stage':'adult with personality <{personality}>'}

		self.cts.utterance_cache.add_recieved_data(utterance_id,utterance_elements)
		with self.assertRaises(ValueError) as ve:
			utterance = self.cts.build_complete_utterance(utterance_id)
		self.assertEqual("Max depth exceeded, possible circular dependencies, remaining unresolved tokens: {'personality'}", str(ve.exception))
