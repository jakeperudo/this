import random
from math import floor
from math import ceil
from random import randrange
import numpy as np

class BetException(Exception):
	pass


class InvalidBetException(BetException):
	#Raised when a bet does not have either a higher quantity or a higher value
	pass


class Bet(object):
	def __init__(self, bet):
		self.current_bet = bet
	def __repr__(self):
		return 'bet'

def create_bet(proposed_bet, last_bet, player, game):
	if last_bet:
		if proposed_bet <= last_bet:
			raise InvalidBetException()
		return proposed_bet
	else:
		return proposed_bet


class Die(object):
	def __init__(self):
		self.roll()
	def roll(self):
		self.value = randrange(1,7)


class Player(object):

	def __init__(self, name, dice_number, game):
		self.name = name
		self.game = game
		self.dice = []
		for i in range(0, dice_number):
			self.dice.append(Die())

	def make_bet(self, current_bet, action):
		pass

	def roll_dice(self):
		for die in self.dice:
			die.roll()
		self.dice = sorted(self.dice, key=lambda die: die.value)

	def count_dice(self, value):
		number = 0
		for die in self.dice:
			if die.value == value:
				number += 1
		return number

class BotPlayer(Player):

	def make_bet(self, current_bet, action):

		total_dice_estimate = self.game.remaining_dice

		if current_bet == 0:
			value = randrange(1,7) #random.choice(self.dice).value
			quantity_limit = (total_dice_estimate - len(self.dice))//6
			quantity = random.randrange(1, 3)
			bet = 6*(quantity-1) + value
			bet = create_bet(bet, current_bet, self, self.game)
			return bet

		else:
			value = (current_bet % 6)
			if value == 0:
				value = 6
			quantity = ((current_bet - value)//6) + 1
			limit = ceil(total_dice_estimate/6.0) + random.randrange(0, ceil(total_dice_estimate/4.0))

			if quantity >= limit:
				bet = 0
				return bet
			else:
				bet = None
				while bet is None:
					value = randrange(1,7)  #random.choice(self.dice).value
					quantity = quantity + random.randrange(0, 2)
					bet = 6*(quantity-1) + value
					try:
						bet = create_bet(bet, current_bet, self, self.game)
					except BetException:
						bet = None

				value = (bet % 6)
				if value == 0:
					value = 6
				quantity = ((bet - value)//6) + 1
			return bet


class SemiRandomPlayer(Player):

	def make_bet(self, current_bet, action):

		if current_bet > 145:
			bet = 0
			return bet
		else:
			bet = None
			while bet is None:
				bet = random.randrange(1,151)
				try:
					bet = create_bet(bet, current_bet, self, self.game)
				except BetException:
					bet = None
		return bet


class StupidPlayer(Player):

	def make_bet(self, current_bet, action):

		if np.random.uniform(0,1) < 0.2:
			bet = 0
		else:
			bet = current_bet + randrange(1,7)
			if bet > 140:
				bet = 0

		return bet


class AIPlayer(Player):

	def make_bet(self, current_bet, action):
		value = (action % 6)
		if value == 0:
			value = 6
		quantity = ((action - value)//6) + 1
		#print('AI ' + str(quantity) + ' x ' + str(value))
		return action
