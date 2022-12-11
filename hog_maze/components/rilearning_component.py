import pygame
import random
import numpy as np
import hog_maze.settings as settings
from hog_maze.components.component import HogMazeComponent
from hog_maze.util.util import index_from_prob_dist


class RIAlgorithm(object):
    VALUE_ITERATION = 1
    FIRST_VISIT_MC = 2
    FIRST_VISIT_MC_Q = 3


class MazeDirections():
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3


class RILearningComponent(HogMazeComponent):

    def __init__(self, name_instance, gamma, nstates, action_space,
                 actions, reward_dict, reward_func,
                 pi_a_s_func, nrows, ncols, num_episodes=100,
                 theta=None, max_iter=None):
        super(RILearningComponent, self).__init__('RILEARNING')
        self.name_instance = name_instance
        self.gamma = gamma
        self.nstates = nstates
        self.states = list(range(0, self.nstates))
        self.action_space = action_space
        self.actions = actions
        self.nactions = len(actions)
        self.reward_dict = reward_dict
        self.num_episodes = num_episodes
        self.nrows = nrows
        self.ncols = ncols
        if theta is None:
            self.theta = .1
        else:
            self.theta = theta
        if max_iter is None:
            self.max_iter = 1000
        else:
            self.max_iter = max_iter
        self.reset(reward_func, pi_a_s_func)

    def reset(self, reward_func, pi_a_s_func):
        self.reward_func = reward_func
        self.pi_a_s_func = pi_a_s_func
        self.delta = 0
        self.converged = False
        self.set_rewards_table()
        self.set_pi_a_s()
        self.set_q_s_a()
        self.initialize_value_function()
        self.current_algorithm = self.value_iteration
        while not self.converged:
            self.current_algorithm()
            # self.first_visit_mc()
            # self.value_iteration()
        self.recalc = False
        self.just_updated = False

    def algorithm_switch(self, algorithm_number):
        if algorithm_number == 1:
            self.current_algorithm = self.value_iteration
        elif algorithm_number == 2:
            self.current_algorithm = self.first_visit_mc

    def set_rewards_table(self):
        self.rewards_table = self.reward_func(
            self.actions, self.reward_dict)

    def set_pi_a_s(self):
        self.pi_a_s = self.pi_a_s_func(self.actions)

    def print_pi_a_s(self):
        for s, p in zip(self.states, self.pi_a_s):
            print("{}: {}".format(p, s))

    def print_best_path(self):
        maze_layout = [[None] * self.ncols
                       for i in range(0, self.nrows)
                       ]
        for state in range(0, self.nstates):
            best_path_state = np.argmax(self.pi_a_s[state])
            spot = divmod(state, self.ncols)
            if MazeDirections.NORTH == best_path_state:
                maze_layout[spot[0]][spot[1]] = "North"
            elif MazeDirections.SOUTH == best_path_state:
                maze_layout[spot[0]][spot[1]] = "South"
            elif MazeDirections.EAST == best_path_state:
                maze_layout[spot[0]][spot[1]] = "East"
            elif MazeDirections.WEST == best_path_state:
                maze_layout[spot[0]][spot[1]] = "West"

        for i in range(self.nrows):
            print(maze_layout[i])

    def initialize_value_function(self):
        self.V = np.zeros(self.nstates)

    def randomize_value_function(self):
        self.V = np.random.uniform(0, 1, self.nstates)

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

    def weighted_rewards_for_state(self, state, V_local=None):
        weighted_rewards = [0] * self.action_space
        for a in self.actions:
            ril_obj = self.rewards_table[state][a]
            if V_local is not None:
                V_next_state = V_local[ril_obj.next_state]
            else:
                V_next_state = self.V[ril_obj.next_state]
            weighted_rewards[a] = ril_obj.prob * (
                ril_obj.reward + (self.gamma * V_next_state))
        return weighted_rewards

    def greedy_policy(self, state):
        weighted_rewards = self.weighted_rewards_for_state(state)
        best_action = np.argmax(weighted_rewards)
        # print("STATE: {}".format(state))
        # print("Best Action: {}".format(best_action))
        # print("Weighted Rewards: {}".format(weighted_rewards))
        best_pi_a_s = np.array([1 if best_action == a else 0
                                for a in self.actions])
        self.pi_a_s[state] = best_pi_a_s

    def greedy_policy_q(self, state):
        best_action = self.max_action_q_s_a(state)
        # print("STATE: {}".format(state))
        # print("Best Action: {}".format(best_action))
        # print("Weighted Rewards: {}".format(weighted_rewards))
        best_pi_a_s = np.array([1 if best_action == a else 0
                                for a in self.actions])
        self.pi_a_s[state] = best_pi_a_s

    def greedy_policy_step(self, state, V_local=None):
        rn = random.uniform(0, 1)
        # print(f"RN: {rn}")
        if rn < .8:
            # print("Explore action space")
            rc = random.choice(range(0, len(self.actions)))
            action = self.actions[rc]
            return action
        else:
            weighted_rewards = self.weighted_rewards_for_state(state, V_local)
            best_action = np.argmax(weighted_rewards)
            # print("STATE: {}".format(state))
            # print("Best Action: {}".format(best_action))
            # print("Weighted Rewards: {}".format(weighted_rewards))
            return best_action

    def greedy_policy_step_q(self, state):
        rn = random.uniform(0, 1)
        # print(f"RN: {rn}")
        if rn < .8:
            # print("Explore action space")
            rc = random.choice(range(0, len(self.actions)))
            action = self.actions[rc]
            return action
        else:
            best_action = self.max_action_q_s_a(state)
            # print("STATE: {}".format(state))
            # print("Best Action: {}".format(best_action))
            # print("Weighted Rewards: {}".format(weighted_rewards))
            return best_action

    def set_pi_a_s_from_policy(self, policy_function="greedy_policy"):
        for state in self.states:
            if policy_function == 'greedy_policy':
                self.greedy_policy(state)
            if policy_function == 'greedy_policy_q':
                self.greedy_policy_q(state)

    def episode(self):
        episode_tracker_obj = EpisodeTracker()
        # state = self.states[0]
        state = random.choice(list(range(0, self.nstates)))
        found_end = False
        # V_local = np.random.uniform(0, 1, self.nstates)
        while not found_end:
            if episode_tracker_obj.T % 100000 == 0:
                print(f"State at Time: {state} at {episode_tracker_obj.T}")
            # action = self.greedy_policy_step(state, V_local)
            action = self.greedy_policy_step(state, self.V)
            # print(f"Action: {action}")
            ril_obj = self.rewards_table[state][action]
            reward = ril_obj.reward
            episode_tracker_obj.insert(state, reward, action)
            episode_tracker_obj.increment()
            # print(f"Current State is {state}")
            # print(f"Next State is {ril_obj.next_state}")
            # print(f"Reward is {reward}")
            if ril_obj.end:
                found_end = True
            else:
                state = ril_obj.next_state
        return episode_tracker_obj

    def episode_for_q(self):
        episode_tracker_obj = EpisodeTracker()
        state = random.choice(list(range(0, self.nstates)))
        action = random.choice(self.actions)
        found_end = False
        while not found_end:
            if episode_tracker_obj.T % 100000 == 0:
                print(f"State at Time: {state} at {episode_tracker_obj.T}")
            # action = self.greedy_policy_step(state, V_local)
            # action = self.greedy_policy_step(state, self.V)
            # print(f"Action: {action}")
            ril_obj = self.rewards_table[state][action]
            reward = ril_obj.reward
            episode_tracker_obj.insert(state, reward, action)
            episode_tracker_obj.increment()
            # print(f"Current State is {state}")
            # print(f"Next State is {ril_obj.next_state}")
            # print(f"Reward is {reward}")
            if ril_obj.end:
                found_end = True
            else:
                state = ril_obj.next_state
                action = self.greedy_policy_step_q(state)
        return episode_tracker_obj

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
                # print(settings.r31(self.V.reshape(3, 3)))
                # self.print_pi_a_s()
                break
            if iter == self.max_iter:
                print("No convergence")
                break
            calc_clock.tick()
            t += calc_clock.get_time()
            if t > 1:
                # print("Time {}, leaving calc".format(t))
                return

    def first_visit_mc(self):
        self.randomize_value_function()
        returns_s_total = [0 for s in range(self.nstates)]
        for e in range(self.num_episodes):
            episode_tracker_obj = self.episode()
            G = 0
            # print(f"T: {episode_tracker_obj.T}")
            for t in range(episode_tracker_obj.T - 1, -1, -1):
                s = episode_tracker_obj.tracker[t].S
                # print(f"Backward loop now at episode number {t}")
                # print(f"State is {s} with map coordinates: {divmod(
                # s, self.ncols)}")
                G = self.gamma * G + episode_tracker_obj.tracker[t].R
                # G = G + episode_tracker_obj.tracker[t].R
                in_prior_state = episode_tracker_obj.state_appears_prior(t)
                if not in_prior_state:
                    # print(f"State {s} was not found in prior
                    # states PRIOR to episode {t}")
                    returns_s_total[s] += 1
                    if returns_s_total[s] == 1:
                        self.V[s] = G
                    else:
                        self.V[s] = ((self.V[s] * (returns_s_total[s] - 1)) +
                                     G)/(returns_s_total[s])
            # episode_tracker_obj.print_episode_journey(self.ncols)
        print(settings.r31(self.V.reshape(self.nrows, self.ncols)))
        self.converged = True
        self.set_pi_a_s_from_policy('greedy_policy')
        self.print_pi_a_s()
        self.print_best_path()

    def first_visit_mc_q(self):
        self.set_q_s_a()
        returns_s_a_total = [[0] * self.nactions
                             for s in range(self.nstates)
                             ]
        for e in range(self.num_episodes):
            episode_tracker_obj = self.episode_for_q()
            G = 0
            # print(f"T: {episode_tracker_obj.T}")
            for t in range(episode_tracker_obj.T - 1, -1, -1):
                s = episode_tracker_obj.tracker[t].S
                a = episode_tracker_obj.tracker[t].A
                # print(f"Backward loop now at episode number {t}")
                # print(f"State is {s} with map coordinates: {divmod(
                # s, self.ncols)}")
                G = self.gamma * G + episode_tracker_obj.tracker[t].R
                # G = G + episode_tracker_obj.tracker[t].R
                in_prior_state = episode_tracker_obj\
                    .state_action_appears_prior(t)
                if not in_prior_state:
                    # print(f"State {s} was not found in prior
                    # states PRIOR to episode {t}")
                    returns_s_a_total[s][a] += 1
                    if returns_s_a_total[s][a] == 1:
                        self.q_s_a[s][a] = G
                    else:
                        self.q_s_a[s][a] = ((self.q_s_a[s][a] *
                                             (returns_s_a_total[s][a] - 1)) +
                                            G)/(returns_s_a_total[s][a])
            # episode_tracker_obj.print_episode_journey(self.ncols)
        print(self.q_s_a)
        self.converged = True
        self.set_pi_a_s_from_policy('greedy_policy_q')
        self.print_pi_a_s()
        self.print_best_path()

    def set_q_s_a(self):
        """
        q*(s,a), the expected return when starting in state s,
        taking action a, and thereafter following policy pi
        """
        self.q_s_a = np.zeros([
            self.nstates, self.action_space
        ])

    def max_action_q_s_a(self, state):
        max_est = np.max(self.q_s_a[state])
        if np.sum([m == max_est for m in self.q_s_a[state]]) > 1:
            action = np.random.choice(
                np.where(max_est == self.q_s_a[state])[0])
        else:
            action = np.argmax(self.q_s_a[state])
        return action

    def infinite_loop_check_recursion(self, state, previous_state):
        if state == previous_state:
            return
        action_probs = self.pi_a_s[state]
        action = index_from_prob_dist(action_probs)
        ril_obj = self.rewards_table[state][action]
        if ril_obj.end:
            return
        next_state = self.rewards_table[state][action].next_state
        if next_state == previous_state:
            print("State {} and {} are an infinite loop".format(state,
                                                                next_state))
            self.infinite_loops.append((state, next_state))
            return True
        else:
            return self.infinite_loop_check_recursion(next_state, state)

    def check_for_infinite_loops(self):
        self.infinite_loops = []
        state = 0
        action_probs = self.pi_a_s[state]
        action = index_from_prob_dist(action_probs)
        next_state = self.rewards_table[state][action].next_state
        if self.infinite_loop_check_recursion(next_state, state):
            print("Infinite loops are {}".format(self.infinite_loops))
            for i in self.infinite_loops:
                print("pi_a_s for state {}: {}".format(
                    i[0], self.pi_a_s[i[0]]))
                print("pi_a_s for state {}: {}".format(
                    i[1], self.pi_a_s[i[1]]))
                print("Rewards table for state {}: {}".format(
                    i[0], self.rewards_table[i[0]]))
            inf_loop = self.infinite_loops[0]
            state_1 = inf_loop[0]
            state_2 = inf_loop[1]
            actions = self.pi_a_s[state_2]
            action = np.argmax(actions)
            other_valid_moves = [
                a
                for a in list(self.rewards_table[state_2].keys())
                if self.rewards_table[state_2][a].is_valid_move and a != action
            ]
            print("other valid moves: {}".format(other_valid_moves))
            if len(other_valid_moves) > 0:
                m = other_valid_moves[0]
                self.pi_a_s[state_2][action] = .5
                self.pi_a_s[state_2][m] = .5
            else:
                actions = self.pi_a_s[state_1]
                action = np.argmax(actions)
                other_valid_moves = [
                    a
                    for a in list(self.rewards_table[state_1].keys())
                    if (
                        self.rewards_table[state_1][a].is_valid_move
                        and a != action
                    )
                ]
                print("other valid moves: {}".format(other_valid_moves))
                if len(other_valid_moves) > 0:
                    m = other_valid_moves[0]
                    self.pi_a_s[state_1][action] = .5
                    self.pi_a_s[state_1][m] = .5

    def update(self, **kwargs):
        if self.recalc:
            # print("Calculation Step")
            # print("Convergence is {}".format(self.converged))
            if self.converged:
                print("Already converged, reset tables")
                self.converged = False
                self.set_rewards_table()
                self.set_pi_a_s()
            # self.initialize_value_function()
            self.current_algorithm()
            if self.converged:
                print("Converged!")
                # self.check_for_infinite_loops()
                self.just_updated = True
                self.recalc = False


class RILearningState(object):
    def __init__(self, prob, next_state, reward, end, is_valid_move):
        self.prob = prob
        self.next_state = next_state
        self.reward = reward
        self.end = end
        self.is_valid_move = is_valid_move


class EpisodeTracker(object):
    def __init__(self):
        self.tracker = []
        self.T = 0

    def insert(self, S, R, A):
        self.tracker.append(Episode(S, R, A))

    def increment(self):
        self.T += 1

    def state_appears_prior(self, t):
        s = self.tracker[t].S
        prior_states = [self.tracker[i].S for i in range(0, t)]
        # print(f"current state: {s}")
        # print(f"prior states: {prior_states}")
        if s in prior_states:
            return True
        else:
            return False

    def state_action_appears_prior(self, t):
        s = self.tracker[t].S
        a = self.tracker[t].A
        prior_state_actions = [(self.tracker[i].S, self.tracker[i].A)
                               for i in range(0, t)
                               ]
        # print(f"current state: {s}")
        # print(f"prior states: {prior_states}")
        # print(f"current state, action: {(s, a)}")
        # print(f"prior states: {prior_state_actions}")
        if (s, a) in prior_state_actions:
            # print("FOUND IN PRIOR STATE!")
            return True
        else:
            return False

    def print_episode_journey(self, ncols):
        journey_list = []
        print(f"Starting state: {self.tracker[0].S}")
        print(f"Starting area on map: {divmod(self.tracker[0].S, ncols)}")
        for e in self.tracker:
            if MazeDirections.NORTH == e.A:
                journey_list.append("North")
            elif MazeDirections.SOUTH == e.A:
                journey_list.append("South")
            elif MazeDirections.EAST == e.A:
                journey_list.append("East")
            elif MazeDirections.WEST == e.A:
                journey_list.append("West")
        print(journey_list)
        print([t.S for t in self.tracker])


class Episode(object):
    def __init__(self, S, R, A):
        self.S = S
        self.R = R
        self.A = A
