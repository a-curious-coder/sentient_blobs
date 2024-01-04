# Sentient Blobs

Sentient Blobs is an agar.io game clone where players are neat ai agents that control blobs that interact with their environment. The goal is for the blobs to eat as much food and players as they can. 

![Placeholder Image](https://placehold.co/1000x400?font=roboto)


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

## Citations
[Neataptic](https://wagenaartje.github.io/neataptic/articles/agario/)



