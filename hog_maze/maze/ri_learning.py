import random
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
        self.theta = .01
        self.delta = 0
        self.set_qn()
        self.cum_reward = 0
        self.step_size_tracker = np.zeros([
            self.nstates, self.action_space
        ])
        self.converged = False
        self.max_iter = 1000
        self.policy_stable = False

    def set_rewards_table(self, rewards_func, reward_dict):
        self.rewards_table = rewards_func(self.actions, reward_dict)

    def set_pi_a_s(self, pi_a_s_func):
        self.pi_a_s = pi_a_s_func(self.actions)

    def set_state_trans_matrix(self):
        self.state_trans_matrix = None
        for current_state in self.states:
            next_states = [
                self.rewards_table[current_state][i][0][1]
                for i in self.actions
            ]
            next_probs = [
                self.rewards_table[current_state][i][0][0]
                for i in self.actions
            ]
            prob_is_state = np.array([
                [next_prob if next_state == s else 0
                 for next_state, next_prob in zip(next_states, next_probs)]
                for s in self.states
            ])
            probs_i = prob_is_state.dot(self.pi_a_s[current_state])
            if self.state_trans_matrix is None:
                self.state_trans_matrix = probs_i.reshape(1, self.nstates)
            else:
                self.state_trans_matrix = np.concatenate(
                    (self.state_trans_matrix, probs_i.reshape(1, self.nstates))
                )

    def set_rewards_matrix_old(self):
        self.R = np.zeros(self.nstates)
        for s, d in self.rewards_table.items():
            cum_sum = 0
            for a in self.actions:
                cum_sum += d[a][0][2]
            self.R[s] = cum_sum / len(self.actions)
        self.R = self.R.reshape(self.nstates, 1)

    def set_rewards_matrix(self):
        self.R = np.zeros(self.nstates)
        for s, d in self.rewards_table.items():
            weighted_rewards = 0
            for a in self.actions:
                prob_s_next_cond_s_a = d[a][0][0]
                reward_s_next_cond_s_a = d[a][0][2]
                prob_a_given_s = self.pi_a_s[s][a]
                weighted_rewards += (prob_a_given_s * prob_s_next_cond_s_a
                                     * reward_s_next_cond_s_a)
            self.R[s] = weighted_rewards
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

    def sweep_new(self):
        self.delta = 0
        for s in self.states:
            prob_a_given_s = self.pi_a_s[s]
            next_states = [l[0][1]
                           for action, l in self.rewards_table[s].items()]
            probs = np.array([l[0][0]
                              for action, l in self.rewards_table[s].items()
                              ])
            rewards = np.array([l[0][2]
                                for action, l in self.rewards_table[s].items()
                                ])
            r = (rewards + self.gamma * np.take(self.V, next_states))
            weighted_rewards = np.multiply(
                prob_a_given_s.reshape(1, self.action_space),
                probs.reshape(1, self.action_space)
            ).dot(r.reshape(self.action_space, 1))[0]
            old_v = self.V[s]
            self.V[s] = weighted_rewards
            self.delta = np.max([self.delta, np.abs(old_v - self.V[s])])

    def bellman_update(self, state):
        prob_a_given_s = self.pi_a_s[state]
        next_states = [l[0][1]
                       for action, l in self.rewards_table[state].items()]
        probs = np.array([l[0][0]
                          for action, l in self.rewards_table[state].items()
                          ])
        rewards = np.array([l[0][2]
                            for action, l in self.rewards_table[state].items()
                            ])
        r = (rewards + self.gamma * np.take(self.V, next_states))
        weighted_rewards = np.multiply(
            prob_a_given_s.reshape(1, self.action_space),
            probs.reshape(1, self.action_space)
        ).dot(r.reshape(self.action_space, 1))[0]
        self.V[state] = weighted_rewards

    def value_iteration_2(self):
        iter = 0
        while True:
            iter += 1
            self.delta = 0
            for s in self.states:
                old_v = self.V[s].copy()
                self.greedy_policy(s)
                self.bellman_update(s)
                self.delta = np.max([self.delta, np.abs(old_v - self.V[s])])
            if self.delta < self.theta:
                self.converged = True
                print("Convergence in {} interations".format(iter))
                break
            if iter == self.max_iter:
                print("No convergence")
                break

    def sweep(self):
        self.delta = 0
        for s in self.states:
            weighted_rewards = 0
            for a in self.actions:
                (p, next_state,
                 reward, end) = self.rewards_table[s][a][0]
                prob_a_given_s = self.pi_a_s[s][a]
                weighted_rewards += prob_a_given_s * p * (
                    reward + (self.gamma * self.V[next_state]))
            old_v = self.V[s]
            self.V[s] = weighted_rewards
            self.delta = np.max([self.delta, np.abs(old_v - self.V[s])])

    def policy_evaluation(self):
        iter = 0
        while True:
            iter += 1
            self.sweep()
            if self.delta < self.theta:
                self.converged = True
                print("Convergence in {} interations".format(iter))
                break
            if iter == self.max_iter:
                print("No convergence")
                break

    def greedy_policy(self, state):
        weighted_rewards = [0] * self.action_space
        for a in self.actions:
            (p, next_state,
             reward, end) = self.rewards_table[state][a][0]
            weighted_rewards[a] = p * (
                reward + (self.gamma * self.V[next_state]))
        best_action = np.argmax(weighted_rewards)
        best_pi_a_s = np.array([1 if best_action == a else 0
                                for a in self.actions])
        self.pi_a_s[state] = best_pi_a_s

    def policy_improvement(self):
        self.policy_stable = True
        for s in self.states:
            old_pi_a_s = self.pi_a_s[s].copy()
            self.greedy_policy(s)
            if not np.array_equal(self.pi_a_s[s], old_pi_a_s):
                self.policy_stable = False

    def policy_iteration(self):
        self.policy_stable = False
        while not self.policy_stable:
            self.policy_evaluation()
            self.policy_improvement()
        self.V = self.V.reshape(self.nstates, 1)

    def train(self):
        state = 0
        end = False
        while not end:
            action = self.epsilon_greedy(state)
            (p, next_state,
             reward, end) = self.rewards_table[state][action][0]
            self.update_qn_for_state_action_1(state, action)
            state = next_state
