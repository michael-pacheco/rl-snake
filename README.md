<h2>
  A reinforcement learning agent that learns to play Snake through Deep Reinforcement Learning (DQN).
  This version of Snake was created by <a href="http://www.pixelatedawesome.com/">Daniel Westbrook</a>, and can be found <a href="http://projects.pixelatedawesome.com/minisnake/">here</a>. The original game was modified into a better learning environment.
</h2>

<h2>Requirements: (Python 3x)</h2>
<ul>
  <li>
    Numpy
  </li>
  <li>
    Pygame
  </li>
  <li>
    Scikit-image
  </li>
  <li>
    Tensorflow
  </li>
  <li>
    Keras
  </li>
  <li>
    h5py
  </li>
</ul>

<h2>
  train.py
</h2>
  <p>
    All information involving the reinforcement learning algorithm.
  </p>
<h2>
  config.py
</h2>
  <p>
    Contains several variables used by the DQN and learning algorithm:
    <ul>
      <li>
        num_of_cols - number of columns for screenshot resizing
      </li>
      <li>
        num_of_rows - number of rows for screenshot resizing
      </li>
      <li>  
        num_of_hidden_layer_neurons - number of neurons in the fully connected layer before the output layer
      </li>
      <li>    
        img_channels - channels of image
      </li>
      <li>  
        num_of_actions
      </li>
      <li>  
        batch_size - batch size in experience replay deque to update
      </li>
      <li>  
        epsilon
      </li>
      <li>  
        observe - amount of timesteps to observe until actually training the agent
      </li>
      <li>  
        gamma
      </li>
      <li>  
        action_array - list of inputs which are the actions the agent can do
      </li>
      <li>  
        reward_on_eat - reward given to the agent for eating food
      </li>
      <li>  
        reward_in_env - reward given to the agent for remaining alive in the environment
      </li>
      <li>  
        death_reward - reward given to the agent when it dies
      </li>
      <li>  
        timesteps_to_save_weights - timesteps until the weights of the model are saved to a file
      </li>
      <li>  
        exp_replay_memory - length of the experience replay deque until it starts popping information from it
      </li>
    </ul>
  </p>
