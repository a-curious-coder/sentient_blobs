# Sentient Blobs

Sentient Blobs is an agar.io game clone where players are neat ai agents that control blobs that interact with their environment. The goal is for the blobs to eat as much food and players as they can. 

<!-- ![Placeholder Image](https://placehold.co/1000x400?font=roboto) -->
![Placeholder Image](https://c.tenor.com/0gKp5z1EVIwAAAAC/tenor.gif)


## Setup

To set up the Sentient Blobs project, follow these steps:
### Windows
1. Create a virtual environment: `virtualenv .venv`
2. Activate the virtual environment: `.venv\Scripts\activate`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Run the `neat-ai.py` file to train the agents: `python neat-ai.py`

### Linux/MacOS
1. Create a virtual environment: `virtualenv .venv`
2. Activate the virtual environment:
    - For Windows: `.venv\Scripts\activate`
    - For macOS/Linux: `source .venv/bin/activate`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Run the `neat-ai.py` file to train the agents: `python neat-ai.py`

That's it! You are now ready to play Sentient Blobs.

## Usage
When agents are training, click on any one to see the nearest three food items and three nearest players

## Inputs
Each blob's neural network receives inputs to best determine the next action
- Current

## Fitness Function
<!-- This will have to be updated in accordance with the fitness function being changed -->
The fitness function is the what determines how well an agent is doing. The fitness of a blob is calculated by their score. The player loses mass every 0.2 seconds to encourage eating.

## Deployment 
Since the game was made using the Pygame library, the only viable way I could find to deploy it to web was using pygbag. Pygbag is a library that allows pygame to be run in the browser. The only downside is that it is slow but also limited with regards to certain features that would work in pygame but not in pygbag. E.g. File drag and drop.

Moreover, the neat-python library isn't really supported as it reads the 'neat' import within the main.py file. However, the workaround was downloading the neat-python source files and importing them ALL directly into main. Sorted. I believe this small workaround and discovery will unlock a lot of potential for pygame games to be deployed to the web with neat ai.

## Citations
[Neataptic](https://wagenaartje.github.io/neataptic/articles/agario/)
[neat-python](https://neat-python.readthedocs.io/en/latest/)



