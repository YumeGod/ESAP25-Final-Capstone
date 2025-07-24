import random
import time
import pandas as pd

class Game:
    def __init__(self, heaps):
        self.heaps = heaps
        self.current_player = 0
        self.depth = 0
        self.minimax_times = []
        self.memo = {}  # Manual cache for minimax

    def startState(self):
        return self.heaps.copy()

    def isEnd(self, state):
        return all(h == 0 for h in state)

    @staticmethod
    def actions_static(state):
        actions = []
        for i, heap in enumerate(state):
            for take in range(1, heap + 1):
                actions.append((i, take))
        return actions

    @staticmethod
    def succ_static(state, action):
        heap_index, remove = action
        new_state = state.copy()
        new_state[heap_index] -= remove
        return new_state

    def actions(self, state):
        return self.actions_static(state)

    def succ(self, state, action):
        return self.succ_static(state, action)

    def random_action(self, state):
        return random.choice(self.actions(state))

    def print_heaps(self, state):
        max_height = max(state)
        for level in range(max_height, 0, -1):
            line = ""
            for heap in state:
                if heap >= level:
                    line += "  |  "
                else:
                    line += "     "
            print(line)
        print("-----" * len(state))
        index_line = ""
        for i in range(len(state)):
            index_line += f"  {i:^3}"
        print(index_line)

    def minimax(self, state, maxPlayer, depth=0):
        """
        Recursive minimax with manual memoization and depth tracking.
        """
        state_key = (tuple(state), maxPlayer)
        if state_key in self.memo:
            return self.memo[state_key]

        if self.isEnd(state):
            result = (-1 if maxPlayer else 1), None
            self.memo[state_key] = result
            return result

        best_action = None
        best_value = float('-inf') if maxPlayer else float('inf')

        for action in self.actions(state):
            next_state = self.succ(state, action)
            value, _ = self.minimax(next_state, not maxPlayer, depth + 1)

            if maxPlayer and value > best_value:
                best_value = value
                best_action = action
            elif not maxPlayer and value < best_value:
                best_value = value
                best_action = action

        self.depth = max(self.depth, depth)
        result = (best_value, best_action)
        self.memo[state_key] = result
        return result

    def play(self, mode="human_vs_bot", simulate=False):
        state = self.startState()
        flip = random.randint(0, 1)
        self.current_player = 0
        self.depth = 0
        self.minimax_times = []
        self.memo = {}
        turns = 0

        if not simulate:
            print(f"\n[INFO] Initial heaps: {state}")
            print(f"[INFO] Minimax bot is player {flip}\n")

        while not self.isEnd(state):
            if not simulate:
                self.print_heaps(state)
                print(f"Player {self.current_player}, it's your turn.")

            if self.current_player == flip:
                start = time.time()
                _, action = self.minimax(state, True, 0)
                self.minimax_times.append(time.time() - start)
                if not simulate:
                    print(f"Bot chooses: Heap {action[0]}, Remove {action[1]}")
            else:
                if simulate or mode == "random_vs_bot":
                    action = self.random_action(state)
                else:
                    try:
                        heap = int(input("Enter the heap index to remove from: "))
                        remove = int(input(f"Enter number to remove from heap {heap}: "))
                        action = (heap, remove)
                        if action not in self.actions(state):
                            print("Invalid move. Try again.")
                            continue
                    except Exception:
                        print("Invalid input. Try again.\n")
                        continue

            state = self.succ(state, action)
            turns += 1

            if self.isEnd(state):
                if not simulate:
                    print(f"Game over! Player {self.current_player} wins!")
                break

            self.current_player = 1 - self.current_player

        return {
            "winner": self.current_player,
            "minimax_player": flip,
            "minimax_bot_wins": self.current_player == flip,
            "turns": turns,
            "max_depth": self.depth,
            "avg_minimax_time": sum(self.minimax_times) / len(self.minimax_times) if self.minimax_times else 0,
            "heaps": str(self.heaps)
        }

def generate_random_heaps(min_heaps=2, max_heaps=5, min_size=1, max_size=5):
    return [random.randint(min_size, max_size) for _ in range(random.randint(min_heaps, max_heaps))]

def run_loop(mode="human_vs_bot", n_games=1, output_file="nim_data.csv"):
    results = []
    for i in range(n_games):
        print(f"\n========== Game {i + 1} / {n_games} ==========")
        heaps = generate_random_heaps()
        game = Game(heaps)
        stats = game.play(mode=mode, simulate=(mode == "random_vs_bot"))
        stats["game_number"] = i + 1
        results.append(stats)

    df = pd.DataFrame(results)
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
    parser.add_argument("--output", type=str, default="nim_data.csv", help="Output CSV filename")
    args = parser.parse_args()

    run_loop(mode=args.mode, n_games=args.games, output_file=args.output)