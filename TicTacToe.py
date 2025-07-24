import random
import copy
import time
import math
import pandas as pd
from functools import lru_cache

class Tictactoe:
    def __init__(self, board=None):
        self.board = board if board else [[" "]*3 for _ in range(3)]
        self.minimax_times = []
        self.depth = 0

    def startState(self):
        return (copy.deepcopy(self.board), 0)

    def actions(self, state):
        board, _ = state
        acts = {}
        for i in range(3):
            row_actions = []
            for j in range(3):
                if board[i][j] == " ":
                    row_actions.append(str(j))
            if row_actions:
                acts[str(i)] = row_actions
        return acts

    def succ(self, state, action):
        board, player = state
        boardcopy = copy.deepcopy(board)
        symbol = "X" if player == 1 else "O"
        boardcopy[int(action[0])][int(action[1])] = symbol
        return (boardcopy, 1 - player)

    def isEnd(self, state):
        board, _ = state
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return (True, True)
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return (True, True)
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return (True, True)
        if board[2][0] == board[1][1] == board[0][2] != " ":
            return (True, True)
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    return (False, False)
        return (True, False)

    def utility(self, state):
        end, win = self.isEnd(state)
        if win:
            return -1 if state[1] == 0 else 1
        return 0

    def board_to_tuple(self, board):
        return tuple(tuple(row) for row in board)

    def minimax(self, state, maximizingPlayer):
        board_tuple = self.board_to_tuple(state[0])
        value, action, full_depth = cached_minimax(board_tuple, state[1], maximizingPlayer, 0)
        self.depth = full_depth
        return value, action

    def random_action(self, state):
        actions = self.actions(state)
        r = random.choice(list(actions.keys()))
        c = random.choice(actions[r])
        return r, c

    def play(self, mode="human_vs_bot", simulate=False):
        state = self.startState()
        flip = random.randint(0, 1)
        self.minimax_times = []
        move_count = 0
        game_depths = []

        if not simulate:
            print(f"\nMinimax bot is Player {flip}\n")

        while not self.isEnd(state)[0]:
            board, player = state
            if not simulate:
                for row in range(3):
                    print("│".join(f" {cell} " for cell in board[row]))
                    if row < 2:
                        print("───+───+───")
                print("\n")

            if player == flip:
                start_time = time.time()
                _, action = self.minimax(state, flip == 0)
                self.minimax_times.append(time.time() - start_time)
                game_depths.append(self.depth)
                if not simulate:
                    print(f"Bot chooses: row {action[0]}, col {action[1]}")
            else:
                if mode == "random_vs_bot" or simulate:
                    action = self.random_action(state)
                else:
                    actions = self.actions(state)
                    action = None
                    while not action or action[0] not in actions or action[1] not in actions[action[0]]:
                        row = input("Choose row (0-2): ").strip()
                        col = input("Choose col (0-2): ").strip()
                        action = (row, col)

            state = self.succ(state, action)
            move_count += 1

        result = self.isEnd(state)
        win_player = 1 - state[1]
        if not simulate:
            if result[1]:
                print(f"\nGame over! Player {win_player} wins!")
            else:
                print("\nGame over! It's a tie!")

        return {
            "moves": move_count,
            "winner": win_player if result[1] else -1,
            "minimax_bot_wins": win_player == flip if result[1] else False,
            "tie": not result[1],
            "minimax_player": flip,
            "max_depth": max(game_depths) if game_depths else 0,
            "avg_minimax_time": sum(self.minimax_times) / len(self.minimax_times) if self.minimax_times else 0
        }

@lru_cache(maxsize=None)
def cached_minimax(board_tuple, player, maximizingPlayer, current_depth):
    board = [list(row) for row in board_tuple]
    state = (board, player)

    game = Tictactoe(board)
    if game.isEnd(state)[0]:
        return game.utility(state), None, current_depth

    best_action = None
    if maximizingPlayer:
        maxEval = float('-inf')
        max_depth_reached = current_depth
        for r in game.actions(state):
            for c in game.actions(state)[r]:
                next_state = game.succ(state, (r, c))
                board_key = game.board_to_tuple(next_state[0])
                eval, _, depth_reached = cached_minimax(board_key, next_state[1], False, current_depth + 1)
                if eval > maxEval:
                    maxEval = eval
                    best_action = (r, c)
                max_depth_reached = max(max_depth_reached, depth_reached)
        return maxEval, best_action, max_depth_reached
    else:
        minEval = float('inf')
        max_depth_reached = current_depth
        for r in game.actions(state):
            for c in game.actions(state)[r]:
                next_state = game.succ(state, (r, c))
                board_key = game.board_to_tuple(next_state[0])
                eval, _, depth_reached = cached_minimax(board_key, next_state[1], True, current_depth + 1)
                if eval < minEval:
                    minEval = eval
                    best_action = (r, c)
                max_depth_reached = max(max_depth_reached, depth_reached)
        return minEval, best_action, max_depth_reached

def run_loop(mode="human_vs_bot", n_games=1, output_file="tictactoe_data.csv"):
    all_results = []
    for i in range(n_games):
        print(f"\n======== Game {i + 1} / {n_games} ========")
        game = Tictactoe()
        stats = game.play(mode=mode, simulate=(mode == "random_vs_bot"))
        stats["game_number"] = i + 1
        all_results.append(stats)

    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False)
    print(f"\n[INFO] Saved {n_games} game results to '{output_file}'")
    print(f"[INFO] Minimax bot win rate: {df['minimax_bot_wins'].mean() * 100:.2f}%")
    print(f"[INFO] Tie rate: {df['tie'].mean() * 100:.2f}%")
    return df

# ========== CLI ==========
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["human_vs_bot", "random_vs_bot"], required=True, help="Game mode")
    parser.add_argument("--games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--output", type=str, default="tictactoe_data.csv", help="Output CSV filename")
    args = parser.parse_args()

    run_loop(mode=args.mode, n_games=args.games, output_file=args.output)