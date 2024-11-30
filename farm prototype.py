import pygame
import sys
import time

# инициализация Pygame
pygame.init()

# настройка экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('I <3 veggies')

# цвета
GREEN = (34, 177, 76)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)

# шрифты
font = pygame.font.SysFont(None, 36)

# стартовый баланс денег
money = 9999

# семена и их стоимость
seed_prices = {
    'carrot': 10,  
    'tomato': 15, 
}

# инвентарь семян (изначально 0)
inventory = {
    'carrot': 0,
    'tomato': 0,
}

# загрузка изображений
background_image = pygame.image.load('background.png')  # фон
carrot_image = pygame.image.load('carrot.png')  # морковка
tomato_image = pygame.image.load('tomato.png')  # помидор
farmer_image = pygame.image.load('farmer.png')  # фермер

# масштабирование изображений под нужный размер (при необходимости)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
carrot_image = pygame.transform.scale(carrot_image, (50, 50))
tomato_image = pygame.transform.scale(tomato_image, (50, 50))
farmer_image = pygame.transform.scale(farmer_image, (100, 100))

# начальная позиция фермера
farmer_x, farmer_y = 400, 300
farmer_speed = 5  # скорость передвижения фермера

# параметры для грядок
GRID_SIZE = 5
CELL_SIZE = 100
GAP = 10

# класс для овоща
class Vegetable:
    def __init__(self, grow_time, name, image):
        self.grow_time = grow_time  # время для роста
        self.start_time = time.time()  # время посадки
        self.grown = False  # состояние созревания
        self.name = name  # имя овоща
        self.image = image  # картинка для овоща

    def update(self):
        # проверяем, прошло ли достаточно времени для роста
        if not self.grown and time.time() - self.start_time >= self.grow_time:
            self.grown = True

    def is_grown(self):
        return self.grown

# класс для грядки
class Garden:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]  # пустая грядка

    def plant(self, row, col, vegetable):
        if self.grid[row][col] is None:  # если клетка пуста, садим овощ
            self.grid[row][col] = vegetable

    def harvest(self, row, col):
        if self.grid[row][col] and self.grid[row][col].is_grown():
            self.grid[row][col] = None  # сбор урожая (убираем с грядки)
            return True
        return False

    def update(self):
        # обновляем состояние всех овощей на грядке
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    self.grid[row][col].update()

    def draw(self, screen):
        # отрисовка грядки
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * (CELL_SIZE + GAP)
                y = row * (CELL_SIZE + GAP)
                pygame.draw.rect(screen, GREEN if self.grid[row][col] else WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)

                # отображение овощей на грядке
                if self.grid[row][col]:
                    if self.grid[row][col].is_grown():
                        screen.blit(self.grid[row][col].image, (x + 25, y + 25))  # отображаем изображение созревшего овоща

    # функция для получения клетки, рядом с которой находится фермер
    def get_nearby_cell(self, farmer_x, farmer_y):
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * (CELL_SIZE + GAP)
                y = row * (CELL_SIZE + GAP)
                if abs(farmer_x - x) < CELL_SIZE and abs(farmer_y - y) < CELL_SIZE:
                    return row, col  # возвращаем ближайшую клетку
        return None  # если рядом нет клетки
# инициализация сада
garden = Garden(GRID_SIZE, GRID_SIZE)

# функция для отрисовки кнопок магазина
def draw_shop_buttons(screen, font):
    # создаем кнопки для каждого типа семян
    carrot_button = pygame.Rect(610, 50, 180, 50)
    tomato_button = pygame.Rect(610, 120, 180, 50)

    # отрисовка кнопки 'Морковь'
    pygame.draw.rect(screen, RED if money >= seed_prices['carrot'] else DARK_RED, carrot_button)
    carrot_text = font.render(f"Купить Морковь - {seed_prices['carrot']} монет", True, WHITE)
    screen.blit(carrot_text, (carrot_button.x + 10, carrot_button.y + 10))

    # отрисовка кнопки 'Помидор'
    pygame.draw.rect(screen, RED if money >= seed_prices['tomato'] else DARK_RED, tomato_button)
    tomato_text = font.render(f"Купить Помидор - {seed_prices['tomato']} монет", True, WHITE)
    screen.blit(tomato_text, (tomato_button.x + 10, tomato_button.y + 10))

    return carrot_button, tomato_button

# функция для отрисовки денег и инвентаря
def draw_money_inventory(screen, font):
    money_text = font.render(f'Деньги: {money}', True, BLACK)
    screen.blit(money_text, (10, 10))

    y = 50
    for seed, count in inventory.items():
        inventory_text = font.render(f'{seed.capitalize()}: {count}', True, BLACK)
        screen.blit(inventory_text, (10, y))
        y += 30

        
# функция для покупки семян
def buy_seed(seed):
    global money
    price = seed_prices[seed]
    if money >= price:
        money -= price
        inventory[seed] += 1
        print(f'Куплено семян: {seed}, осталось денег: {money}')
    else:
        print('Недостаточно денег!')

# функция для посадки семян
def plant_seed(row, col, seed):
    global garden
    if inventory[seed] > 0:  # проверяем, есть ли семена в инвентаре
        vegetable = Vegetable(grow_time=5, name=seed, image=carrot_image if seed == 'carrot' else tomato_image)
        garden.plant(row, col, vegetable)  # сажаем 
        inventory[seed] -= 1  # уменьшаем количество семян
        print(f'Посажено: {seed} на грядке ({row}, {col})')

# GAME LOOP
running = True
selected_seed = 'carrot'  # выбранные семена для посадки

while running:
    # обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # обработка кликов мыши для покупки семян
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # проверяем, нажаты ли кнопки магазина
            carrot_button, tomato_button = draw_shop_buttons(screen, font)
            if carrot_button.collidepoint(mouse_x, mouse_y):
                buy_seed('carrot')  # покупаем семена моркови
            elif tomato_button.collidepoint(mouse_x, mouse_y):
                buy_seed('tomato')  # покупаем семена помидоров

        # обработка клавиш для выбора действия
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_seed = 'carrot'  # выбираем морковь для посадки
            elif event.key == pygame.K_2:
                selected_seed = 'tomato'  # выбираем помидоры для посадки

    # перемещения фермера
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]:  # W - вверх
        farmer_y -= farmer_speed
    if keys[pygame.K_s]:  # S - вниз
        farmer_y += farmer_speed
    if keys[pygame.K_a]:  # A - влево
        farmer_x -= farmer_speed
    if keys[pygame.K_d]:  # D - вправо
        farmer_x += farmer_speed

    # проверка нажатия клавиши для посадки семян
    if keys[pygame.K_e]:  # E - посадка семян
        nearby_cell = garden.get_nearby_cell(farmer_x, farmer_y)
        if nearby_cell:
            row, col = nearby_cell
            plant_seed(row, col, selected_seed)

    # обновление состояния сада
    garden.update()

    # отрисовка всех элементов на экране
    screen.blit(background_image, (0, 0))  # отрисовка фона
    garden.draw(screen)  # отрисовка грядок и овощей
    screen.blit(farmer_image, (farmer_x, farmer_y))  # отрисовка фермера

    # отрисовка интерфейса
    draw_shop_buttons(screen, font)  # отрисовка кнопок магазина
    draw_money_inventory(screen, font)  # отрисовка инвентаря и денег

    # обновляем экран
    pygame.display.flip()

    # устанавливаем FPS
    pygame.time.Clock().tick(60)