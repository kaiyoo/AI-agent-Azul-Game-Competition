# AZUL game AI-agent competition
COMP90054(AI planning for Autonomy) in class competition - AI agent in Azul game

Project information in [project-info.md](https://github.com/kaiyoo/AI-azul/blob/master/project-info.md)

Video demo available is [here](https://youtu.be/vctpCTW8iWU)

## [1] Overview
This project was done as the final project of subject AI planning for autonomy. 

Ranked 12th out of 68 teams. 

Our team implemented 3 algorithms: Monte Carlo Tree Search, Deep Q-learning, Minimax.

Among above algorithms, I implemented both DQN and Minimax.

For our final agent, Minimax player was chosen. 

## [2] DQN
> In the demo, player0 (top) is naive player (baseline - simple strategy) and player1 (bottom) is DQN player.
> 
> At the end of the game, our DQN player beated naive player only by 1 point, which is not powerful...
> 
> Implementation of model training for DQN player is in [dqn_train_model.py] and implementation of DQN player is [/Alpha_Azul_20/dqn_player.py](players/Alpha_Azul_20/dqn_player.py)


![DQN Demo](img/dqn_demo.gif)

![alt text](img/dqn_design.PNG)


## [3] Minimax
> In the demo, player0 (top) is naive player (baseline - simple strategy) and player1 (bottom) is Minimax player.
> 
> At the end of the game, our Minimax player beated naive player by double (16-32), which is very powerful.
> 
> Look at the design of the agent. Besides this, many other strateges were considered (see my code below).
> 
> Implementation of Minimax is in [/Alpha_Azul_20/minimax_player.py](players/Alpha_Azul_20/minimax_player.py)


![Minimax Demo](img/minimax_demo.gif)

![alt text](img/minimax_design.PNG)

