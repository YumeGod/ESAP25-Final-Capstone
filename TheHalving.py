import random
import time
import pandas as pd

class Game:
    def __init__(self, start_number):
        self.start_number = start_number
        self.d = 0
        self.depth = 0
        self.minimax_times = []

    def startState(self):
        return (self.start_number, 0)

    def actions(self, state):
        return ['minus1', 'divide2']

    def succ(self, state, action):
        n, player = state
        if action == 'minus1':
            n -= 1
        elif action == 'divide2':
            n //= 2
        return (n, 1 - player)

    def isEnd(self, state):
        return state[0] == 0

    def utility(self, state):
        if self.isEnd(state):
            return -1 if state[1] == 0 else 1
        return 0

    def minimax(self, state, maximizingPlayer):
        if self.isEnd(state):
            return self.utility(state), None

        best_action = None
        if maximizingPlayer:
            maxEval = float('-inf')
            for action in self.actions(state):
                self.d += 1
                eval, _ = self.minimax(self.succ(state, action), False)
                self.depth = max(self.depth, self.d)
                self.d -= 1
                if eval > maxEval:
                    maxEval = eval
                    best_action = action
            return maxEval, best_action
        else:
            minEval = float('inf')
            for action in self.actions(state):
                self.d += 1
                eval, _ = self.minimax(self.succ(state, action), True)
                self.depth = max(self.depth, self.d)
                self.d -= 1
                if eval < minEval:
                    minEval = eval
                    best_action = action
            return minEval, best_action

    def random_action(self, state):
        return random.choice(self.actions(state))

    def play(self, mode="human_vs_bot", simulate=False):
        """
        Plays a game. If simulate=True, returns a dict with result stats.
        """
        state = self.startState()
        flip = random.randint(0, 1)
        self.minimax_times = []
        self.depth = 0
        turn_count = 0

        if not simulate:
            print(f"\n[INFO] Starting number: {self.start_number}")
            print(f"[INFO] Minimax bot is player {flip}\n")

        while not self.isEnd(state):
            n, player = state
            if not simulate:
                print(f"Current number: {n}, Player {player}'s turn")

            if player == flip:
                start_time = time.time()
                _, action = self.minimax(state, flip == 0)
                self.minimax_times.append(time.time() - start_time)
                if not simulate:
                    print(f"Bot chooses: {action}")
            else:
                if mode == "random_vs_bot" or simulate:
                    action = self.random_action(state)
                else:
                    valid = self.actions(state)
                    action = ""
                    while action not in valid:
                        action = input(f"Choose from {valid}: ").strip()

            state = self.succ(state, action)
            turn_count += 1

        winner = 1 - state[1]
        if not simulate:
            print(f"\nGame Over! Player {winner} wins!")
            print(f"Game Tree Max Depth: {self.depth}")

        return {
            "start_number": self.start_number,
            "winner": winner,
            "minimax_player": flip,
            "minimax_bot_wins": winner == flip,
            "turns": turn_count,
            "max_depth": self.depth,
            "avg_minimax_time": sum(self.minimax_times) / len(self.minimax_times) if self.minimax_times else 0
        }

def run_loop(mode="human_vs_bot", n_games=1, start_range=(15, 30), output_file="game_data.csv"):
    all_results = []
    for i in range(n_games):
        print(f"\n========== Game {i+1} / {n_games} ==========")
        start_number = random.randint(*start_range)
        game = Game(start_number)
        stats = game.play(mode=mode, simulate=(mode == "random_vs_bot"))
        stats["game_number"] = i + 1
        all_results.append(stats)

    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False)
    print(f"\n[INFO] Saved {n_games} game results to '{output_file}'")
    print(f"[INFO] Minimax bot win rate: {df['minimax_bot_wins'].mean() * 100:.2f}%")
    return df

# ========== CLI ENTRY ==========
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["human_vs_bot", "random_vs_bot"], required=True, help="Game mode")
    parser.add_argument("--games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--output", type=str, default="game_data.csv", help="Output CSV filename")
    args = parser.parse_args()

    run_loop(mode=args.mode, n_games=args.games, output_file=args.output)