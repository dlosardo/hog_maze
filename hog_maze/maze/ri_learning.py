import random
from collections import Counter
import numpy as np


class RIState(object):
    def __init__(self, prob, next_state, reward, end):
        self.prob = prob
        self.next_state = next_state
        self.reward = reward
        self.end = end


class RILearning(object):
    def __init__(self, epsilon, alpha, gamma,
                 nstates, action_space, actions):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.nstates = nstates
        self.states = list(range(0, nstates))
        self.action_space = action_space
        self.actions = actions
        self.set_qn()
        self.cum_reward = 0
        self.step_size_tracker = np.zeros([
            self.nstates, self.action_space
        ])

    def set_rewards_table(self, rewards_func, reward_dict):
        self.rewards_table = rewards_func(self.actions, reward_dict)

    def set_state_trans_matrix(self):
        self.state_trans_matrix = None
        for current_state in self.states:
            cnt = Counter()
            next_states = [
                self.rewards_table[current_state][i][0][1]
                for i in self.actions
            ]
            for next_state in next_states:
                cnt[next_state] += 1
            probs = [(i, cnt[i] / len(next_states)) for i in cnt]
            probs_i = np.zeros(self.nstates)
            for p in probs:
                probs_i[p[0]] = p[1]
            if self.state_trans_matrix is None:
                self.state_trans_matrix = probs_i.reshape(1, self.nstates)
            else:
                self.state_trans_matrix = np.concatenate(
                    (self.state_trans_matrix, probs_i.reshape(1, self.nstates))
                )

    def set_rewards_matrix(self):
        self.R = np.zeros(self.nstates)
        for s, d in self.rewards_table.items():
            cum_sum = 0
            for a in self.actions:
                cum_sum += d[a][0][2]
            self.R[s] = cum_sum / len(self.actions)
        self.R = self.R.reshape(self.nstates, 1)

    def set_qn(self):
        self.q_n = np.zeros([
            self.nstates, self.action_space
        ])

    def max_action(self, state):
        max_est = np.max(self.q_n[state])
        if np.sum([m == max_est for m in self.q_n[state]]) > 1:
            action = np.random.choice(
                np.where(max_est == self.q_n[state])[0])
        else:
            action = np.argmax(self.q_n[state])
        return action

    def epsilon_greedy(self, state):
        if random.uniform(0, 1) < self.epsilon:
            # Explore action space
            rc = random.choice(range(0, len(self.actions)))
            action = self.actions[rc]
        else:
            # Exploit learned values
            action = self.max_action(state)
        return action

    def reward_for_state_action(self, state, action):
        return self.rewards_table[state][action][0][2]

    def next_state_for_state_action(self, state, action):
        return self.rewards_table[state][action][0][1]

    def expected_reward(self, state, action, end):
        if end:
            return self.reward_for_state_action(
                state, action)
        elif self.cum_reward < -10:
            return self.reward_for_state_action(
                state, action)
        else:
            (p, next_state,
             reward, end) = self.rewards_table[state][action][0]
            self.cum_reward += reward
            return reward + self.gamma * self.expected_reward(
                next_state, self.epsilon_greedy(next_state), end)

    def step_size_for_state_action(self, state, action):
        return 1./self.step_size_tracker[state][action]

    def update_qn_for_state_action_1(self, state, action):
        # new estimate = old estimate + step_size * [Reward - Old Estimate]
        self.step_size_tracker[state][action] += 1
        self.q_n[state][action] = self.q_n[
            state][action] + self.step_size_for_state_action(state, action) * (
          self.reward_for_state_action(
              state, action) - self.q_n[state][action])

    def update_qn_for_state_action_2(self, state, action):
        self.q_n[state][action] = (1 - self.alpha)*self.q_n[
          state][action] + self.alpha*(self.reward_for_state_action(
              state, action) + self.gamma*np.max(
                  self.q_n[self.next_state_for_state_action(
                      state, action)]))

    def update_qn_for_state_action(self, state, action):
        self.cum_reward = 0
        self.q_n[state][action] = (1 - self.alpha)*self.q_n[
            state][action] + self.alpha*(self.reward_for_state_action(
                state, action) + self.gamma*self.expected_reward(
                    state, action, False))

    def initialize_value_function(self):
        self.V = np.zeros(self.nstates)

    def value_function(self):
        Iden = np.identity(self.nstates)
        self.V = np.linalg.inv(
            Iden - self.gamma*self.state_trans_matrix).dot(self.R)

    def sweep(self):
        for s in self.states:
            weighted_rewards = 0
            for a in self.actions:
                (p, next_state,
                 reward, end) = self.rewards_table[s][a][0]
                weighted_rewards += (1 / len(self.actions)) * (
                    reward + (self.gamma * self.V[next_state]))
            self.V[s] = weighted_rewards

    def train(self):
        state = 0
        end = False
        while not end:
            action = self.epsilon_greedy(state)
            (p, next_state,
             reward, end) = self.rewards_table[state][action][0]
            self.update_qn_for_state_action_1(state, action)
            state = next_state
