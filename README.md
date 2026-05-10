# 🚜 Farm Incremental

**Farm Incremental** is a deep clicker-strategy game built with Python. Manage your farm, automate food production, and master the market through seasons, day/night cycles, and a complex prestige system.

## 🌟 Key Features

*   **Dynamic Seasons:** Spring, Summer, Autumn, and Winter affect crop growth speed and market prices.
*   **Day & Night Cycle:** Grow standard crops during the day and unlock mystical "night" plants like mushrooms and moon-berries.
*   **Massive Skill Tree:** Over 40 upgrades across categories like Basics, Farming, Automation, Chefs, and Prestige.
*   **Food Factory:** Design conveyor lines and use machinery (boilers, fryers, ovens) to create complex dishes for massive profits.
*   **Prestige System:** Reset your progress to gain Prestige Points (PP), unlocking permanent, game-changing buffs.
*   **Living Economy:** Prices fluctuate based on supply. If you flood the market with one crop, its price drops. Use price charts to maximize gains.

## 🛠 Tech Stack

*   **Language:** Python 3.x
*   **Engine:** [Pygame](https://pygame.org)
*   **Data Storage:** JSON with basic XOR encryption to protect save files.

## 🚀 Getting Started

1.  **Ensure Python is installed.**
2.  **Install Pygame dependency:**
    ```bash
    pip install pygame
    ```
3.  **Clone the repository:**
    ```bash
    git clone https://github.com
    cd Game
    ```
4.  **Launch the game:**
    ```bash
    python game.py
    ```

> **Note:** The game looks best with the pixel font located in `fonts/vyazpixel.ttf`. If missing, the game will fallback to Arial.

## 🎮 Controls

*   **Left Click (LMB):** Interact with buttons, crops, and factory objects.
*   **ESC:** Open the Skill Tree or go back to the main menu.
*   **Space:** Fast-forward time (requires specific skill unlock).

## 📊 Project Structure

*   `game.py` — The core engine containing:
    *   `GameState`: Manages economy, inventory, and progression.
    *   `FoodFactory`: The logic behind automation and conveyor systems.
    *   `SKILL_TREE`: Configuration for all available upgrades.
    *   `save_game` / `load_game`: 3-slot save system implementation.

## 📈 Roadmap

- [ ] New factory machinery types.
- [ ] Global Achievement system.
- [ ] Sound effects and background music.
- [ ] Full English localization for in-game text.
