
from copy import copy
from random import choice, random
import numpy as np 

ACTIONS = ["UP", "DOWN", "STAY"]
ACTION_EFFECTS = {
	"UP": (-1,0),
	"DOWN": (1,0),
	"STAY": (0,0)
}

MOVE_REWARD = 0.0
WIN_REWARD = 1.0
LOSE_REWARD = -1.0

direction = "n-v"

# Functions to serialize / deserialize game states
def __serialize_state(state):
	return "\n".join(map(lambda row: "".join(row), state))

def __deserialize_state(str_state):
	return list(map(list, str_state.split("\n")))

## Return the initial state of the game
def get_initial_state(map_file_path):
	with open(map_file_path) as map_file:
		initial_str_state = map_file.read().strip()
	return initial_str_state

## Return the available actions in a given state
def get_legal_actions(str_state):
	return copy(ACTIONS)

## Get the coordinates of an actor
def __get_position(state, marker):
	for row_idx, row in enumerate(state):
		if marker in row:
			return row_idx, row.index(marker)
	return -1, -1

## Check if is a final state
def is_final_state(str_state, score):
	state = __deserialize_state(str_state)
	g_row, g_col = __get_position(state, "o")

	if g_col == 0 or g_col == np.shape(state)[1]-1:
		return True
	elif g_row >= 0 and g_col > 0 and g_col < np.shape(state)[1]-1:
		return False
	return None
	
## Check if the given coordinates are valid (on map and not a wall)
def __is_valid_cell(state, row, col):
	return row >= 0 and row < len(state) and \
		col >= 0 and col < len(state[row]) and \
		state[row][col] != "*"

## Move to next state
def apply_action(str_state, action, enemy, action_enemy):
	global direction

	assert(action in ACTIONS)
	message = "Your bot moved %s." % action

	state = __deserialize_state(str_state)
	g_row, g_col = __get_position(state, "o")
	# ball must be on the map
	assert(g_row >= 0 and g_col >= 0)


	# MY BOT -------------------------------------------------------------
	first_player_start = 0
	for line in range(np.shape(state)[0]):
		if state[line][0] == "|":
			first_player_start = line
			break
	
	if action == "UP" and first_player_start > 1:
		state[line-1][0] = "|"
		state[line+2][0] = " "

	elif action == "DOWN" and first_player_start+2 < np.shape(state)[0]-2:
		state[line+3][0] = "|"
		state[line][0] = " "
	
	# SECOND PLAYER ------------------------------------------------------
	second_player_start = 0
	for line in range(np.shape(state)[0]):
		if state[line][np.shape(state)[1]-1] == "|":
			second_player_start = line
			break

	# RANDOM ENEMY
	if enemy == "random":
		action_second_player = choice(("UP", "DOWN", "STAY"))
	elif enemy == "almost_perfect":
		# ALMOST PERFECT ENEMY
		if 1 - random() < 0.99:
			action_second_player = "STAY"
			if g_row-1 < second_player_start:
				action_second_player = "UP"
			elif g_row+1 > second_player_start+2:
				action_second_player = "DOWN"
		else:
			action_second_player = choice(("UP", "DOWN", "STAY"))
	elif enemy == "greedy":
		action_second_player = action_enemy
	else:
		print "Error"

	if action_second_player == "UP" and second_player_start > 1:
		state[line-1][np.shape(state)[1]-1] = "|"
		state[line+2][np.shape(state)[1]-1] = " "

	elif action_second_player == "DOWN" and \
			second_player_start+2 < np.shape(state)[0]-2:
		state[line+3][np.shape(state)[1]-1] = "|"
		state[line][np.shape(state)[1]-1] = " "

	# BALL LOGIC ---------------------------------------------------------
	if direction == "n-v":
		if state[g_row-1][g_col-1] == "*":
			# colt stanga sus
			if state[g_row][g_col-1] == "|":
				direction = "s-e"
				state[g_row][g_col] = " "
				state[g_row+1][g_col+1] = "o"
			else:
				direction = "s-v"
				state[g_row][g_col] = " "
				state[g_row+1][g_col-1] = "o"
		elif state[g_row-1][g_col-1] == "|":
			direction = "n-e"
			state[g_row][g_col] = " "
			state[g_row-1][g_col+1] = "o"
		else:
			state[g_row][g_col] = " "
			state[g_row-1][g_col-1] = "o"

	elif direction == "s-v":
		if state[g_row+1][g_col-1] == "*":
			# colt stanga jos
			if state[g_row][g_col-1] == "|":
				direction = "n-e"
				state[g_row][g_col] = " "
				state[g_row-1][g_col+1] = "o"
			else:
				direction = "n-v"
				state[g_row][g_col] = " "
				state[g_row-1][g_col-1] = "o"
		elif state[g_row+1][g_col-1] == "|":
			direction = "s-e"
			state[g_row][g_col] = " "
			state[g_row+1][g_col+1] = "o"
		else:
			state[g_row][g_col] = " "
			state[g_row+1][g_col-1] = "o"

	elif direction == "n-e":
		if state[g_row-1][g_col+1] == "*":
			# colt dreapta sus
			if state[g_row][g_col+1] == "|":
				direction = "s-v"
				state[g_row][g_col] = " "
				state[g_row+1][g_col-1] = "o"
			else:
				direction = "s-e"
				state[g_row][g_col] = " "
				state[g_row+1][g_col+1] = "o"
		elif state[g_row-1][g_col+1] == "|":
			direction = "n-v"
			state[g_row][g_col] = " "
			state[g_row-1][g_col-1] = "o"
		else:
			state[g_row][g_col] = " "
			state[g_row-1][g_col+1] = "o"

	elif direction == "s-e":
		if state[g_row+1][g_col+1] == "*":
			# colt dreapta jos
			if state[g_row][g_col+1] == "|":
				direction = "n-v"
				state[g_row][g_col] = " "
				state[g_row-1][g_col-1] = "o"
			else:
				direction = "n-e"
				state[g_row][g_col] = " "
				state[g_row-1][g_col+1] = "o"
		elif state[g_row+1][g_col+1] == "|":
			direction = "s-v"
			state[g_row][g_col] = " "
			state[g_row+1][g_col-1] = "o"
		else:
			state[g_row][g_col] = " "
			state[g_row+1][g_col+1] = "o"

	# Reward -------------------------------------------------------------
	reward = MOVE_REWARD 
	g_row, g_col = __get_position(state, "o")
	
	if g_col == 0 or g_col == np.shape(state)[1]-1:
		if g_col == 0:
			# you lost
			reward = LOSE_REWARD
			message = " You lost "
			return __serialize_state(state), reward, message
		else:
			# you won
			message = " You WON "
			reward = WIN_REWARD

			return __serialize_state(state), reward, message

	return __serialize_state(state), reward, message

def display_state(state):
	print(state)
