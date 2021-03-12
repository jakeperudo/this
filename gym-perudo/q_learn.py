import gym

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import gym_perudo

env = gym.make('perudo_game-v0')

gamma = 0.95
alpha = 0.05
n_eps = 10000

epsilon_max = 1.0
epsilon_min = 0.001
epsilon_decay = 0.99999
epsilon_step = (epsilon_max - epsilon_min) / n_eps

q_table = np.zeros([env.observation_space[0].n, env.observation_space[1].n, env.observation_space[2].n, env.action_space.n])
epsilon = 0.1
game = 0
winner_count = []
env.render = True
reward_list = []
ep_reward = []

for _ in range(n_eps):

    ob = env.reset()
    done = False
    game +=1
    if env.render == True:
        print(' ')
        print(' ')
        print('Game {}'.format(game))
    game_reward = 0

    while not done:

        if np.random.uniform(0,1) >= epsilon:
            a = np.argmax(q_table[ob])
        else:
            a = env.action_space.sample()


        new_ob, r, done, AIturn, a = env.step(a)
        if done == True:
            continue
        if AIturn == True:
            if env.render == True:
                print('Action {}, with ob {}, and reward {}'.format(a, new_ob, r))
            q_table[ob][a] += alpha * (r + gamma * np.max(q_table[new_ob]) - q_table[ob][a])
            ob = new_ob

            game_reward += r
            #epsilon *= epsilon_decay
            #epsilon = max(epsilon-epsilon_step, epsilon_min)


    winner_count.append(env.players[0].name)
    if env.players[0].name == 'Bob':
        game_reward +=10
    ep_reward.append(game_reward)
    #epsilon *= epsilon_decay
    #epsilon = max(epsilon-epsilon_step, epsilon_min)
    #final_reward = r
    #ep_reward.append(final_reward)

#print(reward_list)


wins = 0
Z = []
games = 0
for player in winner_count:
    if player == 'Bob':
        wins +=1
    Z.append(wins)
#print(winner_count)


#print('Q table \n', q_table)
X = range((n_eps))

plt.plot(X, Z)


def smooth_reward(ep_reward, smooth_over):
    smoothed_r = []
    for ii in range(smooth_over, len(ep_reward)):
        smoothed_r.append(np.mean(ep_reward[ii-smooth_over:ii]))
    return smoothed_r

plt.plot(smooth_reward(ep_reward, 20))
plt.title('smoothed reward')
plt.show()
