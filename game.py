import pygame
import json
import base64
import os
import sys
from collections import defaultdict
import math
import random

# ====================== НАСТРОЙКИ ======================
FULLSCREEN = True
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 720
FPS = 30
SAVE_SLOTS = 3
SAVE_TEMPLATE = "farm_save_{}.dat"
ENCRYPTION_KEY = "KEY"
SEASON_DAYS = 10
LANG = "ru"

def load_font(size):
    try:
        return pygame.font.Font("fonts/vyazpixel.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size)

TEXTS = {
    "ru": {
        "main_title": "Ферма Инкрементал",
        "slot": "Слот {}",
        "load_game": "Загрузить",
        "new_game": "Новая игра",
        "exit": "Выход",
        "save_corrupted": "Сохранение повреждено. Новая игра.",
        "day_phase": "День {} ({})",
        "money": "Деньги: {}",
        "time_left": "Время: {}",
        "skip_power": "Пропуск: {}с",
        "season": "Сезон: {}",
        "plot": "Участок {}",
        "long_plot": "Долгий уч. {}",
        "empty_plot": "Пусто",
        "ready": "ГОТОВ",
        "harvest": "Собрать",
        "plant": "Посадить",
        "sell_all": "Продать всё",
        "skip_button": "Пропустить время ({}с)",
        "inventory": "Инвентарь",
        "cooked_inv": "Готовые блюда",
        "hub_title": "Развитие фермы",
        "back_to_game": "Вернуться к игре",
        "back": "← Назад",
        "learn_skill": "Изучить",
        "bought": "Изучено: {}",
        "cant_buy": "Не выполнены условия",
        "need_money": "Недостаточно денег",
        "need_prereq": "Требуется: {}",
        "need_pp": "Недостаточно очков престижа",
        "tab_unlocked": "Открыта страница: {}",
        "prestige_done": "Престиж выполнен! Получено {} PP.",
        "day_ended": "День {} закончен! Откройте древо навыков (ESC).",
        "phase_msg": "Фаза: {}",
        "save_exit": "Сохранить и выйти",
        "no_seeds": "Нет доступных семян!",
        "sold_for": "Продано на {}",
        "skipped": "Пропущено {}с",
        "price_chart": "График цен",
        "farmers": "Фермеры: {} (свободно: {})",
        "assign_farmer": "+Ф",
        "remove_farmer": "-Ф",
        "factory": "Фабрика еды",
        "factory_place": "Разместить",
        "factory_delete": "Удалить",
        "factory_input": "Вход",
        "factory_machine": "Станок",
        "factory_output": "Выход",
        "factory_autosell": "Авто-продажа",
        "factory_conveyor": "Конвейер",
        "factory_operation": "Операция",
        "factory_select_veg": "Выбрать ингредиент",
        "factory_direction": "Направление (→←↓↑)",
        "factory_no_recipe": "Экспериментируйте!",
        "factory_boil": "Варка (2 разн.)",
        "factory_fry": "Жарка (1)",
        "factory_cut": "Резка (3 разн.)",
        "factory_bake": "Запекание (2 разн.)",
        "eternal": "Вечные",
        "prestige_points": "Очки престижа: {}",
    }
}
def t(key, *args):
    txt = TEXTS[LANG].get(key, key)
    return txt.format(*args) if args else txt

# ====================== Игровые данные ======================
SEASONS = [
    {"name": "Весна", "day_len": 50, "night_len": 40, "growth_mod": 1.2, "price_mod": 1.0,
     "bg_color": (200, 255, 200), "header_color": (100, 180, 100)},
    {"name": "Лето",  "day_len": 70, "night_len": 20, "growth_mod": 0.9, "price_mod": 1.1,
     "bg_color": (255, 255, 180), "header_color": (255, 200, 0)},
    {"name": "Осень", "day_len": 40, "night_len": 50, "growth_mod": 1.1, "price_mod": 1.2,
     "bg_color": (255, 220, 180), "header_color": (200, 100, 50)},
    {"name": "Зима",  "day_len": 30, "night_len": 60, "growth_mod": 0.7, "price_mod": 0.8,
     "bg_color": (200, 220, 255), "header_color": (100, 150, 200)},
]

VEGETABLES = {
    "potato": {"name": "Картофель", "base_price": 5, "growth_time": 10, "seed_cost": 2, "min_yield": 0, "max_yield": 10, "unlock": "always", "day": True},
    "carrot": {"name": "Морковь", "base_price": 8, "growth_time": 15, "seed_cost": 5, "min_yield": 0, "max_yield": 10, "unlock": "carrot", "day": True},
    "tomato": {"name": "Помидор", "base_price": 12, "growth_time": 20, "seed_cost": 8, "min_yield": 0, "max_yield": 10, "unlock": "tomato", "day": True},
    "cucumber": {"name": "Огурец", "base_price": 10, "growth_time": 18, "seed_cost": 6, "min_yield": 0, "max_yield": 10, "unlock": "cucumber", "day": True},
    "pepper": {"name": "Перец", "base_price": 15, "growth_time": 25, "seed_cost": 10, "min_yield": 0, "max_yield": 10, "unlock": "pepper", "day": True},
    "zucchini": {"name": "Кабачок", "base_price": 14, "growth_time": 22, "seed_cost": 9, "min_yield": 0, "max_yield": 10, "unlock": "zucchini", "day": True},
    "eggplant": {"name": "Баклажан", "base_price": 16, "growth_time": 26, "seed_cost": 11, "min_yield": 0, "max_yield": 10, "unlock": "eggplant", "day": True},
    "pumpkin": {"name": "Тыква", "base_price": 18, "growth_time": 30, "seed_cost": 12, "min_yield": 0, "max_yield": 10, "unlock": "pumpkin", "day": True},
}
NIGHT_VEGETABLES = {
    "mushroom": {"name": "Гриб", "base_price": 20, "growth_time": 12, "seed_cost": 8, "min_yield": 0, "max_yield": 10, "unlock": "mushroom", "day": False},
    "moonberry": {"name": "Лунная ягода", "base_price": 30, "growth_time": 25, "seed_cost": 15, "min_yield": 0, "max_yield": 10, "unlock": "moonberry", "day": False},
    "ghost_pepper": {"name": "Призрачный перец", "base_price": 40, "growth_time": 35, "seed_cost": 20, "min_yield": 0, "max_yield": 10, "unlock": "ghost_pepper", "day": False},
}
LONG_VEGETABLES = {
    "apple": {"name": "Яблоня", "base_price": 120, "growth_days": 3, "seed_cost": 60, "min_yield": 5, "max_yield": 15, "unlock": "long_seeds"},
    "wine": {"name": "Виноград", "base_price": 200, "growth_days": 5, "seed_cost": 100, "min_yield": 8, "max_yield": 20, "unlock": "long_seeds"},
    "strawberry": {"name": "Клубника", "base_price": 80, "growth_days": 2, "seed_cost": 30, "min_yield": 3, "max_yield": 12, "unlock": "long_seeds"},
}

DISHES = {}  # динамически пополняется

SKILL_TREE = {
    "general": [
        {"id": "click_boost_1", "name": "Быстрый клик I", "desc": "+2 сек пропуска за клик", "cost": 20, "req": [], "effect": ("click_skip", 2)},
        {"id": "click_boost_2", "name": "Быстрый клик II", "desc": "+2 сек пропуска", "cost": 50, "req": ["click_boost_1"], "effect": ("click_skip", 2)},
        {"id": "click_boost_3", "name": "Быстрый клик III", "desc": "+2 сек пропуска", "cost": 100, "req": ["click_boost_2"], "effect": ("click_skip", 2)},
        {"id": "click_boost_4", "name": "Быстрый клик IV", "desc": "+2 сек пропуска", "cost": 200, "req": ["click_boost_3"], "effect": ("click_skip", 2)},
        {"id": "click_boost_5", "name": "Быстрый клик V", "desc": "+2 сек пропуска", "cost": 500, "req": ["click_boost_4"], "effect": ("click_skip", 2)},
        {"id": "speed1", "name": "Ускоренный рост I", "desc": "+10% скорости роста", "cost": 30, "req": [], "effect": ("growth_speed", 0.1)},
        {"id": "speed2", "name": "Ускоренный рост II", "desc": "ещё +10%", "cost": 80, "req": ["speed1"], "effect": ("growth_speed", 0.1)},
        {"id": "yield1", "name": "Урожайность I", "desc": "+1 к мин/макс урожаю", "cost": 30, "req": [], "effect": ("yield_bonus", 1)},
        {"id": "yield2", "name": "Урожайность II", "desc": "ещё +1", "cost": 80, "req": ["yield1"], "effect": ("yield_bonus", 1)},
        {"id": "price_boost", "name": "Лучшие цены", "desc": "Цены выше на 20%", "cost": 100, "req": [], "effect": ("price_mult", 0.2)},
    ],
    "farm": [
        {"id": "farm_expand_1", "name": "Расширение I", "desc": "2-й участок", "cost": 100, "req": [], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_2", "name": "Расширение II", "desc": "3-й участок", "cost": 250, "req": ["farm_expand_1"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_3", "name": "Расширение III", "desc": "4-й участок", "cost": 500, "req": ["farm_expand_2"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_4", "name": "Расширение IV", "desc": "5-й участок", "cost": 1000, "req": ["farm_expand_3"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_5", "name": "Расширение V", "desc": "6-й участок", "cost": 2000, "req": ["farm_expand_4"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_6", "name": "Расширение VI", "desc": "7-й участок", "cost": 4000, "req": ["farm_expand_5"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_7", "name": "Расширение VII", "desc": "8-й участок", "cost": 8000, "req": ["farm_expand_6"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_8", "name": "Расширение VIII", "desc": "9-й участок", "cost": 16000, "req": ["farm_expand_7"], "effect": ("extra_plots", 1)},
        {"id": "farm_expand_9", "name": "Расширение IX", "desc": "10-й участок", "cost": 32000, "req": ["farm_expand_8"], "effect": ("extra_plots", 1)},
        {"id": "night_farm", "name": "Ночной фарм", "desc": "Открывает ночную фазу", "cost": 400, "req": ["farm_expand_1", "speed2"], "effect": ("night_farm", True)},
        {"id": "mushroom", "name": "Грибы", "cost": 150, "req": ["night_farm"], "effect": ("unlock_crop", "mushroom")},
        {"id": "moonberry", "name": "Лунная ягода", "cost": 200, "req": ["night_farm"], "effect": ("unlock_crop", "moonberry")},
        {"id": "ghost_pepper", "name": "Призрачный перец", "cost": 250, "req": ["night_farm"], "effect": ("unlock_crop", "ghost_pepper")},
        {"id": "carrot", "name": "Морковь", "cost": 40, "req": ["farm_expand_1"], "effect": ("unlock_crop", "carrot")},
        {"id": "tomato", "name": "Помидор", "cost": 60, "req": ["farm_expand_1"], "effect": ("unlock_crop", "tomato")},
        {"id": "cucumber", "name": "Огурец", "cost": 50, "req": ["farm_expand_1"], "effect": ("unlock_crop", "cucumber")},
        {"id": "pepper", "name": "Перец", "cost": 70, "req": ["farm_expand_1"], "effect": ("unlock_crop", "pepper")},
        {"id": "zucchini", "name": "Кабачок", "cost": 80, "req": ["farm_expand_1"], "effect": ("unlock_crop", "zucchini")},
        {"id": "eggplant", "name": "Баклажан", "cost": 90, "req": ["farm_expand_1"], "effect": ("unlock_crop", "eggplant")},
        {"id": "pumpkin", "name": "Тыква", "cost": 100, "req": ["farm_expand_1"], "effect": ("unlock_crop", "pumpkin")},
        {"id": "long_expand_1", "name": "Сад I", "desc": "1 долгий участок", "cost": 500, "req": ["farm_expand_3"], "effect": ("extra_long_plots", 1)},
        {"id": "long_expand_2", "name": "Сад II", "desc": "2-й долгий участок", "cost": 1000, "req": ["long_expand_1"], "effect": ("extra_long_plots", 1)},
        {"id": "long_expand_3", "name": "Сад III", "desc": "3-й долгий участок", "cost": 2000, "req": ["long_expand_2"], "effect": ("extra_long_plots", 1)},
        {"id": "long_expand_4", "name": "Сад IV", "desc": "4-й долгий участок", "cost": 4000, "req": ["long_expand_3"], "effect": ("extra_long_plots", 1)},
        {"id": "long_expand_5", "name": "Сад V", "desc": "5-й долгий участок", "cost": 8000, "req": ["long_expand_4"], "effect": ("extra_long_plots", 1)},
        {"id": "long_seeds", "name": "Семена для сада", "desc": "Открывает многодневные культуры", "cost": 300, "req": ["long_expand_1"], "effect": ("unlock_long_crops", True)},
    ],
    "automation": [
        {"id": "auto_plant", "name": "Автозасев", "desc": "Автосажает под потребности фабрики", "cost": 150, "req": ["speed1", "yield1"], "effect": ("auto_plant", True)},
        {"id": "auto_harvest", "name": "Автосбор", "desc": "Автосбор урожая", "cost": 200, "req": ["auto_plant"], "effect": ("auto_harvest", True)},
        {"id": "auto_sell", "name": "Автопродажа", "desc": "Продажа в конце дня", "cost": 300, "req": ["auto_harvest"], "effect": ("auto_sell", True)},
        {"id": "auto_long_plant", "name": "Автозасев сада", "desc": "Автосажает в саду", "cost": 500, "req": ["long_seeds", "auto_plant"], "effect": ("auto_long_plant", True)},
        {"id": "auto_long_harvest", "name": "Автосбор сада", "desc": "Автосбор долгих культур", "cost": 600, "req": ["auto_long_plant"], "effect": ("auto_long_harvest", True)},
    ],
    "farmers": [
        {"id": "farmer_1", "name": "Фермер I", "desc": "+1 фермер", "cost": 200, "req": [], "effect": ("farmer", 1)},
        {"id": "farmer_2", "name": "Фермер II", "desc": "+1 фермер", "cost": 500, "req": ["farmer_1"], "effect": ("farmer", 1)},
        {"id": "farmer_3", "name": "Фермер III", "desc": "+1 фермер", "cost": 1200, "req": ["farmer_2"], "effect": ("farmer", 1)},
        {"id": "farmer_4", "name": "Фермер IV", "desc": "+1 фермер", "cost": 3000, "req": ["farmer_3"], "effect": ("farmer", 1)},
        {"id": "farmer_5", "name": "Фермер V", "desc": "+1 фермер", "cost": 8000, "req": ["farmer_4"], "effect": ("farmer", 1)},
    ],
    "cooking": [
        {"id": "cook_speed_1", "name": "Поварёшка", "desc": "Ручная готовка на 20% быстрее", "cost": 50, "req": [], "effect": ("cook_speed", 0.2)},
        {"id": "cook_speed_2", "name": "Сковорода", "desc": "Ещё +20%", "cost": 150, "req": ["cook_speed_1"], "effect": ("cook_speed", 0.2)},
        {"id": "auto_sell_cooked", "name": "Автопродажа блюд", "desc": "Авто-продажа готовых блюд в конце дня", "cost": 500, "req": ["cook_speed_1"], "effect": ("auto_sell_cooked", True)},
    ],
    "prestige": [
        {"id": "prestige_start", "name": "Престиж", "desc": "+20% к цене за сброс, даёт PP", "cost": 10000, "req": [], "effect": ("prestige", True)},
    ],
    "eternal": [
        {"id": "eternal_yield", "name": "Вечный урожай", "desc": "+1 к урожаю навсегда", "cost": 2, "req": [], "effect": ("eternal_yield", 1)},
        {"id": "eternal_speed", "name": "Вечная скорость", "desc": "+5% скорости роста навсегда", "cost": 3, "req": [], "effect": ("eternal_speed", 0.05)},
        {"id": "eternal_price", "name": "Вечная наценка", "desc": "+10% к цене навсегда", "cost": 5, "req": [], "effect": ("eternal_price", 0.1)},
        {"id": "eternal_farmer", "name": "Вечный фермер", "desc": "+1 фермер навсегда", "cost": 4, "req": [], "effect": ("eternal_farmer", 1)},
    ],
}

HUB_TABS = {
    "general":    {"name": "Базовые улучшения", "cost": 0,   "prereq": []},
    "farm":       {"name": "Ферма",            "cost": 100, "prereq": []},
    "automation": {"name": "Автоматика",       "cost": 300, "prereq": ["general"]},
    "farmers":    {"name": "Фермеры",          "cost": 500, "prereq": ["farm"]},
    "cooking":    {"name": "Готовка",          "cost": 5000, "prereq": ["prestige"]},
    "prestige":   {"name": "Престиж",          "cost": 1000,"prereq": ["general"]},
    "eternal":    {"name": "Вечные",           "cost": 0,   "prereq": ["prestige"], "require_prestige": True},
}

WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200); GREEN = (0, 200, 0); DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19); YELLOW = (255, 255, 0); BLUE = (0, 0, 255)
RED = (255, 0, 0); ORANGE = (255, 165, 0); PURPLE = (128, 0, 128)
NIGHT_BG = (25, 25, 50)

pygame.init()
if FULLSCREEN:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
else:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Farm Incremental")
clock = pygame.time.Clock()
font_small = load_font(16); font_medium = load_font(20); font_large = load_font(28)

# ====================== Шифрование ======================
def encrypt_data(data_str):
    data_bytes = data_str.encode('utf-8')
    key_bytes = ENCRYPTION_KEY.encode('utf-8')
    encrypted = bytes([data_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data_bytes))])
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_data(encrypted_str):
    try:
        encrypted = base64.b64decode(encrypted_str.encode('utf-8'))
        key_bytes = ENCRYPTION_KEY.encode('utf-8')
        decrypted = bytes([encrypted[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted))])
        return decrypted.decode('utf-8')
    except:
        return None

def format_money(amount):
    if amount < 1000: return f"{amount:.0f}"
    elif amount < 1_000_000: return f"{amount/1000:.1f}K"
    else: return f"{amount/1_000_000:.2f}M"

GRID_SIZE = 8
TILE_EMPTY = 0
TILE_INPUT = 1
TILE_MACHINE = 2
TILE_OUTPUT = 3
TILE_AUTOSELL = 4
TILE_CONVEYOR = 5

DIRS = [(1,0), (-1,0), (0,1), (0,-1)]

OPERATIONS = {
    "boil": {"name": "Варка", "need": 2},
    "fry":  {"name": "Жарка", "need": 1},
    "cut":  {"name": "Резка", "need": 3},
    "bake": {"name": "Запекание", "need": 2},
}

class FoodFactory:
    def __init__(self):
        self.grid = [[TILE_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.production_timer = 0.0

    def place(self, x, y, kind, info=None):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.grid[y][x] = kind
            self.data[y][x] = info

    def remove(self, x, y):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.grid[y][x] = TILE_EMPTY
            self.data[y][x] = None

    def get_tile(self, x, y):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return self.grid[y][x], self.data[y][x]
        return TILE_EMPTY, None

    def update(self, dt, game_state):
        if game_state.phase != "day":
            return
        self.production_timer += dt
        if self.production_timer < 0.5:
            return
        self.production_timer = 0.0

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == TILE_MACHINE:
                    info = self.data[y][x]
                    if not info or "operation" not in info:
                        continue
                    op = info["operation"]
                    needed = OPERATIONS[op]["need"]
                    connected_items = set()
                    visited = set()
                    queue = [(x, y)]
                    while queue:
                        cx, cy = queue.pop(0)
                        if (cx, cy) in visited: continue
                        visited.add((cx, cy))
                        if self.grid[cy][cx] == TILE_INPUT and self.data[cy][cx]:
                            connected_items.add(self.data[cy][cx])
                        for dx, dy in DIRS:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                                kind = self.grid[ny][nx]
                                if kind in (TILE_CONVEYOR, TILE_MACHINE, TILE_INPUT, TILE_OUTPUT, TILE_AUTOSELL):
                                    queue.append((nx, ny))
                    if len(connected_items) < needed:
                        continue
                    chosen = list(connected_items)[:needed]
                    can_produce = True
                    total_ingredient_cost = 0
                    for item in chosen:
                        if game_state.inventory.get(item, 0) < 1:
                            can_produce = False
                            break
                        item_data = game_state.get_item_data(item)
                        total_ingredient_cost += item_data.get("base_price", 0)
                    if not can_produce:
                        continue
                    production_cost = total_ingredient_cost * 0.2
                    if game_state.money < production_cost:
                        continue
                    game_state.money -= production_cost
                    for item in chosen:
                        game_state.inventory[item] -= 1
                    dish_id = f"{op}_" + "_".join(sorted(chosen))
                    dish_price = total_ingredient_cost * 10
                    if dish_id not in DISHES:
                        russian_name = game_state.generate_dish_name(dish_id)
                        DISHES[dish_id] = {"name": russian_name, "base_price": dish_price, "type": "dish"}
                    game_state.inventory[dish_id] += 1
                    placed = False
                    for dest in self._find_connected_outputs(x, y):
                        tx, ty, tkind = dest
                        if tkind == TILE_OUTPUT:
                            out_data = self.data[ty][tx]
                            if out_data is None: out_data = []
                            out_data.append(dish_id)
                            self.data[ty][tx] = out_data
                            placed = True
                            break
                        elif tkind == TILE_AUTOSELL:
                            game_state.money += dish_price * game_state.get_price_multiplier()
                            game_state.total_all_time_money += dish_price * game_state.get_price_multiplier()
                            placed = True
                            break
                    if not placed:
                        pass

    def _find_connected_outputs(self, start_x, start_y):
        outputs = []
        visited = set()
        queue = [(start_x, start_y)]
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited: continue
            visited.add((x, y))
            if self.grid[y][x] in (TILE_OUTPUT, TILE_AUTOSELL):
                outputs.append((x, y, self.grid[y][x]))
            for dx, dy in DIRS:
                nx, ny = x+dx, y+dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    kind = self.grid[ny][nx]
                    if kind in (TILE_CONVEYOR, TILE_MACHINE, TILE_INPUT, TILE_OUTPUT, TILE_AUTOSELL):
                        queue.append((nx, ny))
        return outputs

class GameState:
    def __init__(self):
        self.money = 50.0
        self.day = 1
        self.season_index = 0
        self.season_day = 1
        self.phase = "day"
        self.phase_time_left = SEASONS[0]["day_len"]
        self.skills = []
        self.plots = []
        self.night_plots = []
        self.long_plots = []
        self.plot_farmers = []
        self.inventory = defaultdict(int)
        self.unlocked_vegs = {"potato"}
        self.unlocked_long_vegs = set()
        self.market_supply = defaultdict(float)
        self.price_history = defaultdict(list)
        self.price_daily = defaultdict(list)
        self.max_plots = 1
        self.max_night_plots = 1
        self.max_long_plots = 0
        self.night_unlocked = False
        self.farmers = 0
        self.prestige_level = 0
        self.prestige_multiplier = 1.0
        self.total_all_time_money = 0.0
        self.unlocked_tabs = {"general"}
        self.factory = FoodFactory()
        self.eternal_bonuses = {
            "eternal_yield": 0,
            "eternal_speed": 0.0,
            "eternal_price": 0.0,
            "eternal_farmer": 0,
        }
        self.prestige_points = 0
        self.prestige_cost = 100000
        self.auto_sell_cooked = False
        self._init_plots()

    def _init_plots(self):
        while len(self.plots) < self.max_plots:
            self.plots.append({'crop': None, 'growth_timer': 0, 'max_time': 0})
        self.plots = self.plots[:self.max_plots]
        while len(self.night_plots) < self.max_night_plots:
            self.night_plots.append({'crop': None, 'growth_timer': 0, 'max_time': 0})
        self.night_plots = self.night_plots[:self.max_night_plots]
        while len(self.long_plots) < self.max_long_plots:
            self.long_plots.append({'crop': None, 'growth_timer': 0, 'max_time': 0})
        self.long_plots = self.long_plots[:self.max_long_plots]
        while len(self.plot_farmers) < self.max_plots:
            self.plot_farmers.append(0)
        self.plot_farmers = self.plot_farmers[:self.max_plots]

    def _update_phase_timer(self):
        season = SEASONS[self.season_index]
        self.phase_time_left = season["day_len"] if self.phase == "day" else season["night_len"]

    def recalc_from_skills(self):
        extra = 0; extra_long = 0
        self.farmers = self.eternal_bonuses.get("eternal_farmer", 0)
        self.auto_sell_cooked = False
        for sid in self.skills:
            node = self._skill_node(sid)
            if not node: continue
            eff = node["effect"]
            if eff[0] == "extra_plots": extra += eff[1]
            elif eff[0] == "extra_long_plots": extra_long += eff[1]
            elif eff[0] == "farmer": self.farmers += eff[1]
            elif eff[0] == "auto_sell_cooked": self.auto_sell_cooked = True
        if extra != self.max_plots - 1:
            self.max_plots = 1 + extra
            self.max_night_plots = self.max_plots
            self._init_plots()
        if extra_long != self.max_long_plots:
            self.max_long_plots = extra_long
            self._init_plots()
        self.night_unlocked = self.has_skill("night_farm")
        for tab in SKILL_TREE.values():
            for node in tab:
                if node["effect"][0] == "unlock_crop" and self.has_skill(node["id"]):
                    self.unlocked_vegs.add(node["effect"][1])
        self.unlocked_long_vegs.clear()
        if self.has_skill("long_seeds"):
            for key in LONG_VEGETABLES:
                if LONG_VEGETABLES[key]["unlock"] == "long_seeds":
                    self.unlocked_long_vegs.add(key)

    def get_item_data(self, key):
        if key in VEGETABLES: return VEGETABLES[key]
        if key in NIGHT_VEGETABLES: return NIGHT_VEGETABLES[key]
        if key in LONG_VEGETABLES: return LONG_VEGETABLES[key]
        if key in DISHES: return DISHES[key]
        return {"base_price": 0, "name": key}

    def generate_dish_name(self, dish_id):
        parts = dish_id.split('_')
        op = parts[0]
        ingredients = parts[1:]
        op_names = {"boil": "Варка", "fry": "Жарка", "cut": "Резка", "bake": "Запекание"}
        ing_names = []
        for ing in ingredients:
            if ing in VEGETABLES:
                ing_names.append(VEGETABLES[ing]["name"])
            elif ing in NIGHT_VEGETABLES:
                ing_names.append(NIGHT_VEGETABLES[ing]["name"])
            elif ing in LONG_VEGETABLES:
                ing_names.append(LONG_VEGETABLES[ing]["name"])
            elif ing in DISHES:
                ing_names.append(DISHES[ing]["name"])
            else:
                ing_names.append(ing)
        op_name = op_names.get(op, op)
        return f"{op_name} из {', '.join(ing_names)}"

    def _skill_node(self, sid):
        for tab in SKILL_TREE.values():
            for n in tab:
                if n["id"] == sid: return n
        return None

    def has_skill(self, sid): return sid in self.skills

    def get_skip_power(self):
        base = 2
        for sid in self.skills:
            node = self._skill_node(sid)
            if node and node["effect"][0] == "click_skip": base += node["effect"][1]
        return base

    def get_growth_multiplier(self):
        bonus = 0.0
        for sid in self.skills:
            node = self._skill_node(sid)
            if node and node["effect"][0] == "growth_speed": bonus += node["effect"][1]
        bonus += self.farmers * 0.03
        bonus += self.eternal_bonuses["eternal_speed"]
        season_mod = SEASONS[self.season_index]["growth_mod"]
        return (1.0 / (1.0 + bonus)) / season_mod

    def get_yield_bonus(self):
        bonus = 0
        for sid in self.skills:
            node = self._skill_node(sid)
            if node and node["effect"][0] == "yield_bonus": bonus += node["effect"][1]
        bonus += self.eternal_bonuses["eternal_yield"]
        return bonus

    def get_price_multiplier(self):
        bonus = 0.0
        for sid in self.skills:
            node = self._skill_node(sid)
            if node and node["effect"][0] == "price_mult": bonus += node["effect"][1]
        bonus += self.eternal_bonuses["eternal_price"]
        season_mod = SEASONS[self.season_index]["price_mod"]
        return (1.0 + bonus) * self.prestige_multiplier * season_mod

    def get_market_factor(self, veg_key):
        base = self.market_supply.get(veg_key, 0.0)
        factor = 2.0 * math.exp(-0.15 * base) + 0.3
        return max(0.3, min(2.5, factor))

    def _current_plots(self):
        return self.night_plots if self.phase == "night" else self.plots

    def plant(self, plot_index, veg_key):
        plots = self._current_plots()
        if plot_index >= len(plots): return False, "Нет такого участка"
        plot = plots[plot_index]
        if plot['crop'] is not None: return False, "Уже растёт"
        veg = self.get_item_data(veg_key)
        if veg_key not in self.unlocked_vegs: return False, "Семена недоступны"
        if self.money < veg["seed_cost"]: return False, t("need_money")
        self.money -= veg["seed_cost"]
        plot['crop'] = veg_key
        plot['growth_timer'] = veg["growth_time"] * self.get_growth_multiplier()
        plot['max_time'] = plot['growth_timer']
        return True, f"Посажен {veg['name']}"

    def plant_long(self, plot_index, veg_key):
        if plot_index >= len(self.long_plots): return False, "Нет такого долгого участка"
        plot = self.long_plots[plot_index]
        if plot['crop'] is not None: return False, "Уже растёт"
        veg = self.get_item_data(veg_key)
        if veg_key not in self.unlocked_long_vegs: return False, "Семена недоступны"
        if self.money < veg["seed_cost"]: return False, t("need_money")
        self.money -= veg["seed_cost"]
        day_len = SEASONS[self.season_index]["day_len"] + SEASONS[self.season_index]["night_len"]
        growth_sec = veg["growth_days"] * day_len * self.get_growth_multiplier()
        plot['crop'] = veg_key
        plot['growth_timer'] = growth_sec
        plot['max_time'] = growth_sec
        return True, f"Посажен {veg['name']}"

    def harvest(self, plot_index):
        plots = self._current_plots()
        if plot_index >= len(plots): return False, "Неверный участок"
        plot = plots[plot_index]
        if plot['crop'] is None or plot['growth_timer'] > 0: return False, "Нечего собирать"
        crop = plot['crop']
        veg = self.get_item_data(crop)
        bonus = self.get_yield_bonus()
        amount = random.randint(veg.get("min_yield",0)+bonus, veg.get("max_yield",10)+bonus)
        if amount < 0: amount = 0
        self.inventory[crop] += amount
        plot['crop'] = None
        plot['growth_timer'] = 0; plot['max_time'] = 0
        return True, f"Собрано {amount} шт."

    def harvest_long(self, plot_index):
        if plot_index >= len(self.long_plots): return False
        plot = self.long_plots[plot_index]
        if plot['crop'] is None or plot['growth_timer'] > 0: return False
        crop = plot['crop']
        veg = self.get_item_data(crop)
        bonus = self.get_yield_bonus()
        amount = random.randint(veg.get("min_yield",0)+bonus, veg.get("max_yield",20)+bonus)
        if amount < 0: amount = 0
        self.inventory[crop] += amount
        plot['crop'] = None; plot['growth_timer'] = 0; plot['max_time'] = 0
        return True, f"Собрано {amount} шт."

    def sell(self, item_key, amount=1):
        if self.inventory[item_key] < amount: return False, "Недостаточно товара"
        item = self.get_item_data(item_key)
        base = item.get("base_price", 0)
        factor = self.get_market_factor(item_key)
        dynamic_price = base * self.get_price_multiplier() * factor
        earned = dynamic_price * amount
        self.money += earned; self.total_all_time_money += earned
        self.inventory[item_key] -= amount
        self.market_supply[item_key] += amount * 0.2
        return True, f"Продано {amount} за {format_money(earned)}"

    def get_current_price(self, item_key):
        item = self.get_item_data(item_key)
        return item.get("base_price", 0) * self.get_price_multiplier() * self.get_market_factor(item_key)

    def skip_time(self, seconds):
        self.phase_time_left = max(0, self.phase_time_left - seconds)
        for plot in self.plots + self.night_plots + self.long_plots:
            if plot['crop'] and plot['growth_timer'] > 0:
                plot['growth_timer'] = max(0, plot['growth_timer'] - seconds)

    def get_factory_needs(self):
        needs = defaultdict(int)
        for my in range(GRID_SIZE):
            for mx in range(GRID_SIZE):
                if self.factory.grid[my][mx] == TILE_INPUT and self.factory.data[my][mx]:
                    veg = self.factory.data[my][mx]
                    connected = False
                    visited = set()
                    queue = [(mx, my)]
                    while queue and not connected:
                        cx, cy = queue.pop(0)
                        if (cx, cy) in visited: continue
                        visited.add((cx, cy))
                        if self.factory.grid[cy][cx] == TILE_MACHINE:
                            connected = True
                            break
                        for dx, dy in DIRS:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                                kind = self.factory.grid[ny][nx]
                                if kind in (TILE_CONVEYOR, TILE_INPUT, TILE_MACHINE, TILE_OUTPUT, TILE_AUTOSELL):
                                    queue.append((nx, ny))
                    if connected:
                        needs[veg] += 1
        return needs

    def auto_plant_best(self, plot_index):
        if not self.has_skill("auto_plant"): return False
        plots = self._current_plots()
        if plot_index >= len(plots): return False
        if plots[plot_index]['crop'] is not None: return False
        needs = self.get_factory_needs()
        if needs:
            available = {}
            for veg, cnt in needs.items():
                if veg in self.unlocked_vegs:
                    data = self.get_item_data(veg)
                    if (self.phase == "night" and not data.get("day", True)) or (self.phase == "day" and data.get("day", True)):
                        if self.money >= data["seed_cost"]:
                            available[veg] = cnt
            if available:
                total = sum(available.values())
                r = random.uniform(0, total)
                cum = 0
                for veg, cnt in available.items():
                    cum += cnt
                    if r <= cum:
                        return self.plant(plot_index, veg)[0]
        candidates = []
        for veg_key in self.unlocked_vegs:
            veg = self.get_item_data(veg_key)
            if not veg: continue
            if (self.phase=="night" and veg.get("day",True)) or (self.phase=="day" and not veg.get("day",True)):
                continue
            if self.money >= veg["seed_cost"]:
                bonus = self.get_yield_bonus()
                avg = (veg.get("min_yield",0)+veg.get("max_yield",10))/2 + bonus
                price = veg["base_price"] * self.get_price_multiplier() * self.get_market_factor(veg_key)
                grow = veg.get("growth_time",10) * self.get_growth_multiplier()
                candidates.append((avg*price/max(grow,1), veg_key))
        if not candidates: return False
        best = max(candidates, key=lambda x: x[0])[1]
        return self.plant(plot_index, best)[0]

    def update(self, dt):
        self.phase_time_left -= dt
        if self.has_skill("auto_harvest"):
            for plot in self._current_plots():
                if plot['crop'] and plot['growth_timer'] <= 0:
                    veg = plot['crop']
                    veg_data = self.get_item_data(veg)
                    bonus = self.get_yield_bonus()
                    amount = random.randint(veg_data.get("min_yield",0)+bonus, veg_data.get("max_yield",10)+bonus)
                    if amount > 0: self.inventory[veg] += amount
                    plot['crop'] = None; plot['growth_timer'] = 0; plot['max_time'] = 0
        if self.has_skill("auto_long_harvest"):
            for plot in self.long_plots:
                if plot['crop'] and plot['growth_timer'] <= 0:
                    crop = plot['crop']
                    veg = self.get_item_data(crop)
                    bonus = self.get_yield_bonus()
                    amount = random.randint(veg.get("min_yield",0)+bonus, veg.get("max_yield",20)+bonus)
                    if amount > 0: self.inventory[crop] += amount
                    plot['crop'] = None; plot['growth_timer'] = 0; plot['max_time'] = 0
        skip_power = self.get_skip_power()
        for i, plot in enumerate(self._current_plots()):
            if plot['crop'] and plot['growth_timer'] > 0:
                farmer_speed = self.plot_farmers[i] if i < len(self.plot_farmers) else 0
                plot['growth_timer'] -= farmer_speed * skip_power * dt
                if plot['growth_timer'] < 0: plot['growth_timer'] = 0
            plot['growth_timer'] -= dt
            if plot['crop'] and plot['growth_timer'] <= 0:
                plot['growth_timer'] = 0
        for plot in self.long_plots:
            if plot['crop'] and plot['growth_timer'] > 0:
                plot['growth_timer'] -= dt
                if plot['growth_timer'] <= 0: plot['growth_timer'] = 0
        if self.has_skill("auto_plant"):
            for i, plot in enumerate(self._current_plots()):
                if plot['crop'] is None:
                    self.auto_plant_best(i)
        if self.has_skill("auto_long_plant"):
            for i, plot in enumerate(self.long_plots):
                if plot['crop'] is None and self.unlocked_long_vegs:
                    veg = random.choice(list(self.unlocked_long_vegs))
                    self.plant_long(i, veg)
        self.factory.update(dt, self)
        if self.phase_time_left <= 0:
            return "phase_ended"
        return None

    def end_phase(self):
        if self.phase == "day":
            if self.night_unlocked:
                self.phase = "night"
                self._update_phase_timer()
                return False
            else:
                self._end_full_day()
                return True
        else:
            self.phase = "day"
            self._update_phase_timer()
            self._end_full_day()
            return True

    def _end_full_day(self):
        if self.has_skill("auto_sell"):
            for veg in list(self.inventory.keys()):
                while self.inventory[veg] > 0:
                    self.sell(veg, 1)
        if self.auto_sell_cooked:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    tkind, tdata = self.factory.get_tile(x, y)
                    if tkind == TILE_OUTPUT and tdata:
                        for dish_id in tdata:
                            if dish_id in DISHES:
                                price = DISHES[dish_id]["base_price"] * self.get_price_multiplier()
                                self.money += price
                                self.total_all_time_money += price
                        self.factory.data[y][x] = []
        for veg_key in set(list(self.unlocked_vegs) + list(self.unlocked_long_vegs)):
            price = self.get_current_price(veg_key)
            self.price_daily[veg_key].append((self.day, price))
        for dish_id in DISHES:
            price = DISHES[dish_id]["base_price"] * self.get_price_multiplier()
            self.price_daily[dish_id].append((self.day, price))
        self.day += 1
        self.season_day += 1
        if self.season_day > SEASON_DAYS:
            self.season_index = (self.season_index + 1) % len(SEASONS)
            self.season_day = 1
        for v in self.market_supply:
            self.market_supply[v] *= 0.8
        self.price_history.clear()
        self.phase = "day"
        self._update_phase_timer()

    def prestige(self):
        earned_pp = max(1, int(self.money // 1000))
        self.prestige_points += earned_pp
        self.prestige_level += 1
        self.prestige_multiplier = 1.0 + 0.2 * self.prestige_level
        self.prestige_cost *= 10
        self.money = 50.0
        self.day = 1
        self.skills = []
        self.max_plots = 1; self.max_night_plots = 1; self.max_long_plots = 0
        self.plots = []; self.night_plots = []; self.long_plots = []; self.plot_farmers = []
        self._init_plots()
        self.inventory.clear()
        self.unlocked_vegs = {"potato"}; self.unlocked_long_vegs.clear()
        self.market_supply.clear(); self.price_history.clear(); self.price_daily.clear()
        self.factory = FoodFactory()
        self.phase = "day"; self.season_index = 0; self.season_day = 1
        self._update_phase_timer()
        self.unlocked_tabs = {"general"}
        self.farmers = self.eternal_bonuses.get("eternal_farmer", 0)
        self.auto_sell_cooked = False
        return earned_pp

    def can_learn_skill(self, skill_id):
        node = self._skill_node(skill_id)
        if not node or skill_id in self.skills: return False
        if node["id"] in [n["id"] for n in SKILL_TREE.get("eternal", [])]:
            if self.prestige_points < node["cost"]: return False
        else:
            if self.money < node["cost"]: return False
        for req in node["req"]:
            if req not in self.skills: return False
        return True

    def learn_skill(self, skill_id):
        if not self.can_learn_skill(skill_id): return False, t("cant_buy")
        node = self._skill_node(skill_id)
        if node["id"] in [n["id"] for n in SKILL_TREE.get("eternal", [])]:
            self.prestige_points -= node["cost"]
            eff = node["effect"]
            if eff[0] == "eternal_yield": self.eternal_bonuses["eternal_yield"] += eff[1]
            elif eff[0] == "eternal_speed": self.eternal_bonuses["eternal_speed"] += eff[1]
            elif eff[0] == "eternal_price": self.eternal_bonuses["eternal_price"] += eff[1]
            elif eff[0] == "eternal_farmer": self.eternal_bonuses["eternal_farmer"] += eff[1]
        else:
            self.money -= node["cost"]
        self.skills.append(skill_id)
        self.recalc_from_skills()
        if node["id"] == "prestige_start":
            pp = self.prestige()
            return True, t("prestige_done", pp)
        return True, t("bought", node['name'])

    def can_unlock_tab(self, tab_key):
        if tab_key in self.unlocked_tabs: return False
        hub = HUB_TABS.get(tab_key)
        if not hub: return False
        if tab_key == "cooking" and self.prestige_level < 1: return False
        if tab_key == "eternal" and self.prestige_level < 1: return False
        if self.money < hub["cost"]: return False
        for prereq in hub["prereq"]:
            if prereq not in self.unlocked_tabs: return False
        return True

    def unlock_tab(self, tab_key):
        if not self.can_unlock_tab(tab_key): return False
        self.money -= HUB_TABS[tab_key]["cost"]
        self.unlocked_tabs.add(tab_key)
        return True

# ====================== Save/Load ======================
def save_game(state, slot):
    data = {
        "money": state.money, "day": state.day,
        "season_index": state.season_index, "season_day": state.season_day,
        "phase": state.phase, "phase_time_left": state.phase_time_left,
        "skills": state.skills,
        "plots": [{"crop": p["crop"], "growth_timer": p["growth_timer"], "max_time": p["max_time"]} for p in state.plots],
        "night_plots": [{"crop": p["crop"], "growth_timer": p["growth_timer"], "max_time": p["max_time"]} for p in state.night_plots],
        "long_plots": [{"crop": p["crop"], "growth_timer": p["growth_timer"], "max_time": p["max_time"]} for p in state.long_plots],
        "plot_farmers": state.plot_farmers,
        "inventory": dict(state.inventory),
        "unlocked_vegs": list(state.unlocked_vegs),
        "unlocked_long_vegs": list(state.unlocked_long_vegs),
        "max_plots": state.max_plots, "max_night_plots": state.max_night_plots,
        "max_long_plots": state.max_long_plots,
        "night_unlocked": state.night_unlocked,
        "farmers": state.farmers,
        "prestige_level": state.prestige_level,
        "prestige_multiplier": state.prestige_multiplier,
        "total_all_time_money": state.total_all_time_money,
        "market_supply": dict(state.market_supply),
        "price_history": {k: list(v) for k, v in state.price_history.items()},
        "price_daily": {k: [(d, p) for d, p in v] for k, v in state.price_daily.items()},
        "unlocked_tabs": list(state.unlocked_tabs),
        "auto_sell_cooked": state.auto_sell_cooked,
        "factory_grid": [[int(state.factory.grid[y][x]) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)],
        "factory_data": [[state.factory.data[y][x] for x in range(GRID_SIZE)] for y in range(GRID_SIZE)],
        "prestige_points": state.prestige_points,
        "prestige_cost": state.prestige_cost,
        "eternal_bonuses": state.eternal_bonuses,
        "dishes": DISHES,
    }
    json_str = json.dumps(data)
    encrypted = encrypt_data(json_str)
    with open(SAVE_TEMPLATE.format(slot), 'w') as f: f.write(encrypted)

def load_game(slot):
    try:
        with open(SAVE_TEMPLATE.format(slot), 'r') as f: encrypted = f.read()
        decrypted = decrypt_data(encrypted)
        if decrypted is None: return None
        data = json.loads(decrypted)
        state = GameState.__new__(GameState)
        state.money = data["money"]; state.day = data["day"]
        state.season_index = data.get("season_index", 0); state.season_day = data.get("season_day", 1)
        state.phase = data.get("phase", "day"); state.phase_time_left = data.get("phase_time_left", SEASONS[0]["day_len"])
        state.skills = data.get("skills", [])
        state.inventory = defaultdict(int, data.get("inventory", {}))
        state.unlocked_vegs = set(data.get("unlocked_vegs", ["potato"]))
        state.unlocked_long_vegs = set(data.get("unlocked_long_vegs", []))
        state.max_plots = data.get("max_plots", 1); state.max_night_plots = data.get("max_night_plots", 1)
        state.max_long_plots = data.get("max_long_plots", 0)
        state.plot_farmers = data.get("plot_farmers", [])
        state.night_unlocked = data.get("night_unlocked", False)
        state.farmers = data.get("farmers", 0)
        state.prestige_level = data.get("prestige_level", 0)
        state.prestige_multiplier = data.get("prestige_multiplier", 1.0)
        state.total_all_time_money = data.get("total_all_time_money", state.money)
        state.plots = [pd for pd in data["plots"]]
        state.night_plots = [pd for pd in data.get("night_plots", [])]
        state.long_plots = [pd for pd in data.get("long_plots", [])]
        state.market_supply = defaultdict(float, data.get("market_supply", {}))
        state.price_history = defaultdict(list, {k: v for k, v in data.get("price_history", {}).items()})
        state.price_daily = defaultdict(list)
        for k, v in data.get("price_daily", {}).items():
            state.price_daily[k] = [(d, p) for d, p in v]
        state.unlocked_tabs = set(data.get("unlocked_tabs", ["general"]))
        state.auto_sell_cooked = data.get("auto_sell_cooked", False)
        state.factory = FoodFactory()
        if "factory_grid" in data:
            grid = data["factory_grid"]
            fdata = data["factory_data"]
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    state.factory.grid[y][x] = grid[y][x]
                    if fdata[y][x] is not None:
                        state.factory.data[y][x] = fdata[y][x]
        state.prestige_points = data.get("prestige_points", 0)
        state.prestige_cost = data.get("prestige_cost", 100000)
        state.eternal_bonuses = data.get("eternal_bonuses", {"eternal_yield":0,"eternal_speed":0.0,"eternal_price":0.0,"eternal_farmer":0})
        global DISHES
        DISHES = data.get("dishes", {})
        state._init_plots()
        state.recalc_from_skills()
        return state
    except: return None

def delete_save(slot):
    try: os.remove(SAVE_TEMPLATE.format(slot)); return True
    except: return False

def save_exists(slot): return os.path.exists(SAVE_TEMPLATE.format(slot))

# ====================== Drawing helpers ======================
def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    if center:
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
    else:
        screen.blit(surf, (x, y))

def draw_button(rect, text, color, text_color=BLACK):
    pygame.draw.rect(screen, color, rect, border_radius=3)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=3)
    draw_text(text, font_small, text_color, rect.centerx, rect.centery, center=True)

# ====================== Main Game ======================
STATE_MAIN_MENU = 0
STATE_GAME = 1
STATE_SKILL_TREE = 2
STATE_PRICE_CHART = 3
STATE_FACTORY = 4

class Game:
    def __init__(self):
        self.state = STATE_MAIN_MENU
        self.game_state = None
        self.slot = 1
        self.running = True
        self.message = ""; self.message_timer = 0
        self.current_tab = "general"
        self.selected_node = None
        self.skill_tree_visible = False
        self.chart_veg = "potato"
        self.factory_cursor = (0, 0)
        self.factory_palette = "conveyor"
        self.factory_veg_to_set = "tomato"
        self.factory_operation_to_set = "fry"
        self.factory_conveyor_dir = 0
        self.factory_dropdown_open = False

    def run(self):
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.running = False
                self.handle_event(event)
            if self.state == STATE_MAIN_MENU: self.update_main_menu(dt)
            elif self.state in (STATE_GAME, STATE_SKILL_TREE, STATE_FACTORY):
                self.update_game(dt)
            elif self.state == STATE_PRICE_CHART: self.update_price_chart(dt)
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if self.state == STATE_MAIN_MENU: self.main_menu_click(mx, my)
            elif self.state == STATE_GAME: self.day_click(mx, my)
            elif self.state == STATE_SKILL_TREE: self.skill_tree_click(mx, my)
            elif self.state == STATE_PRICE_CHART: self.price_chart_click(mx, my)
            elif self.state == STATE_FACTORY: self.factory_click(mx, my)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == STATE_SKILL_TREE:
                    self.state = STATE_GAME
                    self.message = t("day_phase", self.game_state.day, self.game_state.phase)
                    self.message_timer = 2.0
                elif self.state == STATE_PRICE_CHART:
                    self.state = STATE_GAME
                elif self.state == STATE_FACTORY:
                    self.state = STATE_GAME
            if self.state == STATE_FACTORY:
                if event.key == pygame.K_LEFT: self.factory_cursor = (max(0, self.factory_cursor[0]-1), self.factory_cursor[1])
                elif event.key == pygame.K_RIGHT: self.factory_cursor = (min(GRID_SIZE-1, self.factory_cursor[0]+1), self.factory_cursor[1])
                elif event.key == pygame.K_UP: self.factory_cursor = (self.factory_cursor[0], max(0, self.factory_cursor[1]-1))
                elif event.key == pygame.K_DOWN: self.factory_cursor = (self.factory_cursor[0], min(GRID_SIZE-1, self.factory_cursor[1]+1))

    def update_main_menu(self, dt):
        screen.fill(BLACK)
        draw_text(t("main_title"), font_large, WHITE, WINDOW_WIDTH//2, 100, center=True)
        y = 200
        for i in range(1, SAVE_SLOTS+1):
            exists = save_exists(i)
            label = t("slot", i) + " - " + (t("load_game") if exists else t("new_game"))
            rect = pygame.Rect(WINDOW_WIDTH//2-100, y, 200, 40)
            draw_button(rect, label, BLUE)
            if exists:
                del_rect = pygame.Rect(WINDOW_WIDTH//2+110, y, 30, 30)
                draw_button(del_rect, "X", RED)
            y += 50
        exit_rect = pygame.Rect(WINDOW_WIDTH//2-100, y+20, 200, 40)
        draw_button(exit_rect, t("exit"), RED)
        if self.message: draw_text(self.message, font_medium, WHITE, WINDOW_WIDTH//2, 650, center=True)

    def main_menu_click(self, mx, my):
        y = 200
        for i in range(1, SAVE_SLOTS+1):
            rect = pygame.Rect(WINDOW_WIDTH//2-100, y, 200, 40)
            del_rect = pygame.Rect(WINDOW_WIDTH//2+110, y, 30, 30)
            if del_rect.collidepoint(mx, my) and save_exists(i):
                delete_save(i); self.message = f"Слот {i} удалён."; self.message_timer = 2.0; return
            if rect.collidepoint(mx, my):
                self.slot = i
                if save_exists(i):
                    state = load_game(i)
                    self.game_state = state if state else GameState()
                    self.message = f"Игра загружена из слота {i}" if state else t("save_corrupted")
                else:
                    self.game_state = GameState()
                    self.message = f"Новая игра в слоте {i}"
                self.state = STATE_GAME; self.message_timer = 2.0; return
            y += 50
        exit_rect = pygame.Rect(WINDOW_WIDTH//2-100, y+20, 200, 40)
        if exit_rect.collidepoint(mx, my): self.running = False

    def update_game(self, dt):
        gs = self.game_state
        if self.state == STATE_GAME:
            result = gs.update(dt)
            if result == "phase_ended" or gs.phase_time_left <= 0:
                full_day_ended = gs.end_phase()
                if full_day_ended:
                    self.message = t("day_ended", gs.day - 1)
                    self.state = STATE_SKILL_TREE; self.selected_node = None; self.skill_tree_visible = False
                else: self.message = t("phase_msg", gs.phase); self.message_timer = 1.5
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0: self.message = ""
        if self.state == STATE_GAME: self.draw_day_ui()
        elif self.state == STATE_SKILL_TREE:
            if not self.skill_tree_visible: self.draw_hub_ui()
            else: self.draw_skill_tree_ui()
        elif self.state == STATE_FACTORY: self.draw_factory_ui()

    # ---------- Day UI ----------
    def draw_day_ui(self):
        gs = self.game_state
        season = SEASONS[gs.season_index]
        bg = season["bg_color"] if gs.phase == "day" else NIGHT_BG
        header = season["header_color"] if gs.phase == "day" else (25, 25, 80)
        screen.fill(bg)
        pygame.draw.rect(screen, header, (0, 0, WINDOW_WIDTH, 80))
        draw_text(t("day_phase", gs.day, gs.phase) + f" - {season['name']}", font_large, WHITE, 20, 10)
        draw_text(t("money", format_money(gs.money)), font_large, YELLOW, 300, 10)
        draw_text(t("prestige_points", gs.prestige_points), font_medium, YELLOW, 300, 35)
        mins = int(gs.phase_time_left // 60); secs = int(gs.phase_time_left % 60)
        draw_text(t("time_left", f"{mins:02d}:{secs:02d}"), font_medium, WHITE, 600, 10)
        draw_text(t("skip_power", gs.get_skip_power()), font_medium, WHITE, 600, 45)
        free_farmers = gs.farmers - sum(gs.plot_farmers)
        draw_text(t("farmers", gs.farmers, free_farmers), font_medium, WHITE, 600, 65)

        # Область участков (левая часть)
        plot_area_width = WINDOW_WIDTH - 270  # 250 на инвентарь + отступы
        y_start = 100; plot_w, plot_h = 120, 130
        plots = gs._current_plots()
        row_y = y_start
        for i, plot in enumerate(plots):
            x = 20 + i * (plot_w + 10)
            if x + plot_w > plot_area_width:
                row_y += plot_h + 20; x = 20
            pygame.draw.rect(screen, BROWN, (x, row_y, plot_w, plot_h), border_radius=8)
            pygame.draw.rect(screen, BLACK, (x, row_y, plot_w, plot_h), 2, border_radius=8)
            draw_text(t("plot", i+1), font_small, WHITE, x+plot_w//2, row_y+10, center=True)
            if plot['crop']:
                veg = gs.get_item_data(plot['crop'])
                draw_text(veg["name"], font_small, GREEN, x+plot_w//2, row_y+35, center=True)
                progress = 1.0 if plot['growth_timer'] <= 0 else 1.0 - (plot['growth_timer'] / plot['max_time'])
                bar_w = 80
                pygame.draw.rect(screen, GRAY, (x+20, row_y+60, bar_w, 10))
                fill = int(bar_w * progress)
                pygame.draw.rect(screen, GREEN if progress < 1.0 else YELLOW, (x+20, row_y+60, fill, 10))
                if progress >= 1.0:
                    draw_button(pygame.Rect(x+25, row_y+80, 70, 25), t("harvest"), GREEN)
                else:
                    t_left = max(0, int(plot['growth_timer'] + 0.5))
                    draw_text(f"{t_left}с", font_small, BLACK, x+plot_w//2, row_y+90, center=True)
            else:
                draw_button(pygame.Rect(x+25, row_y+55, 70, 25), t("plant"), DARK_GREEN)
            farmers_on = gs.plot_farmers[i] if i < len(gs.plot_farmers) else 0
            free_now = gs.farmers - sum(gs.plot_farmers)
            if free_now > 0:
                plus_rect = pygame.Rect(x+5, row_y+115, 25, 20)
                draw_button(plus_rect, t("assign_farmer"), (100,200,100))
            if farmers_on > 0:
                minus_rect = pygame.Rect(x+35, row_y+115, 25, 20)
                draw_button(minus_rect, t("remove_farmer"), (200,100,100))
            draw_text(str(farmers_on), font_small, WHITE, x+plot_w//2, row_y+125, center=True)

        # Долгие участки
        if gs.max_long_plots > 0:
            long_y = row_y + plot_h + 30
            draw_text("Долгие участки:", font_medium, WHITE, 20, long_y)
            for i, plot in enumerate(gs.long_plots):
                x = 20 + i * (plot_w + 10)
                pygame.draw.rect(screen, BROWN, (x, long_y+30, plot_w, plot_h), border_radius=8)
                pygame.draw.rect(screen, BLACK, (x, long_y+30, plot_w, plot_h), 2)
                draw_text(t("long_plot", i+1), font_small, WHITE, x+plot_w//2, long_y+40, center=True)
                if plot['crop']:
                    veg = gs.get_item_data(plot['crop'])
                    draw_text(veg["name"], font_small, GREEN, x+plot_w//2, long_y+65, center=True)
                    progress = 1.0 if plot['growth_timer'] <= 0 else 1.0 - (plot['growth_timer'] / plot['max_time'])
                    bar_w = 80
                    pygame.draw.rect(screen, GRAY, (x+20, long_y+90, bar_w, 10))
                    fill = int(bar_w * progress)
                    pygame.draw.rect(screen, GREEN if progress < 1.0 else YELLOW, (x+20, long_y+90, fill, 10))
                    if progress >= 1.0:
                        draw_button(pygame.Rect(x+25, long_y+110, 70, 25), t("harvest"), GREEN)
                    else:
                        days_left = plot['growth_timer'] / (SEASONS[gs.season_index]["day_len"] + SEASONS[gs.season_index]["night_len"])
                        draw_text(f"{days_left:.1f}д", font_small, BLACK, x+plot_w//2, long_y+120, center=True)
                else:
                    draw_button(pygame.Rect(x+25, long_y+85, 70, 25), t("plant"), DARK_GREEN)

        # Правая панель инвентаря
        inv_x = WINDOW_WIDTH - 250
        inv_y = 100
        draw_text(t("inventory"), font_medium, YELLOW, inv_x + 125, inv_y, center=True)
        y = inv_y + 25
        # Овощи
        for key, count in sorted(gs.inventory.items(), key=lambda x: gs.get_item_data(x[0]).get("name", x[0])):
            if key in DISHES: continue
            name = gs.get_item_data(key).get("name", key)
            draw_text(f"{name}: {count}", font_small, WHITE, inv_x + 10, y)
            y += 18
            if y > WINDOW_HEIGHT - 200:
                break
        # Готовые блюда
        draw_text(t("cooked_inv"), font_medium, YELLOW, inv_x + 125, y+5, center=True)
        y += 25
        for key, count in sorted(gs.inventory.items(), key=lambda x: x[0]):
            if key not in DISHES: continue
            name = DISHES[key]["name"]
            draw_text(f"{name}: {count}", font_small, WHITE, inv_x + 10, y)
            y += 18
            if y > WINDOW_HEIGHT - 100:
                break

        # Нижние кнопки
        y_btn = WINDOW_HEIGHT - 80
        draw_button(pygame.Rect(20, y_btn, 180, 30), t("skip_button", gs.get_skip_power()), BLUE)
        draw_button(pygame.Rect(220, y_btn, 120, 30), t("sell_all"), RED)
        draw_button(pygame.Rect(WINDOW_WIDTH-130, y_btn, 120, 30), t("save_exit"), RED)
        draw_button(pygame.Rect(WINDOW_WIDTH-130, y_btn-40, 120, 30), t("factory"), ORANGE) if gs.unlocked_tabs and "cooking" in gs.unlocked_tabs else None
        draw_button(pygame.Rect(WINDOW_WIDTH//2 - 60, y_btn, 120, 30), t("price_chart"), BLUE)
        if self.message: draw_text(self.message, font_medium, BLACK, WINDOW_WIDTH//2, y_btn - 30, center=True)

    def day_click(self, mx, my):
        gs = self.game_state
        # Нижние кнопки
        y_btn = WINDOW_HEIGHT - 80
        save_rect = pygame.Rect(WINDOW_WIDTH-130, y_btn, 120, 30)
        price_rect = pygame.Rect(WINDOW_WIDTH//2 - 60, y_btn, 120, 30)
        factory_rect = pygame.Rect(WINDOW_WIDTH-130, y_btn-40, 120, 30) if gs.unlocked_tabs and "cooking" in gs.unlocked_tabs else pygame.Rect(0,0,0,0)
        skip_rect = pygame.Rect(20, y_btn, 180, 30)
        sell_rect = pygame.Rect(220, y_btn, 120, 30)
        if save_rect.collidepoint(mx, my):
            save_game(gs, self.slot); self.state = STATE_MAIN_MENU; self.message = ""; return
        if price_rect.collidepoint(mx, my): self.state = STATE_PRICE_CHART; return
        if factory_rect.collidepoint(mx, my):
            self.state = STATE_FACTORY; self.factory_cursor = (0,0); return
        if sell_rect.collidepoint(mx, my):
            total = 0
            for veg in list(gs.inventory.keys()):
                while gs.inventory[veg] > 0:
                    gs.sell(veg, 1); total += gs.get_current_price(veg)
            self.message = t("sold_for", format_money(total)); self.message_timer = 2.0; return
        if skip_rect.collidepoint(mx, my):
            gs.skip_time(gs.get_skip_power()); self.message = t("skipped", gs.get_skip_power()); self.message_timer = 1.0; return

        # Клик по участкам
        plot_area_width = WINDOW_WIDTH - 270
        y_start = 100; plot_w, plot_h = 120, 130
        plots = gs._current_plots()
        row_y = y_start
        for i, plot in enumerate(plots):
            x = 20 + i * (plot_w + 10)
            if x + plot_w > plot_area_width:
                row_y += plot_h + 20; x = 20
            if plot['crop'] and plot['growth_timer'] <= 0:
                h_rect = pygame.Rect(x+25, row_y+80, 70, 25)
                if h_rect.collidepoint(mx, my):
                    success, msg = gs.harvest(i); self.message = msg; self.message_timer = 2.0; return
            elif not plot['crop']:
                p_rect = pygame.Rect(x+25, row_y+55, 70, 25)
                if p_rect.collidepoint(mx, my): self.show_plant_menu(i, False); return
            farmers_on = gs.plot_farmers[i] if i < len(gs.plot_farmers) else 0
            free_now = gs.farmers - sum(gs.plot_farmers)
            plus_rect = pygame.Rect(x+5, row_y+115, 25, 20)
            minus_rect = pygame.Rect(x+35, row_y+115, 25, 20)
            if free_now > 0 and plus_rect.collidepoint(mx, my):
                gs.plot_farmers[i] += 1; self.message = "Фермер назначен."; self.message_timer = 1.0; return
            if farmers_on > 0 and minus_rect.collidepoint(mx, my):
                gs.plot_farmers[i] -= 1; self.message = "Фермер снят."; self.message_timer = 1.0; return

        if gs.max_long_plots > 0:
            long_y = row_y + plot_h + 30
            for i, plot in enumerate(gs.long_plots):
                x = 20 + i * (plot_w + 10)
                rect_y = long_y + 30
                if plot['crop'] and plot['growth_timer'] <= 0:
                    h_rect = pygame.Rect(x+25, rect_y+80, 70, 25)
                    if h_rect.collidepoint(mx, my):
                        success, msg = gs.harvest_long(i); self.message = msg; self.message_timer = 2.0; return
                elif not plot['crop']:
                    p_rect = pygame.Rect(x+25, rect_y+55, 70, 25)
                    if p_rect.collidepoint(mx, my): self.show_plant_menu(i, True); return

        # Клик в другое место -> пропуск времени
        gs.skip_time(gs.get_skip_power())
        self.message = t("skipped", gs.get_skip_power()); self.message_timer = 0.8

    def show_plant_menu(self, plot_index, is_long=False):
        gs = self.game_state
        available = []
        if is_long:
            available = list(gs.unlocked_long_vegs)
        else:
            for veg in gs.unlocked_vegs:
                data = gs.get_item_data(veg)
                if (gs.phase == "night" and not data.get("day", True)) or (gs.phase == "day" and data.get("day", True)):
                    available.append(veg)
        if not available: self.message = t("no_seeds"); self.message_timer = 2.0; return
        chosen = None; menu = True
        while menu:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: self.running = False; menu = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: menu = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    y = 300
                    for veg in available:
                        rect = pygame.Rect(300, y, 300, 30)
                        if rect.collidepoint(mx, my): chosen = veg; menu = False; break
                        y += 35
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)); overlay.set_alpha(150); overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            draw_text("Выберите семя:", font_large, WHITE, WINDOW_WIDTH//2, 200, center=True)
            y = 300
            for veg in available:
                data = gs.get_item_data(veg); cost = data.get("seed_cost", 0)
                draw_button(pygame.Rect(300, y, 300, 30), f"{data['name']} ({cost}$)", LIGHT_GRAY)
                y += 35
            pygame.display.flip(); clock.tick(FPS)
        if chosen:
            if is_long: ok, msg = gs.plant_long(plot_index, chosen)
            else: ok, msg = gs.plant(plot_index, chosen)
            self.message = msg; self.message_timer = 2.0

    # ---------- Фабрика UI ----------
    def draw_factory_ui(self):
        gs = self.game_state
        screen.fill((30,30,40))
        draw_text(t("factory"), font_large, WHITE, WINDOW_WIDTH//2, 20, center=True)
        draw_button(pygame.Rect(20, 20, 100, 30), t("back"), BLUE)
        cell_size = min(30, (WINDOW_WIDTH-300)//GRID_SIZE, (WINDOW_HEIGHT-150)//GRID_SIZE)
        offset_x = 250; offset_y = 80
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size, cell_size, cell_size)
                kind = gs.factory.grid[y][x]
                color = LIGHT_GRAY
                if kind == TILE_INPUT: color = GREEN
                elif kind == TILE_MACHINE: color = BLUE
                elif kind == TILE_OUTPUT: color = YELLOW
                elif kind == TILE_AUTOSELL: color = ORANGE
                elif kind == TILE_CONVEYOR: color = (100,100,100)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                if kind == TILE_INPUT and gs.factory.data[y][x]:
                    veg = gs.factory.data[y][x]
                    draw_text(veg[:2], font_small, BLACK, rect.centerx, rect.centery, center=True)
                elif kind == TILE_MACHINE and gs.factory.data[y][x] and "operation" in gs.factory.data[y][x]:
                    op = gs.factory.data[y][x]["operation"]
                    draw_text(op[:2], font_small, WHITE, rect.centerx, rect.centery, center=True)
                elif kind == TILE_OUTPUT and gs.factory.data[y][x]:
                    count = len(gs.factory.data[y][x])
                    draw_text(str(count), font_small, BLACK, rect.centerx, rect.centery, center=True)
                elif kind == TILE_CONVEYOR:
                    dir_char = [">", "<", "v", "^"][gs.factory.data[y][x] if gs.factory.data[y][x] is not None else 0]
                    draw_text(dir_char, font_small, WHITE, rect.centerx, rect.centery, center=True)
        cx, cy = self.factory_cursor
        pygame.draw.rect(screen, WHITE, (offset_x + cx*cell_size, offset_y + cy*cell_size, cell_size, cell_size), 2)
        pal_x = 10; pal_y = 400
        draw_text("Инструменты:", font_small, WHITE, pal_x, pal_y)
        pal_items = ["input", "machine", "output", "autosell", "conveyor", "delete"]
        pal_names = [t("factory_input"), t("factory_machine"), t("factory_output"), t("factory_autosell"),
                     t("factory_conveyor"), t("factory_delete")]
        for i, (pid, pname) in enumerate(zip(pal_items, pal_names)):
            rect = pygame.Rect(pal_x, pal_y+20+i*30, 120, 25)
            col = GREEN if self.factory_palette == pid else GRAY
            draw_button(rect, pname, col)
        if self.factory_palette == "input":
            veg_btn_rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30 + 10, 120, 25)
            draw_button(veg_btn_rect, f"{self.factory_veg_to_set} ▼", (150,150,250))
            if self.factory_dropdown_open:
                drop_x = 10; drop_y = 80
                for j, veg in enumerate(gs.unlocked_vegs):
                    item_rect = pygame.Rect(drop_x, drop_y + j*25, 120, 22)
                    col = GREEN if veg == self.factory_veg_to_set else LIGHT_GRAY
                    draw_button(item_rect, veg, col)
        if self.factory_palette == "machine":
            op_texts = [("boil", t("factory_boil")), ("fry", t("factory_fry")), ("cut", t("factory_cut")), ("bake", t("factory_bake"))]
            for j, (op_id, op_name) in enumerate(op_texts):
                rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30 + 10 + j*30, 120, 25)
                col = GREEN if self.factory_operation_to_set == op_id else GRAY
                draw_button(rect, op_name, col)
        if self.factory_palette == "conveyor":
            draw_text(t("factory_direction"), font_small, WHITE, pal_x, pal_y+20+len(pal_items)*30+10)
            dirs = ["→", "←", "↓", "↑"]
            for i, d in enumerate(dirs):
                rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30+10+30 + i*25, 40, 22)
                col = GREEN if self.factory_conveyor_dir == i else GRAY
                draw_button(rect, d, col)
        draw_text(t("money", format_money(gs.money)), font_medium, YELLOW, 600, 60)
        if self.message: draw_text(self.message, font_medium, WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT-30, center=True)

    def factory_click(self, mx, my):
        gs = self.game_state
        back_rect = pygame.Rect(20, 20, 100, 30)
        if back_rect.collidepoint(mx, my):
            self.state = STATE_GAME; self.factory_dropdown_open = False; self.message = ""; return
        cell_size = min(30, (WINDOW_WIDTH-300)//GRID_SIZE, (WINDOW_HEIGHT-150)//GRID_SIZE)
        offset_x = 250; offset_y = 80
        if self.factory_dropdown_open:
            drop_x = 10; drop_y = 80
            for j, veg in enumerate(gs.unlocked_vegs):
                item_rect = pygame.Rect(drop_x, drop_y + j*25, 120, 22)
                if item_rect.collidepoint(mx, my):
                    self.factory_veg_to_set = veg; self.factory_dropdown_open = False; return
            self.factory_dropdown_open = False
            return
        pal_x = 10; pal_y = 400
        pal_items = ["input", "machine", "output", "autosell", "conveyor", "delete"]
        for i, pid in enumerate(pal_items):
            rect = pygame.Rect(pal_x, pal_y+20+i*30, 120, 25)
            if rect.collidepoint(mx, my):
                self.factory_palette = pid; self.factory_dropdown_open = False; return
        if self.factory_palette == "input":
            veg_btn_rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30 + 10, 120, 25)
            if veg_btn_rect.collidepoint(mx, my):
                self.factory_dropdown_open = not self.factory_dropdown_open; return
        if self.factory_palette == "machine":
            op_btns = [("boil", t("factory_boil")), ("fry", t("factory_fry")), ("cut", t("factory_cut")), ("bake", t("factory_bake"))]
            for j, (op_id, _) in enumerate(op_btns):
                rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30 + 10 + j*30, 120, 25)
                if rect.collidepoint(mx, my): self.factory_operation_to_set = op_id; return
        if self.factory_palette == "conveyor":
            dirs = ["→", "←", "↓", "↑"]
            for i, d in enumerate(dirs):
                rect = pygame.Rect(pal_x, pal_y+20+len(pal_items)*30+10+30 + i*25, 40, 22)
                if rect.collidepoint(mx, my): self.factory_conveyor_dir = i; return
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size, cell_size, cell_size)
                if rect.collidepoint(mx, my):
                    tkind, tdata = gs.factory.get_tile(x, y)
                    if tkind == TILE_OUTPUT and tdata:
                        for dish_id in tdata:
                            if dish_id in DISHES:
                                gs.money += DISHES[dish_id]["base_price"] * gs.get_price_multiplier()
                                gs.total_all_time_money += DISHES[dish_id]["base_price"] * gs.get_price_multiplier()
                        gs.factory.data[y][x] = []
                        self.message = "Блюда проданы."; self.message_timer = 1.5; return
                    if self.factory_palette == "delete": gs.factory.remove(x, y)
                    elif self.factory_palette == "input": gs.factory.place(x, y, TILE_INPUT, self.factory_veg_to_set)
                    elif self.factory_palette == "machine": gs.factory.place(x, y, TILE_MACHINE, {"operation": self.factory_operation_to_set})
                    elif self.factory_palette == "output": gs.factory.place(x, y, TILE_OUTPUT, [])
                    elif self.factory_palette == "autosell": gs.factory.place(x, y, TILE_AUTOSELL, None)
                    elif self.factory_palette == "conveyor":
                        if gs.factory.grid[y][x] == TILE_CONVEYOR:
                            cur_dir = gs.factory.data[y][x] if gs.factory.data[y][x] is not None else 0
                            gs.factory.data[y][x] = (cur_dir + 1) % 4
                        else:
                            gs.factory.place(x, y, TILE_CONVEYOR, self.factory_conveyor_dir)
                    return

    # ---------- Skill tree / hub ----------
    def draw_hub_ui(self):
        gs = self.game_state
        screen.fill((40, 40, 60))
        draw_text(t("hub_title"), font_large, WHITE, WINDOW_WIDTH//2, 40, center=True)
        draw_text(t("money", format_money(gs.money)), font_medium, YELLOW, WINDOW_WIDTH//2, 80, center=True)
        draw_text(t("prestige_points", gs.prestige_points), font_medium, YELLOW, WINDOW_WIDTH//2, 105, center=True)
        draw_button(pygame.Rect(20, 20, 120, 30), t("back_to_game"), BLUE)
        draw_button(pygame.Rect(WINDOW_WIDTH-130, 650, 120, 30), t("save_exit"), RED)
        y = 140
        for tab_key, hub in HUB_TABS.items():
            if tab_key == "cooking" and gs.prestige_level < 1: continue
            if tab_key == "eternal" and gs.prestige_level < 1: continue
            rect = pygame.Rect(WINDOW_WIDTH//2 - 120, y, 240, 40)
            if tab_key in gs.unlocked_tabs:
                draw_button(rect, f"→ {hub['name']}", GREEN)
            else:
                cost_str = format_money(hub["cost"])
                if gs.can_unlock_tab(tab_key):
                    draw_button(rect, f"Открыть {hub['name']} ({cost_str}$)", BLUE)
                else:
                    reason = []
                    if gs.money < hub["cost"]: reason.append(t("need_money"))
                    missing = [HUB_TABS[r]["name"] for r in hub["prereq"] if r not in gs.unlocked_tabs]
                    if missing: reason.append(t("need_prereq", ", ".join(missing)))
                    draw_button(rect, f"{hub['name']} ({', '.join(reason)})", GRAY)
            y += 50
        if self.message: draw_text(self.message, font_medium, WHITE, WINDOW_WIDTH//2, 680, center=True)

    def draw_skill_tree_ui(self):
        gs = self.game_state
        screen.fill((40, 40, 60))
        draw_button(pygame.Rect(20, 20, 100, 30), t("back"), BLUE)
        draw_button(pygame.Rect(WINDOW_WIDTH-130, 650, 120, 30), t("save_exit"), RED)
        tab_name = HUB_TABS[self.current_tab]["name"] if self.current_tab in HUB_TABS else self.current_tab
        draw_text(tab_name, font_large, WHITE, WINDOW_WIDTH//2, 40, center=True)
        draw_text(t("money", format_money(gs.money)), font_medium, YELLOW, WINDOW_WIDTH//2, 80, center=True)
        if self.current_tab in ("prestige", "eternal"):
            draw_text(t("prestige_points", gs.prestige_points), font_medium, YELLOW, WINDOW_WIDTH//2, 105, center=True)
        nodes = SKILL_TREE.get(self.current_tab, [])
        visible_nodes = [n for n in nodes if all(req in gs.skills for req in n["req"])]
        node_positions = {}
        col, row = 0, 0
        for node in visible_nodes:
            x = 150 + col * 140; y = 120 + row * 80
            node_positions[node["id"]] = (x, y)
            col += 1
            if col >= 4: col = 0; row += 1
        for node in visible_nodes:
            x, y = node_positions[node["id"]]
            if node["id"] in gs.skills: color = PURPLE
            elif gs.can_learn_skill(node["id"]): color = GREEN
            else: color = GRAY
            pygame.draw.circle(screen, color, (x, y), 22)
            pygame.draw.circle(screen, BLACK, (x, y), 22, 2)
            draw_text(node["name"], font_small, WHITE, x, y-20, center=True)
            for req in node["req"]:
                if req in node_positions: pygame.draw.line(screen, WHITE, node_positions[req], (x, y), 2)
        if self.selected_node:
            node = gs._skill_node(self.selected_node)
            if node:
                ix, iy = WINDOW_WIDTH//2 + 60, 200
                draw_text(f"Название: {node['name']}", font_medium, WHITE, ix, iy)
                if "desc" in node: draw_text(f"Описание: {node['desc']}", font_small, WHITE, ix, iy+30)
                if self.current_tab == "eternal":
                    draw_text(f"Стоимость: {node['cost']} PP", font_small, WHITE, ix, iy+60)
                else:
                    draw_text(f"Стоимость: {format_money(node['cost'])} $", font_small, WHITE, ix, iy+60)
                if self.selected_node in gs.skills:
                    draw_text("ИЗУЧЕНО", font_medium, GREEN, ix, iy+90)
                elif gs.can_learn_skill(self.selected_node):
                    learn_rect = pygame.Rect(ix, 520, 150, 40)
                    draw_button(learn_rect, t("learn_skill"), GREEN)
                else:
                    missing = [req for req in node["req"] if req not in gs.skills]
                    if missing:
                        names = [gs._skill_node(r)["name"] for r in missing if gs._skill_node(r)]
                        draw_text(t("need_prereq", ", ".join(names)), font_small, RED, ix, iy+90)
                    elif self.current_tab == "eternal" and gs.prestige_points < node["cost"]:
                        draw_text(t("need_pp"), font_small, RED, ix, iy+90)
                    elif gs.money < node["cost"]:
                        draw_text(t("need_money"), font_small, RED, ix, iy+90)
        if self.message: draw_text(self.message, font_medium, WHITE, WINDOW_WIDTH//2, 680, center=True)

    def skill_tree_click(self, mx, my):
        gs = self.game_state
        save_rect = pygame.Rect(WINDOW_WIDTH-130, 650, 120, 30)
        if save_rect.collidepoint(mx, my):
            save_game(gs, self.slot); self.state = STATE_MAIN_MENU; self.message = ""; return
        if not self.skill_tree_visible:
            back_rect = pygame.Rect(20, 20, 120, 30)
            if back_rect.collidepoint(mx, my):
                self.state = STATE_GAME; self.message = t("day_phase", gs.day, gs.phase); self.message_timer = 2.0; return
            y = 140
            for tab_key in HUB_TABS:
                if tab_key == "cooking" and gs.prestige_level < 1: continue
                if tab_key == "eternal" and gs.prestige_level < 1: continue
                rect = pygame.Rect(WINDOW_WIDTH//2 - 120, y, 240, 40)
                if rect.collidepoint(mx, my):
                    if tab_key in gs.unlocked_tabs:
                        self.current_tab = tab_key; self.skill_tree_visible = True; self.selected_node = None
                    elif gs.can_unlock_tab(tab_key):
                        if gs.unlock_tab(tab_key):
                            self.message = t("tab_unlocked", HUB_TABS[tab_key]['name']); self.message_timer = 2.0
                    return
                y += 50
            return
        back_rect = pygame.Rect(20, 20, 100, 30)
        if back_rect.collidepoint(mx, my):
            self.skill_tree_visible = False; self.selected_node = None; return
        if self.selected_node and gs.can_learn_skill(self.selected_node):
            learn_rect = pygame.Rect(WINDOW_WIDTH//2 + 60, 520, 150, 40)
            if learn_rect.collidepoint(mx, my):
                ok, msg = gs.learn_skill(self.selected_node); self.message = msg; self.message_timer = 2.0
                if self.selected_node == "prestige_start" and ok: self.state = STATE_GAME
                return
        nodes = SKILL_TREE.get(self.current_tab, [])
        visible_nodes = [n for n in nodes if all(req in gs.skills for req in n["req"])]
        col, row = 0, 0
        for node in visible_nodes:
            x = 150 + col * 140; y = 120 + row * 80
            if math.hypot(mx-x, my-y) <= 22: self.selected_node = node["id"]; return
            col += 1
            if col >= 4: col = 0; row += 1
        self.selected_node = None

    # ---------- Price chart ----------
    def update_price_chart(self, dt): self.draw_price_chart()
    def draw_price_chart(self):
        gs = self.game_state
        screen.fill((50,50,70))
        draw_text(t("price_chart"), font_large, WHITE, WINDOW_WIDTH//2, 30, center=True)
        draw_button(pygame.Rect(20, 20, 100, 30), t("back"), BLUE)
        all_items = list(gs.unlocked_vegs) + list(gs.unlocked_long_vegs) + list(DISHES.keys())
        x_start = 200
        for i, veg in enumerate(all_items):
            rect = pygame.Rect(x_start + (i % 6) * 100, 60 + (i // 6) * 30, 90, 25)
            color = GREEN if veg == self.chart_veg else GRAY
            draw_button(rect, gs.get_item_data(veg)["name"], color)
        if self.chart_veg in gs.price_daily and len(gs.price_daily[self.chart_veg]) > 1:
            data = gs.price_daily[self.chart_veg][-30:]
            min_day = data[0][0]; max_day = data[-1][0]
            max_price = max(p[1] for p in data); min_price = min(p[1] for p in data)
            if max_price == min_price: max_price += 1
            day_range = max(1, max_day - min_day); price_range = max_price - min_price
            chart_x, chart_y, chart_w, chart_h = 50, 160, 860, 500
            pygame.draw.rect(screen, WHITE, (chart_x, chart_y, chart_w, chart_h), 2)
            for i in range(0, day_range + 1, max(1, day_range // 5)):
                x = chart_x + int((i / day_range) * chart_w)
                pygame.draw.line(screen, GRAY, (x, chart_y), (x, chart_y + chart_h), 1)
                draw_text(str(min_day + i), font_small, GRAY, x, chart_y + chart_h + 5, center=True)
            for i in range(5):
                y = chart_y + chart_h - int((i / 4) * chart_h)
                price = min_price + (i / 4) * price_range
                draw_text(format_money(price), font_small, GRAY, chart_x - 10, y, center=True)
            points = [(chart_x + int((d - min_day) / day_range * chart_w), chart_y + chart_h - int((p - min_price) / price_range * chart_h)) for d, p in data]
            if len(points) >= 2:
                pygame.draw.lines(screen, YELLOW, False, points, 2)
        else:
            draw_text("Нет данных для отображения", font_medium, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, center=True)

    def price_chart_click(self, mx, my):
        gs = self.game_state
        if pygame.Rect(20, 20, 100, 30).collidepoint(mx, my): self.state = STATE_GAME; return
        all_items = list(gs.unlocked_vegs) + list(gs.unlocked_long_vegs) + list(DISHES.keys())
        x_start = 200
        for i, veg in enumerate(all_items):
            rect = pygame.Rect(x_start + (i % 6) * 100, 60 + (i // 6) * 30, 90, 25)
            if rect.collidepoint(mx, my): self.chart_veg = veg; break

if __name__ == "__main__":
    Game().run()
