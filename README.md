# Pong-Game-Bot

Python2 Pong Bot using Q-learning machine learning algorithm.

I implemented the movement logic for the ball, the enemy and the agent. 

For the graphical part I used pygame. (pip2 install pygame)

Q-learning:
1. Learning rate (determines which percentage of the new info will replace the current one) - if the learning rate is 0, the agent won't learn, it it's closer to 1, the algorithm will take into consideration only the newest info.
2. Discount factor (the importance of the next reward) - if it's 0 the agent will take into consideration only the current rewards. Being a deterministic game, the discount factor doesn't have a significant effect on the learning process.
3. Epsilon (the randomness of the algorithm) - if it's 0, the algorithm picks the best action, if it has a higher value, the possibility to pick a random action is higher.
4. No. of train episodes - if the number is lower, the algorithm can not learn enough and the game will be over fast. The higher the number, the better is the environment exploration ( ex. 5000 train episodes). 
  
Python2 example : python2 q_learning_skel.py --plot --final_show_pygame --train_episodes 50


![Terminal Screenshot](https://github.com/sabinahorincar/pong-game-bot/blob/master/screenshots/terminal-screenshot.png)
![Pygame Screenshot](https://github.com/sabinahorincar/pong-game-bot/blob/master/screenshots/pygame-screenshot.png) 
