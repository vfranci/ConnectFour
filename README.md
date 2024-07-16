# Connect Four AI with Alpha-Beta Pruning and Q-Learning

This Python project enhances the classic Connect Four game with two sophisticated AI strategies: Alpha-Beta Pruning and Q-Learning. The Alpha-Beta Pruning AI serves as a benchmark opponent to train the Q-Learning agent, providing a robust adversary for adaptive learning.

## Project Description

This project implements a Connect Four game with advanced AI components. The primary goal is to train a Q-Learning agent using reinforcement learning techniques, with the Alpha-Beta Pruning algorithm acting as a challenging opponent. By playing against a strong, pre-programmed AI, the Q-Learning agent can develop more sophisticated strategies and improve its performance over time.

## How It Works
- Alpha-Beta Pruning AI: This AI uses the Alpha-Beta Pruning technique to evaluate potential moves efficiently, providing a challenging opponent for the Q-Learning agent. It prunes unnecessary branches in the decision tree, reducing the number of nodes evaluated and thus speeding up the decision-making process.

- Q-Learning AI: This AI starts with no prior knowledge and learns by playing multiple games. It updates its Q-table based on the rewards it receives from different states and actions, gradually improving its strategy. The training process involves the Q-Learning agent playing against the Alpha-Beta Pruning AI.

## Key Features
- Connect Four Gameplay: Play the classic Connect Four game.
- Alpha-Beta Pruning AI: An efficient and strong opponent using the Alpha-Beta Pruning algorithm to minimize search depth and make optimal moves.
- Q-Learning AI: An adaptive AI agent that learns from its experiences, improving its strategy over time through reinforcement learning.
- Customizable Parameters: Configure various parameters for both the game and the learning process, including learning rate, discount factor, and exploration rate.

## Notes and comments

- This project is an enhancement of an X/0 game.
- There is also an implementation for a human versus Q-Learning agent gameplay.
