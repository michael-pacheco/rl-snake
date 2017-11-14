import sys, os
from MiniSnake import game
from keras.models import Sequential
from keras.layers.core import Dense, Flatten, Dropout
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D, BatchNormalization
import numpy as np
from collections import deque
from skimage import color, transform
import random
from keras.utils import plot_model

game_engine = game()
D = deque()
from config import num_of_cols, num_of_rows, num_of_hidden_layer_neurons, img_channels, num_of_actions, \
	batch_size, epsilon, observe, gamma, action_array, reward_on_eat, reward_in_env, death_reward, \
	timesteps_to_save_weights, exp_replay_memory


#Convolves 32 filters size 8x8 with stride = 4
model = Sequential()
model.add(Conv2D(32, kernel_size=(8,8), strides=(4, 4), activation='relu',input_shape=(num_of_cols,num_of_rows,img_channels)))
model.add(MaxPooling2D(pool_size=(4,4), strides=(2, 2), padding='same'))
model.add(Conv2D(64, kernel_size=(4,4), strides=(2, 2), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(1, 1), padding='same'))
model.add(Flatten())
model.add(Dense(num_of_hidden_layer_neurons, activation='relu'))
model.add(Dense(num_of_actions))
model.compile(loss='mse',optimizer='adam')
#plot_model(model, to_file='model.png')
model.load_weights("weights.hdf5")

start_game = game_engine.play(0)


#Obtain the starting state
r_0, s_t, s_f = game_engine.play(0)

s_t = color.rgb2gray(s_t)
s_t = transform.resize(s_t,(num_of_cols,num_of_rows))
s_t = np.stack((s_t, s_t, s_t, s_t), axis=2)
#In Keras, need to reshape
s_t = s_t.reshape(1, s_t.shape[0], s_t.shape[1], s_t.shape[2])	#1*num_of_cols*num_of_rows*4


t=0

while True:
	explored = False

	loss = 0	#initialize the loss of the network
	Q_sa = 0	#initialize state
	action_index = 0	#initialize action index
	r_t = 0		#initialize reward
	#a_t = np.zeros([num_of_actions])   #initalize acctions as an array that holds one array [0, 0]

	if t < observe:
		action_index = 1 if random.random() < 0.5 else 0
	else:
		if random.random() <= epsilon:
			action_index = random.randint(0, num_of_actions-1)	  #choose a random action
			explored = True
		else:
			q = model.predict(s_t)		 #input a stack of 4 images, get the prediction
			action_index = np.argmax(q)


	r_t, s_t1, terminal = game_engine.play(action_array[action_index])

	#get and preprocess our transitioned state
	s_t1 = color.rgb2gray(s_t1)
	s_t1 = transform.resize(s_t1,(num_of_rows,num_of_cols))

	s_t1 = s_t1.reshape(1, s_t1.shape[0], s_t1.shape[1], 1) #1x80x80x1
	s_t1 = np.append(s_t1, s_t[:, :, :, :3], axis=3)

	#append the state to our experience replay memory
	D.append((s_t, action_index, r_t, s_t1, terminal))

	if len(D) > exp_replay_memory:
		D.popleft()

	if t > observe:
		#sample a random minibatch of transitions in D (replay memory)
		random_minibatch = random.sample(list(D), batch_size)

		inputs = np.zeros((batch_size, s_t.shape[1], s_t.shape[2], s_t.shape[3]))	#32, 80, 80, 4
		targets = np.zeros((inputs.shape[0], num_of_actions))						  #32, 2

		for i in range(0, len(random_minibatch)):
			state_t = random_minibatch[i][0]
			action_t = random_minibatch[i][1]
			reward_t = random_minibatch[i][2]
			state_t1 = random_minibatch[i][3]
			terminal = random_minibatch[i][4]

			#fill out the inputs and outputs with the information in the minibatch, and what values we get from the network
			inputs[i:i + 1] = state_t
			targets[i] = model.predict(state_t)

			Q_sa = model.predict(state_t1)
			#set the value of the action we chose in each state in the random minibatch to the reward given at that state (Q-learn)
			if terminal:
				targets[i, action_t] = death_reward
			else:
				targets[i, action_t] = reward_t + gamma * np.max(Q_sa)

		#train the network with the new values calculated with Q-learning and get loss of our network for evaluation
		loss += model.train_on_batch(inputs, targets)

	s_t = s_t1
	t += 1

	if t % timesteps_to_save_weights == 0:
		model.save_weights('weights.hdf5', overwrite=True)

	print("Timestep: %d, Action: %d, Reward: %.2f, Q: %.2f, Loss: %.2f, Explored: %s" % (t, action_index, r_t, np.max(Q_sa), loss, explored))
