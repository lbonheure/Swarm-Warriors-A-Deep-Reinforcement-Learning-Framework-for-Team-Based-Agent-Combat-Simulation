import random
from collections import deque

import numpy as np
import tensorflow as tf

DIRECTIONS = ["N", "S", "W", "E"]

North = (0, 1)
South = (0, -1)
West = (-1, 0)
East = (1, 0)
# List of actions
move_list = ["N", "S", "W", "E", "A"]


class Agent:
    def __init__(self, input_size=25, output_size=5,
                 epsilon=0.9,
                 decay=0.9863,
                 gamma=0.9,
                 loss_fct="mse",
                 opt_fct="adam",
                 mem=1000000, metrics=None, epsilon_min=0.1) -> None:

        # ---- Init Neural networks ----
        tf.keras.utils.disable_interactive_logging()
        self.n_games = 0
        # Init parameter for NN
        if metrics is None:
            metrics = ["mean_squared_error"]
        self.input_size = input_size
        self.epsilon = epsilon
        self.gamma = gamma
        self.loss_fct = loss_fct
        self.opt_fct = opt_fct
        self.memory = deque(maxlen=mem)
        self.decay = decay
        self.metrics = metrics
        self.moves = []
        self.epsilon_min = epsilon_min
        # Structure of NN
        self.model = tf.keras.models.Sequential()
        self.model.add(tf.keras.layers.Dense(64, activation="relu", input_shape=(input_size,)))
        # self.model.add(tf.keras.layers.Dense(64, activation="relu"))
        # self.model.add(tf.keras.layers.Dense(64, activation="relu"))
        self.model.add(tf.keras.layers.Dense(64, activation="relu"))
        self.model.add(tf.keras.layers.Dense(32, activation="relu"))
        self.model.add(tf.keras.layers.Dense(output_size, activation="linear"))
        self.model.compile(
            optimizer=self.opt_fct, loss=self.loss_fct, metrics=self.metrics)

    def calculate_decay(self, episodes):
        """
        Compute the value of decay parameter in function of the number of training episodes
        :param episodes: Number of training episodes
        """
        target_ratio = self.epsilon_min / self.epsilon
        self.decay = target_ratio ** (1 / (0.8 * episodes))

    def train_long_memory(self, batch_size=64):
        """
        This function extract previous instances to upgrade the behavior, and update epsilon
        :param batch_size: Number of instance used for the learning
        :return: none
        """
        # Selection of "model" in the memory
        if len(self.memory) > batch_size:
            sample = random.sample(self.memory, batch_size)
        else:
            sample = self.memory

        states, rewards, next_states, dones = zip(*sample)
        self.training_montage(states, rewards, next_states, dones)
        self.epsilon = max(
            self.epsilon * self.decay, self.epsilon_min
        )

    def training_montage(self, state, reward, next_state, done):
        """
        This function allow the learning of our agent using Q-learning and the neural network
        Parameters can be a single value or a batch of values in a numpy array
        :param state: Information of the environment
        :param reward: Reward of the action done
        :param next_state: New state of the snake after an action
        :param done: Boolean about the state of the game (True when game finished)
        :return: None
        """
        if len(state) == 0:
            return
        state = tf.convert_to_tensor(state, dtype=tf.float32)
        reward = tf.convert_to_tensor(reward, dtype=tf.float32)
        next_state = tf.convert_to_tensor(next_state, dtype=tf.float32)
        # print("state tensor=", state)

        if len(state.shape) == 1:
            state = tf.expand_dims(state, 0)
            reward = tf.expand_dims(reward, 0)
            next_state = tf.expand_dims(next_state, 0)
            done = (done,)
        # Q values with current state
        scores = self._predict_scores(next_state)  # Prediction with the neural network
        dataset = []
        target = []
        # Apply Q-learning method
        for i in range(len(done)):
            if not done[i]:
                next_q = self.gamma * scores[i] + reward[i]
            else:
                next_q = reward[i]

            dataset.append(list(state[i]))
            target.append(np.array(next_q))

        dataset = tf.convert_to_tensor(dataset)
        target = tf.convert_to_tensor(target)

        # start = time.time_ns()
        self.model.train_on_batch(
            dataset, target
        )
        # print("time train on batch", (time.time_ns() - start)/1000000, "ms")

    def act_train(self, state):
        """
        Train the model using random moves and predictions
        :param state: Information about the environment of the snake
        :return: Next move
        """
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(move_list)
        else:
            state0 = tf.convert_to_tensor(state, dtype=tf.float32)
            prediction = self._predict_scores(state0)  # Prediction with the neural network
            move = int(tf.math.argmax(prediction[0]))  # Take the best move predicted
            final_move = move_list[move]

        return final_move

    def act_best(self, state):
        """
        Use the best possible prediction with  the model (no randomness)
        :param state: Information about the environment of the snake
        :return: next move
        """
        state0 = tf.convert_to_tensor(state, dtype=tf.float32)
        prediction = self._predict_scores(state0)  # Prediction with the neural network
        move = int(tf.math.argmax(prediction[0]))  # Take the best move predicted
        final_move = move_list[move]

        return final_move

    def _predict_scores(self, states):
        """
        Predict the new action of the snake using the neural network
        :param states: Information about the environment of the snake
        :return: Possible moves with ponderation
        """
        input = tf.cast(tf.constant(states), dtype=tf.float32)
        if input.ndim == 1:
            input = tf.expand_dims(input, axis=0)

        predictions = self.model.predict_on_batch(input)
        # predictions = self.model.predict(input) Causes memory leaks over time
        return predictions

    def fill_memory(self, state, reward, next_state, done):
        """
        Fill the buffer with previous experiences
        :param state:original state
        :param reward:reward received
        :param next_state:state after the action
        :param done:boolean value to signify whether the end of an episode is reached
        """
        self.memory.append((state, reward, next_state, done))

    def save(self, path: str):
        """
        save the weights of the network
        :param path: filepath where weights are saved
        """
        self.model.save_weights(path)

    def load(self, path: str):
        """
        load the weights of the network
        :param path: filepath where weights are saved
        """
        self.model.load_weights(path)

    def choose_next_move(self, game):
        """
        Return the move chosen by the agent
        :param game: the game object in order to access the state
        :return: the move chosen in [RIGHT, LEFT, UP, DOWN]
        """
        state = self.get_information(game)
        return self.act_best(state)


class CombatAgent(Agent):
    def __init__(self, color: str, atk_range: int, atk: int) -> None:
        super().__init__()
        self.color = color
        self.atk_range = atk_range
        self.atk = atk

    def get_color(self):
        return self.color

    def get_range(self):
        return self.atk_range

    def get_atk(self):
        return self.atk
