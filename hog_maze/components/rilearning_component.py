import pygame
import numpy as np
from hog_maze.components.component import HogMazeComponent


class RILearningComponent(HogMazeComponent):

    def __init__(self, name_instance, gamma, nstates, action_space,
                 actions, reward_dict, reward_func,
                 pi_a_s_func, theta=None, max_iter=None):
        super(RILearningComponent, self).__init__('RILEARNING')
        self.name_instance = name_instance
        self.gamma = gamma
        self.nstates = nstates
        self.states = list(range(0, nstates))
        self.action_space = action_space
        self.actions = actions
        self.reward_dict = reward_dict
        self.reward_func = reward_func
        self.pi_a_s_func = pi_a_s_func
        if theta is None:
            self.theta = .1
        else:
            self.theta = theta
        if max_iter is None:
            self.max_iter = 1000
        else:
            self.max_iter = max_iter
        self.delta = 0
        self.converged = False
        self.set_rewards_table()
        self.set_pi_a_s()
        self.initialize_value_function()
        while not self.converged:
            self.value_iteration()
        self.recalc = False
        self.just_updated = False

    def set_rewards_table(self):
        self.rewards_table = self.reward_func(
            self.actions, self.reward_dict)

    def set_pi_a_s(self):
        self.pi_a_s = self.pi_a_s_func(self.actions)

    def initialize_value_function(self):
        self.V = np.zeros(self.nstates)

    def bellman_update(self, state):
        prob_a_given_s = self.pi_a_s[state]
        next_states = [ril_obj.next_state
                       for action, ril_obj
                       in self.rewards_table[state].items()]
        probs = np.array([ril_obj.prob
                          for action, ril_obj
                          in self.rewards_table[state].items()
                          ])
        rewards = np.array([ril_obj.reward
                            for action, ril_obj
                            in self.rewards_table[state].items()
                            ])
        r = (rewards + self.gamma * np.take(self.V, next_states))
        weighted_rewards = np.multiply(
            prob_a_given_s.reshape(1, self.action_space),
            probs.reshape(1, self.action_space)
        ).dot(r.reshape(self.action_space, 1))[0]
        self.V[state] = weighted_rewards

    def value_iteration(self):
        calc_clock = pygame.time.Clock()
        t = 0
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
                # print("Convergence in {} interations".format(iter))
                break
            if iter == self.max_iter:
                print("No convergence")
                break
            calc_clock.tick()
            t += calc_clock.get_time()
            if t > 1:
                # print("Time {}, leaving calc".format(t))
                return

    def greedy_policy(self, state):
        weighted_rewards = [0] * self.action_space
        for a in self.actions:
            ril_obj = self.rewards_table[state][a]
            weighted_rewards[a] = ril_obj.prob * (
                ril_obj.reward + (self.gamma * self.V[ril_obj.next_state]))
        best_action = np.argmax(weighted_rewards)
        best_pi_a_s = np.array([1 if best_action == a else 0
                                for a in self.actions])
        self.pi_a_s[state] = best_pi_a_s

    def update(self, **kwargs):
        if self.recalc:
            print("Calculation Step")
            # print("Convergence is {}".format(self.converged))
            if self.converged:
                # print("Already converged, reset tables")
                self.converged = False
                self.set_rewards_table()
                self.set_pi_a_s()
            # self.initialize_value_function()
            self.value_iteration()
            if self.converged:
                self.just_updated = True
                self.recalc = False


class RILearningState(object):
    def __init__(self, prob, next_state, reward, end):
        self.prob = prob
        self.next_state = next_state
        self.reward = reward
        self.end = end
