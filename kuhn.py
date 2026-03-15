import random


class Node:
    def __init__(self, info_set):
        self.info_set = info_set
        self.regret_sum = [0.0, 0.0]
        self.strategy_sum = [0.0, 0.0]
        self.strategy = [0.0, 0.0]
        self.num_actions = 2

    def get_strategy(self, realization_weight):

        normalizing_sum = 0.0

        for i in range(self.num_actions):
            self.strategy[i] = self.regret_sum[i] if self.regret_sum[i] > 0 else 0.0
            normalizing_sum += self.strategy[i]

        for i in range(self.num_actions):
            if normalizing_sum > 0:
                self.strategy[i] /= normalizing_sum
            else:
                self.strategy[i] = 1.0 / self.num_actions

            self.strategy_sum[i] += realization_weight * self.strategy[i]

        return self.strategy

    def get_average_strategy(self):
        avg_strategy = [0.0, 0.0]
        normalizing_sum = sum(self.strategy_sum)
        for i in range(self.num_actions):
            if normalizing_sum > 0:
                avg_strategy[i] = self.strategy_sum[i] / normalizing_sum
            else:
                avg_strategy[i] = 1.0 / self.num_actions
        return avg_strategy

    def __str__(self):
        avg_strat = self.get_average_strategy()
        return f"info set: {self.info_set:4}: [Pass prob: {avg_strat[0]:.4f}, Bet prob: {avg_strat[1]:.4f}]"


class KuhnPokerCFR:
    def __init__(self):
        self.node_map = {}

    def cfr(self, cards, history, p0, p1):
        plays = len(history)
        player = plays % 2
        opponent = 1 - player

        # Compute payoff for terminal states
        if plays > 1:
            is_player_card_higher = cards[player] > cards[opponent]

            # Case 1: both players checked
            if history == "pp":
                return 1 if is_player_card_higher else -1

            # Case 2: someone bet and opponent folded
            if history in ("bp", "pbp"):
                return 1

            # Case 3: double bet
            if history in ("bb", "pbb"):
                return 2 if is_player_card_higher else -2

        # info_set = player's card + history of actions
        info_set = str(cards[player]) + history
        if info_set not in self.node_map:
            self.node_map[info_set] = Node(info_set)
        node = self.node_map[info_set]

        # current stratedy for this information set
        strategy = node.get_strategy(p0 if player == 0 else p1)

        # expected payoff
        util = [0.0, 0.0]
        node_util = 0.0

        actions = ["p", "b"]  # 0: Pass, 1: Bet
        for i, action in enumerate(actions):
            next_history = history + action
            # recursion, my payoff = -opponent's payoff
            if player == 0:
                util[i] = -self.cfr(cards, next_history, p0 * strategy[i], p1)
            else:
                util[i] = -self.cfr(cards, next_history, p0, p1 * strategy[i])

            node_util += strategy[i] * util[i]

        # Regret and regret sum
        for i in range(2):
            regret = util[i] - node_util
            # Weight
            node.regret_sum[i] += (p1 if player == 0 else p0) * regret

        return node_util

    def train(self, iterations, seed=None):
        if seed is not None:
            random.seed(seed)
        cards = [1, 2, 3]  # 1: J, 2: Q, 3: K
        expected_game_value = 0.0

        print(f"iterations:{iterations} ")
        for _ in range(iterations):
            random.shuffle(cards)
            expected_game_value += self.cfr(cards, "", 1.0, 1.0)

        print("complete")
        print(
            f"expected game value of player 1 (Theoratically = -1/18 ≈ -0.0556): {expected_game_value / iterations}"
        )

        print("Strategy(Nash Equilibrium)")
        for _, node in sorted(self.node_map.items()):
            print(node)


if __name__ == "__main__":
    cfr_trainer = KuhnPokerCFR()
    cfr_trainer.train(1000000, seed=42)
