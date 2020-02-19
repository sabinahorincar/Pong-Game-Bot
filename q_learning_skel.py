
# General imports
from copy import copy
from random import choice, random
from argparse import ArgumentParser
from time import sleep
import numpy

# PYGAME
import pygame, sys
from pygame.locals import *

# Game functions
from pong import ( get_initial_state,       # get initial state from file
						  get_legal_actions,  # get the legal actions in a state
						  is_final_state,         # check if a state is terminal
						  apply_action,       # apply an action in a given state
						  display_state,	# display the current state
						  __deserialize_state,
						  __get_position)            

def print_pygame(state, train_ep):
	# PYGAME
	paddle_size = 3
	scale = 30
	
	state_deserialized = __deserialize_state(state)
	
	board_width = numpy.shape(state_deserialized)[1]
	board_height = numpy.shape(state_deserialized)[0]

	ball_raw, ball_column = __get_position(state_deserialized, "o")

	# Take agent first "|"
	first_player_start = 0
	for line in range(numpy.shape(state_deserialized)[0]):
		if state_deserialized[line][0] == "|":
			first_player_start = line
			break
	# Take enemy first "|"
	second_player_start = 0
	for line in range(numpy.shape(state_deserialized)[0]):
		if state_deserialized[line][numpy.shape(state_deserialized)[1]-1] == "|":
			second_player_start = line
			break
	
	window_width = (board_width - 1) * scale
	window_height = board_height * scale

	agent_x, agent_y = 0, first_player_start + paddle_size /2 + 2
	enemy_x, enemy_y = board_width - 1, second_player_start + paddle_size/2 + 2

	# Draw screen
	pygame.init()
	screen = pygame.display.set_mode((window_width, window_height + 200))  

	screen.fill((0, 0, 102))

	# Draw ball
	pygame.draw.rect(
		screen, (255, 255, 255),
		[ball_column * scale, ball_raw * scale, scale, scale]
	)

	# Draw agent
	pygame.draw.polygon(
		screen, (255, 255, 255),
		[
			[agent_x * scale, (agent_y - paddle_size) * scale],
			[(agent_x + 1) * scale, (agent_y - paddle_size) * scale], 
			[(agent_x + 1) * scale, agent_y * scale],
			[agent_x * scale, agent_y * scale],
		],
		0
	)

	# Draw enemy
	pygame.draw.polygon(
		screen,
		(255, 255, 255),
		[
			[(enemy_x - 1) * scale, (enemy_y - paddle_size) * scale],
			[enemy_x * scale, (enemy_y - paddle_size) * scale], 
			[enemy_x * scale, enemy_y * scale],            
			[(enemy_x - 1) * scale, enemy_y * scale],
		],
		0
	)
	
	very_small = pygame.font.SysFont("Times New Roman", int(scale))
	# Draw line
	pygame.draw.line(screen, (204, 204, 225), [1, window_height - scale],\
									[window_width, window_height - scale], 1)

	pygame.draw.line(screen, (204, 204, 225), [1, scale],\
									[window_width, scale], 1)
	# Draw text
	ag = very_small.render("Agent strategy: " + str(args.agent), 1, (255, 204, 153))
	screen.blit(ag, (0, -25 + window_height))           
	
	enem = very_small.render("Adversary strategy: " + str(args.enemy), 1, (255, 204, 153))
	screen.blit(enem, (0, 10 + window_height))

	learning_rate = very_small.render("Learning_rate: " + str(args.learning_rate), 1, (255, 204, 153))
	screen.blit(learning_rate, (0, 45 + window_height))

	discount = very_small.render("Discount: " + str(args.discount), 1, (255, 204, 153))
	screen.blit(discount, (0, 80 + window_height))

	epsilon = very_small.render("Epsilon: " + str(args.epsilon), 1, (255, 204, 153))
	screen.blit(epsilon, (0, 110 + window_height))

	# Draw only on verbose
	if train_ep != 0:
		episodee = very_small.render("Episode nr " + str(train_ep), 1, (255, 204, 153))
		screen.blit(episodee, (0, 140 + window_height))  
    			
	pygame.display.update()

def epsilon_greedy(Q, state, legal_actions, epsilon):
	# TODO (2) : Epsilon greedy
	neexplored = []
	for action in legal_actions:
		if (state, action) not in Q:
			neexplored.append(action)
	if neexplored != []:
		return choice(neexplored)

	prob = random()
	if prob < epsilon:
		return choice(legal_actions)
	else:
		return best_action(Q, state, legal_actions)

def best_action(Q, state, legal_actions):
	# TODO (3) : Best action
	maxim = -999999
	b_action = None
	for action in legal_actions:
		if (state, action) not in Q:
			Q[(state, action)] = 0
		if Q.get((state, action)) > maxim:
			maxim = Q.get((state, action))
			b_action = action
	return b_action

def reverse_state(state):
	line = ""
	len_raw = 0
	state_enemy = ""
	for s in state:
		if s != '\n':
			line += s
			if len(line) > len_raw:
				len_raw = len(line)				
		else:
			state_enemy += line[::-1]
			state_enemy += "\n"
			line = ""

	if len(state_enemy) + len_raw == len(state):
		state_enemy += line[::-1]

	return state_enemy

def q_learning(args):
	Q = {}
	train_scores = []
	eval_scores = []
	action_enemy = ""

	# for each episode ...
	for train_ep in range(1, args.train_episodes + 1):

		 # ... get the initial state,
		score = 0
		state = get_initial_state(args.map_file)

		# display current state and sleep
		if args.verbose:
			display_state(state); sleep(args.sleep)

		step = 1000
		# while current state is not terminal
		while not is_final_state(state, score):
			if step < 0:
				break
			step -= 1

			# choose one of the legal actions
			actions = get_legal_actions(state)

			# ENEMY GREEDY
			if args.enemy == "greedy":
				state_enemy = reverse_state(state)
				action_enemy = best_action(Q, state_enemy, actions)

			# AGENT
			if args.agent == "e-greedy":
				action = epsilon_greedy(Q, state, actions, args.epsilon)
			if args.agent == "random":
				action = choice(actions)
			if args.agent == "greedy":
				action = epsilon_greedy(Q, state, actions, args.epsilon)

			# apply action and get the next state and the reward
			next_state, reward, msg = apply_action(state, action, args.enemy, action_enemy)
			score += reward

			# TODO (1) : Q-Learning
			qinit_state = Q.get((state, action))
			if qinit_state == None:
				qinit_state = 0

			max_a = best_action(Q, next_state, get_legal_actions(next_state))
			Q[(state, action)] = qinit_state + args.learning_rate * \
				(reward + args.discount * Q[(next_state, max_a)] - qinit_state)

			# display current state and sleep
			if args.verbose:
				print(msg); display_state(state); print_pygame(state, train_ep); sleep(args.sleep)

			# current state update
			state = next_state
			
		print("Episode %6d / %6d" % (train_ep, args.train_episodes))

		train_scores.append(score)

		# evaluate the greedy policy
		if train_ep % args.eval_every == 0:
			avg_score = .0
			args.epsilon -= 0.025
			# TODO (4) : Evaluate
			if args.epsilon < 0.0:
				args.epsilon = 0.0

			for eval_ep in range(args.eval_every):
				s = get_initial_state(args.map_file)

				step = 1000
				while not is_final_state(s, avg_score):
					if step < 0:
						break
					step -= 1
					
					action = best_action(Q, s, get_legal_actions(s))

					if args.enemy == "greedy":
						state_enemy = reverse_state(s)
						action_enemy = best_action(Q, state_enemy, actions)

					s, reward, msg = apply_action(s, action, args.enemy, action_enemy)
					avg_score += reward

			eval_scores.append(avg_score/args.eval_every)


	# FINAL SHOW --------------------------------------------------------------
	if args.final_show:
		state = get_initial_state(args.map_file)
		final_score = 0

		step = 1000
		while not is_final_state(state, final_score):
			if step < 0:
				print " It's a draw "
				print "*******************************"
				break
			step -= 1

			action = best_action(Q, state, get_legal_actions(state))
			
			if args.enemy == "greedy":
				state_enemy = reverse_state(state)
				action_enemy = best_action(Q, state_enemy, actions)


			state, reward, msg = apply_action(state, action, args.enemy, action_enemy)
			final_score += reward
			print(msg); display_state(state); sleep(args.sleep)
	
	# FINAL SHOW PYGAME ---------------------------------------------------------
	if args.final_show_pygame:

		state = get_initial_state(args.map_file)
		final_score = 0

		step = 1000
		while not is_final_state(state, final_score):
			if step < 0: 
				print " It's a draw "
				print "*******************************"
				break
			step -= 1

			action = best_action(Q, state, get_legal_actions(state))
			
			if args.enemy == "greedy":
				state_enemy = reverse_state(state)
				action_enemy = best_action(Q, state_enemy, actions)

			state, reward, msg = apply_action(state, action, args.enemy, action_enemy)
			final_score += reward
			print(msg)

			# PYGAME
			print_pygame(state, 0)

			display_state(state);
			sleep(args.sleep) 

	if args.plot_scores:
		from matplotlib import pyplot as plt
		import numpy as np
		plt.xlabel("Episode")
		plt.ylabel("Average score")
		plt.plot(
			np.linspace(1, args.train_episodes, args.train_episodes),
			np.convolve(train_scores, [0.2,0.2,0.2,0.2,0.2], "same"),
			linewidth = 1.0, color = "blue"
		)
		plt.plot(
			np.linspace(args.eval_every, args.train_episodes, len(eval_scores)),
			eval_scores, linewidth = 2.0, color = "red"
		)
		plt.show()

if __name__ == "__main__":
	parser = ArgumentParser()
	# Input file
	parser.add_argument("--map_file", type = str, default = "mini_map",
						help = "File to read map from.")
	# Meta-parameters
	parser.add_argument("--learning_rate", type = float, default = 0.1,
						help = "Learning rate")
	parser.add_argument("--discount", type = float, default = 0.99,
						help = "Value for the discount factor")
	parser.add_argument("--epsilon", type = float, default = 0.05,
						help = "Probability to choose a random action.")
	# Training and evaluation episodes
	parser.add_argument("--train_episodes", type = int, default = 100,
						help = "Number of episodes")
	parser.add_argument("--eval_every", type = int, default = 10,
						help = "Evaluate policy every ... games.")
	parser.add_argument("--eval_episodes", type = float, default = 10,
						help = "Number of games to play for evaluation.")
	# Display
	parser.add_argument("--verbose", dest="verbose",
						action = "store_true", help = "Print each state")
	parser.add_argument("--plot", dest="plot_scores", action="store_true",
						help = "Plot scores in the end")
	parser.add_argument("--sleep", type = float, default = 0.1,
						help = "Seconds to 'sleep' between moves.")
	parser.add_argument("--final_show", dest = "final_show",
						action = "store_true",
						help = "Demonstrate final strategy.")
	# ENEMY
	parser.add_argument("--enemy", type = str, default = "almost_perfect",
						help = "random or almost_perfect or greedy enemy")
	# AGENT
	parser.add_argument("--agent", type = str, default = "e-greedy",
						help = "random or greedy or e-greedy agent")
	# Display PYGAME
	parser.add_argument("--final_show_pygame", dest = "final_show_pygame",
						action = "store_true",
						help = "Demonstrate final strategy.")
	args = parser.parse_args()

	q_learning(args)
