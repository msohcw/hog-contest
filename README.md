## Hog Contest

This program develops a strategy to play the two-player game of Hog (CS61A Fall '16). The game is simulated in C++, and the strategy is learned over time using reinforcement learning, specifically, tabular Q-learning. 

* memory.in stores the latest strategy being trained against
* memory.50000 is the strategy trained over 50000 epochs
* viz.py creates a visualization of a given strategy
* hog_rl.cpp compiles to hog, hog_cv and hog_in_to_py
  * hog is the main file, run this to train the strategy
  * hog_cv is for cross validating across strategies, to compare strategies directly
  * hog_in_to_py converts a .in file to a list.py file which is in the format of a python list. Append this to viz.py for visualization
