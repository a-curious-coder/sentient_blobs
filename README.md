## Inputs
- 10 nearest players (euclidean distances)
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
- Player doesn't move away from wall 5 more seconds
- Player doesn't eat something for 5 more seconds
- Player doesn't move for 5 more seconds
- Player score doesn't change for 10 seconds
# Rewards
## Player eats food
- Increment score
- Increase size
## Player eats player
- Increase score by 2/3rds
- Increase size by 2/3rds opposing player's radius
## Player travels 250 pixels
- Travel points