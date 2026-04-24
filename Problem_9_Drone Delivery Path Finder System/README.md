📖 Problem Description

This project focuses on solving a grid-based pathfinding problem in the context of a drone delivery system. The environment is modeled as a two-dimensional matrix where each cell represents either a traversable space or a restricted zone:

0 → Free path (accessible for drone movement)
1 → Obstacle (no-fly zone)

Given a predefined start position (source) and goal position (destination), the objective is to determine a valid path that allows the drone to reach its destination while avoiding obstacles.
The system not only identifies feasible paths but also evaluates their efficiency using different search strategies. It provides both visual representation and analytical insights into how different algorithms behave in the same environment.

Algorithms 

1. Breadth-First Search (BFS)

Breadth-First Search is a graph traversal algorithm that explores nodes level by level starting from the source node. It uses a queue (FIFO) data structure to systematically visit all neighboring nodes before moving to the next level.
Guarantees the shortest path in an unweighted grid
Explores all possible directions uniformly
Suitable for optimal pathfinding scenarios

2. Depth-First Search (DFS)

Depth-First Search is a traversal algorithm that explores as far as possible along a branch before backtracking. It uses recursion or a stack (LIFO) to dive deep into the search space.
Does not guarantee the shortest path
Can be faster in reaching a solution in certain cases
Useful for exploring all possible paths

Execution Steps

Download or clone the repository from GitHub.
Open the project folder containing the source files.
Run the project by executing the main.py file:
python main.py
Create or load a grid environment for the simulation.
Enter the required inputs such as:
Start position
Goal position
Obstacles (optional)
Click the “Run BFS” or “Run DFS” button to execute the algorithms.
The system generates outputs including:
Path from start to goal
Path length
Number of nodes explored
Execution time
Visual grid representation
Comparison between BFS and DFS performance

Sample Output

![BFS](assets/screenshots/BFS.png)

![DFS](assets/screenshots/DFS.png)

