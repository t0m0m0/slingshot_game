# Slingshot Physics Game

A simple physics-based slingshot game built with Pygame. Launch projectiles to hit targets while navigating around obstacles.

## Features

- Physics-based projectile motion with gravity and air resistance
- Multiple levels with increasing difficulty
- Obstacles and targets with collision detection
- Visual effects including projectile trails and hit animations
- Simple trajectory prediction when aiming

## How to Play

1. Drag the projectile to aim
2. Release to fire
3. Hit all targets to complete the level
4. Progress through increasingly difficult levels

## Controls

- **Mouse Click and Drag**: Aim the slingshot
- **Mouse Release**: Fire the projectile
- **Click**: Continue to next level after completing a level

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/slingshot-game.git
cd slingshot-game
```

2. Install the required dependencies:
```bash
pip install pygame
```

3. Run the game:
```bash
cd src
./run.sh
```

Or directly:
```bash
python3 src/slingshot_game.py
```

## Project Structure

```
slingshot_game/
├── assets/
│   ├── images/
│   └── sounds/
├── docs/
├── src/
│   ├── slingshot_game.py
│   └── run.sh
└── README.md
```

## Physics Implementation

The game implements several physics concepts:
- Projectile motion under gravity
- Elastic and inelastic collisions
- Air resistance (drag)
- Friction on surfaces

## Future Enhancements

- Sound effects and background music
- More levels with varied obstacles
- Different projectile types with unique properties
- Power-ups and special abilities
- Score tracking and high scores

## License

This project is licensed under the MIT License - see the LICENSE file for details.
