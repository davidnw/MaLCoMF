# This is a very basic service to experiment with LLM 'personalities' talking to each other
# 
# Basically each member of the conversation is a facard for an LLM, injecting personality elements
# into the prompts
# 
# The service manages the sequencing and distribution of the conversation between the participants
# 
from group_conversation.conversation_participant import ConversationParticipant
from group_conversation.conversation_sequencer import ConversationSequencer
import logging
import datetime

class GroupConversation:
	def __init__(self, conversation_name, max_utterances=50):
		self.participants = {}
		self.conversation = []
		self.conversation_name = conversation_name
		self.max_utterances = 50

	def add_participant(self, name, participant):
		self.participants[name] = participant
		logging.info(f'{name} added to {self.conversation_name}')

	def remove_participant(self, name):
		self.participants.pop(name, None)
		logging.info(f'{name} removed from {self.conversation_name}')

	def set_conversation_sequencer(self, conversation_sequencer):
		self.conversation_sequencer = conversation_sequencer

	def seed_conversation(self, name, conversation_seed):
		# one of the participants starts the conversation 
		self.add_conversation_utterance(name, conversation_seed)
		logging.info(f'{self.conversation_name} seeded with {conversation_seed}')

	def add_conversation_utterance(self, name, utterance, conversation_type='default_conversation', conversation_stage='default_stage', llm_briefing=''):
		timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
		record = {'time': timestamp, 
				'participant':name, 
				'utterance':utterance, 
				'conversation_type':conversation_type, 
				'conversation_stage':conversation_stage,
				'llm_briefing':llm_briefing}
		self.conversation.append(record)
		logging.info(f'{record} added to {self.conversation_name}')

	def conversation_text(self, include_time=True):
		text = ''
		for record in self.conversation:
			if include_time:
				utterance_text = f"{record['time']} {record['participant']} : {record['utterance']}\n"
			else:
				utterance_text = f"{record['participant']} : {record['utterance']}\n"

			text = text + utterance_text

		return text

	def formatted_conversation_record(self):
		txt = ''
		for utterance in self.conversation:
			txt += f"\n{utterance['time']} participant: {utterance['participant']} Conversation Type: {utterance['conversation_type']} Conversation Stage: {utterance['conversation_stage']}"
			txt += f"\nBriefing:\n{utterance['llm_briefing']}\n"
			txt += f"\nUtterance:\n{utterance['utterance']}\n"
		return txt

	def next_utterance(self, name):
		participant = self.participants[name]
		utterance_from_participant = participant.add_to_conversation(self.conversation_text(include_time=False))
		self.add_conversation_utterance(name, utterance_from_participant)
		return utterance_from_participant

	def next_utterance2(self, participant, add_to_conversation=True, conversation_type='default_conversation', conversation_stage='default_stage'):
		
		utterance_from_participant, llm_briefing = participant.utterance_for_conversation(self.conversation_text(include_time=False), 
			conversation_type=conversation_type, 
			conversation_stage=conversation_stage)

		if add_to_conversation:
			self.add_conversation_utterance(participant.participant_name, utterance_from_participant, conversation_type=conversation_type, conversation_stage=conversation_stage, llm_briefing=llm_briefing)

		return utterance_from_participant,llm_briefing

	def run(self):
		while len(self.conversation) < self.max_utterances:
			for key in self.participants:
				utterance = self.next_utterance(key)
				print(f'{key} says : {utterance}\n')


	def run2(self):
		conversation_sequence = iter(self.conversation_sequencer)
		for next_participants, conv_type, conv_stage in conversation_sequence:

			# The next participants may be a single value or a list
			# a list indicates they should be asked in parallel for their
			# utterances, which are added to the conversation at once
			# i.e everyone is commenting on something at the same time
			# e.g. like an initail brainstorm
			# Note: This isn't done litterally in parrallel we're just
			# asking each participant for their comment before updating the 
			# conversation...
			if isinstance(next_participants, list):
				parrallel_utterances = list()
				for p in next_participants:
					utterance, llm_briefing = self.next_utterance2(p, add_to_conversation=False, conversation_type=conv_type, conversation_stage=conv_stage)
					parrallel_utterances.append({'name':p.participant_name,'utterance':utterance, 'briefing':llm_briefing})
				# now add all utterances to the conversation at once
				for u in parrallel_utterances:
					self.add_conversation_utterance(u['name'],u['utterance'], llm_briefing=u['briefing'], conversation_type=conv_type, conversation_stage=conv_stage)
					print(f"{u['name']} says : {u['utterance']}\n")
			else:
				# single participant
				utterance = self.next_utterance2(next_participants, add_to_conversation=True, conversation_type=conv_type, conversation_stage=conv_stage)
				print(f'{next_participants.participant_name} says : {utterance}\n')


	@staticmethod
	def conversation_from_config(config):
		conversation = GroupConversation(config['topic'])
		for participant_name in config['participants']:
			p = ConversationParticipant(participant_name)
			p.personality = config['participants'][participant_name]['personality']
			conversation.add_participant(participant_name,p)
		conversation.seed_conversation(config['seed']['who'],config['seed']['text'])

		return conversation


def main():

	conversation1_config = {
		'topic':'Abortion debate',
		'participants':{
			'David':{'personality':'a polite, strict conservative'},
			'Sally':{'personality':'a polite, pro-choice liberal'},
			'Louise':{'personality':"""an excellent calm discussion facilitator, who summerises key points of the conversation so far
									and then asks a brief insightful question of the other participants"""}
		},
		'seed':{'who':'Louise','text':"""What are your points of view on the abortion debate? 
		Do you think there are any circumstances where it is the right thing to do?"""}
	}

	conversation2_config = {
		'topic':'Marvel vs. Star Wars',
		'participants':{
			'David':{'personality':'a huge Star Wars fan, who knows everything about the franchise and thinks its the greatest, has a great sence of humour and is sarcastic about other franchises'},
			'Sally':{'personality':'a huge Marvel fan, loves super heros and has seen every film, likes winding up fans of other franchises'},
			'Louise':{'personality':"""an excellent fun discussion facilitator, who summerises key points of the conversation so far
									and then asks a brief insightful question of the other participants often adds a joke to keep things light hearted"""}
		},
		'seed':{'who':'Louise','text':"""Star Wars is the original and best movie franchise. I know you agree!  Let's discuss!"""}
	}


	conversation3_config = {
		'topic':'Dualist vs. Materialist',
		'participants':{
			'David':{'personality':'a hugely experienced neuroscientist who has a strong materialist and reductionist view of the theory-of-mind. draws on cutting edge neuroscience experiements to make ones arguments'},
			'Charles':{'personality':'a very well respected neuroscience who has a deep understanding of the latest neuroscience experimental and thoretical work. Has a dualist view of the Theory of mind and uses experimental and philisophical knowledge to make ones arguments'},
			'Louise':{'personality':"""a well respecteed and balanced discussion facilitator with no particular point of view on the theory-of-mind, who summerises key points of the conversation so far
									and then asks a brief insightful question of the other participants, aims to close the debate after about 10 rounds of conversation"""}
		},
		'seed':{'who':'Louise','text':"""The theory-of-mind can be seen from a reductionist or dualist point of view. Let's discuss!"""}
	}


	converation = GroupConversation.conversation_from_config(conversation3_config)
	converation.run()


def main_with_sequencer():

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
	g1 = sequencer.GroupSequence([p1, p2], sequence_type='parallel', count=3)
	g2 = sequencer.GroupSequence([p3], sequence_type='round_robin', count=1)

	# Overall sequence
	sequencer.add_sequence(g1)
	sequencer.add_sequence(g2)
	sequencer.add_sequence(g1)
	sequencer.add_sequence(g2)
	
	conversation = GroupConversation('Marvel Discussion')
	conversation.set_conversation_sequencer(sequencer)

	conversation.seed_conversation('Louise', 'Star Wars vs Marvel Let\'s discuss!')

	conversation.run2()

	print(conversation.conversation_text(include_time=True))


def main_with_stages():

	brainstorm_participant_briefing = {
	'brainstorm':
		{
		'initial':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Add *3* initial ideas to the brainstorm as {name}.
		{name}:
		''',
		'positive_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Review and comment (be positive) on others ideas so far. {name}.
		{name}:
		''',
		'critical_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Review and comment on others ideas so far. Be polite, but identify any potential problems you see {name}.
		{name}:
		''',
		'final_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		It is coming to a close
		You are {personality}.
		Make your final points and identify your favorite idea{name}.
		{name}:
		'''
		}
	}


	brainstorm_facilitator_briefing = {
	'brainstorm':
		{
		'initial':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Summerise what's been contributed so far.  Then set some ground rules for a round of positive comments, where the participants comment on the ideas in a positive way
		{name}:
		''',
		'positive_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Summerise what's been contributed so far.  Then set some ground rules for a round of critical analysis comments, where the participants comment on any problems with the ideas in ideas in a constructive way
		{name}:
		''',
		'critical_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Summerise what's been contributed so far.  Then set some ground rules for a round of final comments from the participants, where the pick there favorite idea
		{name}:
		''',
		'final_analysis':
		'''
		You are {name}. You are participting in the above brainstorm.
		You are {personality}.
		Summerize the final output of the brainstorm and close the session
		{name}:
		'''
		}
	}

	def add_briefing_elements(participant, briefings_config):
		for conversation,v in briefings_config.items():
			for stage, briefing in v.items():
				participant.add_llm_briefing(conversation,stage,briefing)  

	# Participants
	p1 = ConversationParticipant('David')
	p1.personality = 'a product manager for a cake making company, you are keen to create profitable products'
	add_briefing_elements(p1,brainstorm_participant_briefing)

	p2 = ConversationParticipant('Sally')
	p2.personality = 'a marketing manager for a cake making company, you are keen that your products can be made to appeal to a wide audiance'
	add_briefing_elements(p2,brainstorm_participant_briefing)

	p3 = ConversationParticipant('Tom')
	p3.personality = 'a manufacturing production manager for a cake making company, you are keen that your products can be sourced and maufactured as efficiently as possible'
	add_briefing_elements(p3,brainstorm_participant_briefing)

	p4 = ConversationParticipant('John')
	p4.personality = """a well respecteed and balanced discussion facilitator with no particular point of view on cake production, polite, calm and enquiring"""
	add_briefing_elements(p4,brainstorm_facilitator_briefing)

	# Sequence Groups
	sequencer = ConversationSequencer()
	step1 = sequencer.GroupSequence([p1, p2, p3], sequence_type='parallel', count=1, conversation_type='brainstorm', conversation_stage='initial')
	step2 = sequencer.GroupSequence([p4], sequence_type='round_robin', count=1, conversation_type='brainstorm', conversation_stage='initial')

	step3 = sequencer.GroupSequence([p1, p2, p3], sequence_type='parallel', count=1, conversation_type='brainstorm', conversation_stage='positive_analysis')
	step4 = sequencer.GroupSequence([p1, p2, p3], sequence_type='no_replace_sample', count=3, conversation_type='brainstorm', conversation_stage='positive_analysis')
	step5 = sequencer.GroupSequence([p4], sequence_type='round_robin', count=1, conversation_type='brainstorm', conversation_stage='positive_analysis')

	step6 = sequencer.GroupSequence([p1, p2, p3], sequence_type='parallel', count=1, conversation_type='brainstorm', conversation_stage='critical_analysis')
	step7 = sequencer.GroupSequence([p1, p2, p3], sequence_type='no_replace_sample', count=3, conversation_type='brainstorm', conversation_stage='critical_analysis')
	step8 = sequencer.GroupSequence([p4], sequence_type='round_robin', count=1, conversation_type='brainstorm', conversation_stage='critical_analysis')

	step9 = sequencer.GroupSequence([p1, p2, p3], sequence_type='parallel', count=1, conversation_type='brainstorm', conversation_stage='final_analysis')
	step10 = sequencer.GroupSequence([p1, p2, p3], sequence_type='no_replace_sample', count=3, conversation_type='brainstorm', conversation_stage='final_analysis')
	step11 = sequencer.GroupSequence([p4], sequence_type='round_robin', count=1, conversation_type='brainstorm', conversation_stage='final_analysis')

	# Overall sequence
	sequencer.add_sequence(step1)
	sequencer.add_sequence(step2)
#	sequencer.add_sequence(step3)
	sequencer.add_sequence(step4)
	sequencer.add_sequence(step5)
#	sequencer.add_sequence(step6)
	sequencer.add_sequence(step7)
	sequencer.add_sequence(step8)
	sequencer.add_sequence(step9)
#	sequencer.add_sequence(step10)
	sequencer.add_sequence(step11)
	
	conversation = GroupConversation('Cake Brainstorm')
	conversation.set_conversation_sequencer(sequencer)

	conversation.seed_conversation('John', 'We are brainstorming ideas for a new cake product... lets begin...')

	# for step in sequencer:
	# 	p, conv_type, conv_stage = step

	# 	print(f'Type: {conv_type} Stage: {conv_stage} participants: {p}')
	# 	if not isinstance(p, list):
	# 		print(f'{p.participant_name} : {p.get_llm_briefing(conv_type,conv_stage)}')


	conversation.run2()

	print(conversation.formatted_conversation_record())
	logging.info(f'Full conversation\n\n{conversation.formatted_conversation_record()}\n\n')


if __name__ == '__main__':

	# dump the logging in a file...
	# Configure logging to write to a file
	log_file = "group_conversation.log"
	file_handler = logging.FileHandler(log_file)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(process)d %(filename)s:%(lineno)d %(threadName)s: %(message)s'))
	root_logger = logging.getLogger()
	root_logger.addHandler(file_handler)
	root_logger.setLevel(logging.INFO)

	main_with_stages()

