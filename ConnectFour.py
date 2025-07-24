import random
import copy
import time
import math
import pandas as pd

# GLOBAL cache shared across all games
global_cache = {}

class Connect4:
    def __init__(self):
        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.maxdepth = 0
        self.count = 0
        self.cache = global_cache
        self.minimax_times = []
        self.minimax(self.startState(), True, 0)

    def startState(self):
        return (copy.deepcopy(self.board), 0)

    def actions(self, state):
        board, _ = state
        return [str(i) for i in range(4) if board[0][i] == ' ']

    def succ(self, state, action):
        board, player = state
        boardcopy = copy.deepcopy(board)
        col = int(action)
        token = 'X' if player == 1 else 'O'
        for i in range(3, -1, -1):
            if boardcopy[i][col] == ' ':
                boardcopy[i][col] = token
                break
        return (boardcopy, 1 - player)

    def isEnd(self, state):
        board, _ = state

        # Horizontal and vertical
        for i in range(4):
            if board[i][0] == board[i][1] == board[i][2] == board[i][3] != ' ':
                return True, True
            if board[0][i] == board[1][i] == board[2][i] == board[3][i] != ' ':
                return True, True

        # Diagonal
        if board[3][0] == board[2][1] == board[1][2] == board[0][3] != ' ':
            return True, True
        if board[3][3] == board[2][2] == board[1][1] == board[0][0] != ' ':
            return True, True

        # Check if board is full
        for row in board:
            if ' ' in row:
                return False, False

        return True, False

    def utility(self, state):
        if self.isEnd(state)[1]:
            return -1 if state[1] == 0 else 1
        return 0

    def board_to_tuple(self, state):
        board, player = state
        return (tuple(tuple(row) for row in board), player)

    def minimax(self, state, maximizingPlayer, depth):
        key = (self.board_to_tuple(state), maximizingPlayer)
        if key in self.cache:
            return self.cache[key] + (depth,)

        if self.isEnd(state)[0]:
            return self.utility(state), None, depth

        best_action = None
        if maximizingPlayer:
            maxEval = -2
            for action in self.actions(state):
                eval, _, d = self.minimax(self.succ(state, action), False, depth + 1)
                if eval > maxEval:
                    maxEval = eval
                    best_action = action
            self.cache[key] = (maxEval, best_action)
            return maxEval, best_action, depth
        else:
            minEval = 2
            for action in self.actions(state):
                eval, _, d = self.minimax(self.succ(state, action), True, depth + 1)
                if eval < minEval:
                    minEval = eval
                    best_action = action
            self.cache[key] = (minEval, best_action)
            return minEval, best_action, depth

    def play(self, mode="human_vs_bot", simulate=False):
        state = self.startState()
        flip = random.randint(0, 1)  # bot player index
        self.count = 0
        self.maxdepth = 0
        self.minimax_times = []

        while not self.isEnd(state)[0]:
            board, player = state
            if player == flip:
                start = time.time()
                _, action, d = self.minimax(state, flip == 0, self.count)
                self.maxdepth = max(self.maxdepth, 16 - d)
                self.minimax_times.append(time.time() - start)
            else:
                if mode == "random_vs_bot" or simulate:
                    action = random.choice(self.actions(state))
                else:
                    print("\n".join(["| " + " | ".join(row) + " |" for row in board]))
                    print("  " + "   ".join(map(str, range(len(board)))))
                    action = None
                    valid = self.actions(state)
                    while action not in valid:
                        action = input(f"Player {player}, choose a column {valid}: ")

            state = self.succ(state, action)
            self.count += 1

        final_board, _ = state
        if not simulate and mode == "human_vs_bot":
            print("\nFinal board:")
            print("\n".join(["| " + " | ".join(row) + " |" for row in board]))
            print("  " + "   ".join(map(str, range(len(board)))))

        win, ended = self.isEnd(state)
        result = {
            "winner": (1 - state[1]) if ended else "Draw",
            "bot_player": flip,
            "bot_wins": (1 - state[1]) == flip if ended else False,
            "moves": self.count,
            "depth": self.maxdepth,
            "avg_minimax_time": sum(self.minimax_times) / len(self.minimax_times) if self.minimax_times else 0
        }
        return result

def run_loop(mode="human_vs_bot", n_games=1, output_file="connect4_data.csv"):
    results = []
    for i in range(n_games):
        print(f"\n========== Game {i + 1} / {n_games} ==========")
        game = Connect4()
        result = game.play(mode=mode, simulate=(mode == "random_vs_bot"))
        result["game_number"] = i + 1
        results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\n[INFO] Saved results to {output_file}")
    print(f"[INFO] Bot win rate: {(df['bot_wins'].mean() * 100):.2f}%")

# ===== Main Entry =====
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["human_vs_bot", "random_vs_bot"], required=True)
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--output", type=str, default="connect4_data.csv")
    args = parser.parse_args()

    run_loop(mode=args.mode, n_games=args.games, output_file=args.output)