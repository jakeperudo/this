import gym
from gym.spaces import Discrete
from gym.spaces import Tuple
import random
import numpy as np

from gym_perudo.envs.player import BotPlayer
from gym_perudo.envs.player import StupidPlayer
from gym_perudo.envs.player import SemiRandomPlayer
from gym_perudo.envs.player import AIPlayer
import itertools

x = [1, 2, 3, 4, 5, 6]
Dict = [(0,)]
for i in range(1,6):
    Dict += [p for p in itertools.combinations_with_replacement(x, i)]


class PerudoEnv(gym.Env):

    def __init__(self):
        self.action_space = Discrete(151)
        self.observation_space = Tuple((Discrete(151), Discrete(26), Discrete(462)))

        self.players = []
        self.render = False
        self.AIturn = False
        self.dudo = False
        self.done = False
        self.action = 0
        self.reward = 0

        self.round = 0
        self.previous_round = 0

        self.current_player = None
        self.next_player = None

        self.previous_bet = 0
        self.current_bet = 0
        self.next_bet = 0

        self.remaining_dice = 0
        self.AI_dice = 0

    def step(self, action):

        self.reward = 0
        self.AIturn = False
        self.dudo = False

        while len(self.players) > 1:

            if self.dudo == True:
                self.AIturn = False
                self.dudo = False
                return self.get_obs(), self.reward, self.done, self.AIturn, action

            if self.first_bet == 0:
                self.current_bet = self.current_player.make_bet(self.first_bet, action)

                if self.invalidmove(self.current_player, self.current_bet, self.next_bet) == True:
                    self.reward = -5
                    if self.render == True:
                        bet_quantity, bet_value = self.bet_decoder(self.next_bet)
                        print('{} tried an incorrect play with {}x{}'.format(self.current_player.name, bet_quantity, bet_value))
                    self.ob_bet = self.first_bet
                    self.AIturn = True
                    return self.get_obs(), self.reward, self.done, self.AIturn, action

                self.first_bet = 1
                self.previous_bet = 0

            while self.first_bet != 0:

                if self.round > self.previous_round:
                    if self.render == True:
                        print(' ')
                        print('Round {}'.format(self.round))
                    for player in self.players:
                        player.roll_dice()
                    for player in self.players:
                        if player.name == 'Bob':
                            self.AI_dice = self.dice_encoder(player)
                    self.remaining_dice -= 1
                    self.previous_round = self.round

                if self.render == True:
                    bet_quantity, bet_value = self.bet_decoder(self.current_bet)
                    print('{} calls {} x {}'.format(self.current_player.name, bet_quantity, bet_value))

                self.next_player = self.get_next_player(self.current_player)
                self.next_bet = self.next_player.make_bet(self.current_bet, action)

                if self.invalidmove(self.next_player, self.current_bet, self.next_bet) == True:
                    self.reward = -5
                    if self.render == True:
                        bet_quantity, bet_value = self.bet_decoder(self.next_bet)
                        print('{} tried an incorrect play with {}x{}'.format(self.next_player.name, bet_quantity, bet_value))
                    self.ob_bet = self.current_bet
                    self.AIturn = True
                    return self.get_obs(), self.reward, self.done, self.AIturn, action


                if self.next_bet == 0: #if dudo is called
                    self.run_dudo(self.current_player, self.current_bet)
                    action = self.action
                    self.first_bet = 0
                    self.previous_round = self.round
                    self.round +=1
                    self.dudo = True

                    if self.AIturn == True:
                        return self.get_obs(), self.reward, self.done, self.AIturn, action
                    else:
                        continue

                else:
                    if self.current_player.name == 'Bob':
                        self.ob_bet = self.previous_bet
                        self.AIturn = True
                        self.reward = 1

                        self.previous_bet = self.current_bet
                        self.previous_player = self.current_player
                        self.current_player = self.next_player
                        self.current_bet = self.next_bet

                        return self.get_obs(), self.reward, self.done, self.AIturn, action

                    else:
                        self.previous_bet = self.current_bet
                        self.previous_player = self.current_player
                        self.current_player = self.next_player
                        self.current_bet = self.next_bet

        else:
            self.done = True
            return self.get_obs(), self.reward, self.done, self.AIturn, action


    def reset(self):
        self.done = False
        self.round = 1
        self.previous_round = 0
        self.first_bet = 0
        self.reward = 0
        self.ob_bet = 0
        self.AIturn = False

        self.players = [AIPlayer(
                            name = 'Bob',
                            dice_number = 5,
                            game = self),
                        BotPlayer(
                            name = 'Chris',
                            dice_number = 5,
                            game = self),
                        BotPlayer(
                            name = 'Chenyu',
                            dice_number = 5,
                            game = self),
                        BotPlayer(
                            name = 'Kexin',
                            dice_number = 5,
                            game = self),
                        BotPlayer(
                            name = 'Jake',
                            dice_number = 5,
                            game = self)]

        for player in self.players:
            player.roll_dice()
        self.current_player = self.players[random.randint(0,len(self.players)-1)]
        self.remaining_dice = len(self.players)*5
        for player in self.players:
            if player.name == 'Bob':
                self.AI_dice = self.dice_encoder(player)
        return self.get_obs()


    ##game functions##

    def get_next_player(self, player):
        return self.players[(self.players.index(player) + 1) % len(self.players)]

    def get_previous_player(self, player):
        return self.players[(self.players.index(player) - 1) % len(self.players)]

    def run_dudo(self, player, bet):
        value = (bet % 6)
        if value == 0:
            value = 6
        quantity = ((bet - value)//6) + 1
        dice_count = self.count_dice(value)

        if dice_count >= quantity:
            if self.render == True:
                print('{} called dudo wrong and loses a die'.format(self.next_player.name))
            if self.next_player.name == 'Bob':
                self.AIturn = True
                self.reward = -2
                self.ob_bet = self.current_bet
                self.action = 0

            if self.current_player.name == 'Bob':
                self.AIturn = True
                self.reward = 2
                self.ob_bet = self.previous_bet
                self.action = self.current_bet

            self.remove_die(self.next_player)

        else:
            previous_player = self.get_previous_player(player)
            if self.render == True:
                print('{} called dudo right, {} loses a die'.format(self.next_player.name, self.current_player.name))
            if self.next_player.name == 'Bob':
                self.AIturn = True
                self.reward = 2
                self.ob_bet = self.current_bet
                self.action = 0

            if self.current_player.name == 'Bob':
                self.AIturn = True
                self.reward = -2
                self.ob_bet = self.previous_bet
                self.action = self.current_bet
            self.remove_die(self.current_player)

    def remove_die(self, player):
        player.dice.pop()
        if len(player.dice) == 0:
            self.current_player = self.get_next_player(player)
            if self.render == True:
                print('{} is out!'. format(player.name))
            self.players.remove(player)

    def count_dice(self, value):
        number = 0
        for player in self.players:
            number += player.count_dice(value)
        return number

    def get_obs(self):
        return self.ob_bet, self.remaining_dice, self.AI_dice

    def invalidmove(self, player, current_bet, next_bet):
        if player.name == 'Bob':
            if next_bet == 0:
                if current_bet == 0:
                    return True
                else:
                    return False
            else:
                if next_bet <= current_bet:
                    return True
                else:
                    return False

    def bet_decoder(self, bet):
        bet_value = (bet % 6)
        if bet_value == 0:
            bet_value = 6
        bet_quantity = ((bet - bet_value)//6) + 1
        return bet_quantity, bet_value

    def dice_encoder(self, player):
        current_dice = []
        for dice in player.dice:
            current_dice.append(dice.value)
        return Dict.index(tuple(current_dice))
