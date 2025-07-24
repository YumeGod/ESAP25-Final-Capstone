# ESAP25 Final Capstone  
**Strategic Game Analysis via Minimax Search: A Computational Study**  
**University of Pennsylvania | School of Engineering and Applied Science**  
**Date:** July 2025  

---

## 📘 Overview

This project investigates the performance of a recursive **minimax search algorithm** across four two-player, perfect-information games:

- **Halving Game**
- **Nim**
- **Tic-Tac-Toe**
- **Connect Four (4×4)**

Each game was implemented in Python and integrated with a unified minimax agent capable of simulating optimal decision-making. To ensure scalability and efficiency, state caching (memoization) was incorporated for all games except Halving.

The agent was tested in two experimental scenarios:
- **Against a random agent** (10,000 simulations)
- **Against a human player** (50 simulations)

The results offer insights into algorithmic performance, strategic depth, and human-agent interaction in adversarial environments.

---

## 📁 Repository Contents

```text
.
├── ConnectFour.py             # Connect Four game logic
├── Nim.py                     # Nim game logic
├── TicTacToe.py               # Tic-Tac-Toe logic
├── TheHalving.py              # Halving game logic
├── *_human.csv                # Game data of minimax agent vs human player
├── *_random.csv               # Game data of minimax agent vs random agent
└── graph.ipynb                # Jupyter notebook for visualizations
