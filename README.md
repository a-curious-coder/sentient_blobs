# Sentient Blobs

![Placeholder Image](https://placehold.co/1000x400?font=roboto)

## Overview

Sentient Blobs is a game where players control blobs that interact with their environment. The blobs can eat food, interact with other players, and navigate the game world.

## Inputs
- Player position x
- Player position y
- Player score
- Player radius

- 10 nearest players (euclidean distances)
- 10 nearest players sizes (to identify larger players)
- 10 nearest pieces of food

- Distance to right side of screen
- Distance to top of screen
- Distance to bottom of screen
- Distance to left of screen


# Punishments

## Reduce score by 15%

- Player stays still for 5 seconds
- Player loiters around walls for 5 seconds
- Player doesn't eat something for 5 seconds

## Reduce score by 35%

- Player stays still for additional 5 seconds
- Player loiters around walls for additional 5 seconds
- Player doesn't eat something for additional 5 seconds

## Kill player

- Player doesn't move away from wall for 5 more seconds
- Player doesn't eat something for 5 more seconds
- Player doesn't move for 5 more seconds
- Player score doesn't change for 10 seconds

# Rewards

## Player eats food

- Increment score
- Increase size

## Player eats player

- Increase score by 2/3rds
- Increase size by 2/3rds of the opposing player's radius

## Player travels 250 pixels

- Travel points

## Setup Guide

To set up the Sentient Blobs project, follow these steps:

1. Clone the repository: `git clone https://github.com/username/sentient-blobs.git`
2. Navigate to the project directory: `cd sentient-blobs`
3. Install the required dependencies: `npm install`
4. Start the game: `npm start`

That's it! You are now ready to play Sentient Blobs.
