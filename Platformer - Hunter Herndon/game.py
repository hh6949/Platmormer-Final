# Imports
import pygame
import random
import json

# Window settings
GRID_SIZE = 64
WIDTH = 20 * GRID_SIZE
HEIGHT = 10 * GRID_SIZE
TITLE = "BM-GO"
FPS = 60

# Create window
pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (0, 150, 255)
GRAY = (175,175,175)

#stages
START = 0
PLAYING = 1
LOSE = 2
WIN = 3

# Load fonts
font_xs = pygame.font.Font(None,14)
font_sm = pygame.font.Font(None, 24)
font_md = pygame.font.Font(None, 40)
font_lg = pygame.font.Font(None, 70)
font_xl = pygame.font.Font(None, 140)

# Load images

hero_idle_imgs_rt = [pygame.image.load('assets/images/characters/player_idle.png').convert_alpha(),]
hero_walk_imgs_rt = [pygame.image.load('assets/images/characters/player_walk1.png').convert_alpha(),
                    pygame.image.load('assets/images/characters/player_walk2.png').convert_alpha()]
hero_jump_imgs_rt = [pygame.image.load('assets/images/characters/player_jump.png').convert_alpha(),]

hero_idle_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_idle_imgs_rt]
hero_walk_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_walk_imgs_rt]
hero_jump_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_jump_imgs_rt]


grass_dirt_img = pygame.image.load('assets/images/tiles/grass_dirt.png').convert_alpha()
brick_img = pygame.image.load('assets/images/tiles/block.png').convert_alpha()
bush_img = pygame.image.load('assets/images/tiles/bush.png').convert_alpha()
gem_img = pygame.image.load('assets/images/items/gem.png').convert_alpha()
key_img = pygame.image.load('assets/images/items/key.png').convert_alpha()
k_door_img = pygame.image.load('assets/images/tiles/locked_door.png').convert_alpha()
background_grass = pygame.image.load('assets/images/backgrounds/backgroundColorGrass.png').convert_alpha()
background_forest = pygame.image.load('assets/images/backgrounds/backgroundColorForest.png').convert_alpha()
dirt_img = pygame.image.load('assets/images/tiles/dirt.png').convert_alpha()
spike_img = pygame.image.load('assets/images/tiles/spike.png').convert_alpha()

enemy_imgs = [pygame.image.load('assets/images/characters/enemy2a.png').convert_alpha(),
              pygame.image.load('assets/images/characters/enemy2b.png').convert_alpha()]

blue_on_img = pygame.image.load('assets/images/tiles/blue_on.png').convert_alpha()
blue_off_img = pygame.image.load('assets/images/tiles/blue_off.png').convert_alpha()
path_img = pygame.image.load('assets/images/tiles/path.png').convert_alpha()
button_up_img = pygame.image.load('assets/images/tiles/button_up.png').convert_alpha()
button_down_img = pygame.image.load('assets/images/tiles/button_down.png').convert_alpha()
heart_img = pygame.image.load('assets/images/items/heart.png').convert_alpha()

# Load sounds


# Game classes
class Entity(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2

    def apply_gravity(self):
        self.vy += gravity
        if self.vy > terminal_velocity:
            self.vy = terminal_velocity

class AnimatedEntity(Entity):

    def  __init__(self, x, y, images):
        super().__init__( x, y, images[0])

        self.images = images
        self.image_index = 0
        self.ticks = 0
        self.animation_speed = 12

    def animate(self):
        self.ticks += 1
        
        if self.ticks % self.animation_speed == 0:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = self.images[self.image_index]
                  
class Hero(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        
        self.speed = 5
        self.vx = 0
        self.vy = 0
        self.jump_power = 16.2
        self.gems = 0
        self.key_state = False
        self.level = 0
        self.hearts = 3
        self.hurt_timer = 0
        self.button_pressed = False
        self.score = 0
        self.facing_right = True
        self.jumping = False
       
    def move_right(self):
    	self.vx = self.speed
    	self.facing_right = True
    	
    def move_left(self):
    	self.vx = -1 * self.speed
    	self.facing_right = False
    
    def jump(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -=2

        if len(hits):
            self.vy = -1 * self.jump_power
        self.jumping = True
    
    def stop(self):
        self.vx = 0
        
    def move_and_check_platforms(self):
        self.rect.x += self.vx

        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right

        self.rect.y += self.vy

        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
                self.jumping = False
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
            self.vy = 0
                
    def check_world_edges(self): 
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > world_width:
            self.rect.right = world_width
            
    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def check_key_doors(self):
        hits = pygame.sprite.spritecollide(self, key_doors, False)

        for door in hits:
            door.apply(self)

    def check_enemies(self):
        hits = pygame.sprite.spritecollide(self, enemies, False)

        for spike in hits:
            if self.hurt_timer ==0:
                self.hearts -= 1
                print(self.hearts)
                self.hurt_timer = 2.0 * FPS
                
        if self.hurt_timer > 0:            
            self.hurt_timer -= 1
            
        hits = pygame.sprite.spritecollide(self, enemies, False)

        for hit in hits:
            if self.vx > 0:
                self.vx = -10
                self.vy = -3
            elif self.vx < 0:
                self.vx = 10
                self.vy = -3
            elif self.vy > 0:
                self.vx = 10
                self.vy = -3
            elif hit.vx > 0:
                self.vx = -10
                self.vy = -3
            elif hit.vx < 0:
                self.vx = 10
                self.vy = -3
                
    def check_spikes(self):
        hits = pygame.sprite.spritecollide(self, spikes, False)

        for spike in hits:
            if self.hurt_timer ==0:
                self.hearts -= 1
                print(self.hearts)
                self.hurt_timer = 1.0 * FPS
                
        if self.hurt_timer > 0:            
            self.hurt_timer -= 1
        
        hits = pygame.sprite.spritecollide(self, spikes, False)

        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
                self.vy = -10

    def check_buttons(self):
        hits = pygame.sprite.spritecollide(self, buttons, False)

        for button in hits:
            button.apply(self)

    def check_paths(self):
        hits = pygame.sprite.spritecollide(self, paths, False)

        for path in hits:
            path.apply(self)

    def set_image_list(self):
        if self.facing_right == True:
            if self.jumping:
                self.images = hero_jump_imgs_rt
            elif self.vx == 0:
                self.images = hero_idle_imgs_rt
            else:
                self.images = hero_walk_imgs_rt
        else:
            if self.jumping:
                self.images = hero_jump_imgs_lt
            elif self.vx == 0:
                self.images = hero_idle_imgs_lt
            else:
                self.images = hero_walk_imgs_lt

    def update(self):
        self.apply_gravity()
        self.check_world_edges()
        self.check_items()
        self.check_key_doors()
        if self.hurt_timer <= 0:
            self.check_enemies()
        self.check_spikes()
        self.move_and_check_platforms()
        self.check_buttons()
        self.check_paths()
        self.set_image_list()
        self.animate()
        
class Platform(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def update(self):
        platforms.empty()
        items.empty()
        inert_platforms.empty()
        key_doors.empty()
        spikes.empty()
        enemies.empty()
        buttons.empty()
        paths.empty()
        setup()

class Gem(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.gems += 1
        character.score += 100 

class Key(Entity):
    
    def __init__(self, x, y, image):
        super().__init__( x, y, image)

    def apply(self, character):
        character.key_state = True
        
class Inert_platform(Entity):
    
    def __init__(self, x, y, image):
        super().__init__( x, y, image)

class Key_door(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, hero):
        if hero.key_state == True:
            hero.rect.x = 3 * GRID_SIZE
            hero.rect.y = 7 * GRID_SIZE
            hero.level += 1
            hero.key_state = False
            Platform.update(self)
        elif hero.key_state == False:
            pass
        
class Spike(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE + GRID_SIZE // 2 - 2#change the image to meet entity requirments

class Enemy(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__( x, y, images)
       
        self.speed = 3
        self.vx = -1 * self.speed
        self.vy = 0

    def move_and_check_platforms(self):
        self.rect.x += self.vx

        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
                self.vx = -1 * self.speed
            elif self.vx < 0:
                self.rect.left = hit.rect.right
                self.vx = self.speed

        self.rect.y += self.vy

        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
            self.vy = 0
            
    def check_world_edge(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > world_width:
            self.rect.right = world_width
            self.vx = -1 * self.speed
    def check_spikes(self):
        hits = pygame.sprite.spritecollide(self, spikes, False)

        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
        
    def update(self):
        self.move_and_check_platforms()
        self.apply_gravity()
        self.check_world_edge()
        self.check_spikes()
        self.animate()

class Button(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE + GRID_SIZE // 2
        
    def apply(self, Hero):
        Hero.button_pressed = True
        platforms.empty()
        items.empty()
        inert_platforms.empty()
        key_doors.empty()
        spikes.empty()
        enemies.empty()
        buttons.empty()
        paths.empty()
        
        Platform.update(self)
          
class Path(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, Hero):
        Hero.level += 1
        if hero.level < 4:
            hero.rect.x = 3 * GRID_SIZE
            hero.rect.y = 7 * GRID_SIZE
            Platform.update(self)
        
# Helper functoins
def first_run():
    global player, hero
    
    player = pygame.sprite.GroupSingle()

    start_x = 3 * GRID_SIZE
    start_y = 7 * GRID_SIZE

    hero = Hero(start_x, start_y, hero_idle_imgs_rt)

    hero.rect.x = start_x
    hero.rect.y = start_y
    
    player.empty()
    player.add(hero)
    
def setup():
    global platforms, items ,inert_platforms, key_doors, spikes, enemies, buttons, paths
    global world_width, world_height
   
    platforms = pygame.sprite.Group()
    items = pygame.sprite.Group()
    inert_platforms = pygame.sprite.Group()
    key_doors = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    paths = pygame.sprite.Group()
    

    if hero.level == 0:
        with open("assets/levels/level_0.json") as f:
            data = json.load(f)
        world_width = data["width"] * GRID_SIZE
        world_height = data["height"] * GRID_SIZE
    elif hero.level == 1:
        with open("assets/levels/level_1.json") as f:
            data = json.load(f)
        world_width = data["width"] * GRID_SIZE
        world_height = data["height"] * GRID_SIZE
    elif hero.level == 2:
        with open("assets/levels/level_2.json") as f:
            data = json.load(f)
        world_width = data["width"] * GRID_SIZE
        world_height = data["height"] * GRID_SIZE
    elif hero.level == 3:
        with open("assets/levels/level_3.json") as f:
            data = json.load(f)
        world_width = data["width"] * GRID_SIZE
        world_height = data["height"] * GRID_SIZE
    

    for loc in data["platform_locs"]:
        platforms.add(Platform(loc[0],loc[1], grass_dirt_img))

    for loc in data["dirt_platform_locs"]:
        platforms.add(Platform(loc[0],loc[1], dirt_img))

    for loc in data["brick_locs"]:
        platforms.add(Platform(loc[0],loc[1], brick_img ))

    for loc in data["spike_locs"]:
        spikes.add(Spike(loc[0],loc[1], spike_img ))

    for loc in data["gem_locs"]:
        items.add(Gem(loc[0],loc[1], gem_img ))

    for loc in data["key_locs"]:
        items.add(Key(loc[0],loc[1], key_img ))

    for loc in data["k_door_locs"]:
        key_doors.add(Key_door(loc[0],loc[1], k_door_img ))

    for loc in data["path_locs"]:
        paths.add(Path(loc[0],loc[1], path_img ))

    for loc in data["bush_locs"]:
        inert_platforms.add(Inert_platform(loc[0],loc[1], bush_img ))

    for loc in data["enemy_locs"]:
        enemies.add(Enemy(loc[0],loc[1], enemy_imgs ))
        
    if hero.button_pressed == True:
        for loc in data["button_locs"]:
            inert_platforms.add(Inert_platform(loc[0],loc[1], button_down_img))
        
        for loc in data["blue_off_locs"]:
            inert_platforms.add(Inert_platform(loc[0],loc[1], blue_off_img ))
    else:
        for loc in data["blue_on_locs"]:
            platforms.add(Platform(loc[0],loc[1], blue_on_img ))

        for loc in data["button_locs"]:
            buttons.add(Button(loc[0],loc[1], button_up_img))

#background images
def draw_background(x,y):
    if hero.level == 0:
        screen.blit(background_grass,[x * GRID_SIZE,y * GRID_SIZE])
        screen.blit(background_grass,[x * GRID_SIZE + 16 * GRID_SIZE ,y * GRID_SIZE])
    elif hero.level == 1:
        screen.blit(background_forest,[x * GRID_SIZE,y * GRID_SIZE])
        screen.blit(background_forest,[x * GRID_SIZE + 16 * GRID_SIZE,y * GRID_SIZE])
    else:
        screen.blit(background_grass,[x * GRID_SIZE,y * GRID_SIZE])
        screen.blit(background_grass,[x * GRID_SIZE + 16 * GRID_SIZE ,y * GRID_SIZE])
        ''' If i had more time I would have redone all the levels with each having
        envirmental themes with the assets I have.
        '''
#grid
def draw_grid(offset_x=0, offset_y=0):
    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        adj_x = x - offset_x % GRID_SIZE
        pygame.draw.line(screen, GRAY, [adj_x, 0], [adj_x, HEIGHT], 1)

    for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
        adj_y = y - offset_y % GRID_SIZE
        pygame.draw.line(screen, GRAY, [0, adj_y], [WIDTH, adj_y], 1)

    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
            adj_x = x - offset_x % GRID_SIZE + 4
            adj_y = y - offset_y % GRID_SIZE + 4
            disp_x = x // GRID_SIZE + offset_x // GRID_SIZE
            disp_y = y // GRID_SIZE + offset_y // GRID_SIZE
            
            point = '(' + str(disp_x) + ',' + str(disp_y) + ')'
            text = font_xs.render(point, True, GRAY)
            screen.blit(text, [adj_x, adj_y])

#displays
def show_start_screen():
    text = font_xl.render(TITLE, True, BLACK)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)

    text = font_md.render("press any key to start", True, BLACK)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)
    
def show_lose_screen():
    text = font_xl.render("Game Over", True, BLACK)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)

    text = font_md.render("press \'r\' to restart", True, BLACK)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)
    
def show_win_screen():
    text = font_xl.render("World Complete!", True, BLACK)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)

    text = font_md.render("press \'r\' to restart", True, BLACK)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)
            
def show_hud():
    text = font_md.render(str(hero.score), True, BLACK)
    rect = text.get_rect()
    rect.topleft = 2, 64
    screen.blit(text, rect)

    screen.blit(gem_img, [4, 16])
    text = font_md.render("x" + str(hero.gems), True, BLACK)
    rect = text.get_rect()
    rect.midleft = 34, 32
    screen.blit(text, rect)

    for i in range(hero.hearts):
        x = i * 34 + 1
        y = 96
        screen.blit(heart_img, [x, y])
                   

#background colors
""" this would have been useful in areas where I would enable upward scrolling, using the top
most color of the background images as a background temporarily"""
background_clr = (207,239,252)
"""
#get colors at some point

if hero.level == 0:
    background_clr = (207,239,252)

if hero.level == 1:
    background_clr = (207,239,252)
"""

#initial settings

gravity = .65
terminal_velocity = 30
stage = START
grid_on = False

# Game loop
running = True
first_run()
setup()

while running:
    if hero.level == 4:
        stage = WIN
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                if grid_on == False:
                    grid_on = True
                elif grid_on == True:
                    grid_on = False
                
            elif stage == START:
                stage = PLAYING

            elif stage == PLAYING:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w: 
                    hero.jump()

            elif stage == LOSE:
                if event.key == pygame.K_r:
                    stage = START

                    hero.rect.x = 3 * GRID_SIZE
                    hero.rect.y = 7 * GRID_SIZE

                    hero.hearts = 3

                    first_run()
                    setup()
            elif stage == WIN:
                if event.key == pygame.K_r:
                    stage = START

                    hero.rect.x = 3 * GRID_SIZE
                    hero.rect.y = 7 * GRID_SIZE

                    hero.hearts = 3

                    first_run()
                    setup()

    pressed = pygame.key.get_pressed()
    if stage == PLAYING:
        if pressed[pygame.K_a]:
            hero.move_left()
        elif pressed[pygame.K_d]:
            hero.move_right()
        else:
            hero.stop()
    
    # Game logic
    if stage == PLAYING:
        player.update()
        enemies.update()

        if hero.hearts <= 0:
            stage = LOSE

    if hero.rect.centerx < WIDTH // 2:
        offset_x = 0
    elif hero.rect.centerx > world_width - WIDTH // 2:
        offset_x = world_width - WIDTH
    else:
        offset_x = hero.rect.centerx - WIDTH // 2
    
        
    # Drawing code
    screen.fill(background_clr)
    draw_background(0,-3.5)

    for sprite in platforms:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in key_doors:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in spikes:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in buttons:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in paths:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in enemies:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in player:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in items:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
    for sprite in inert_platforms:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
        
    if grid_on == True:
        draw_grid(offset_x)
    show_hud()
    if stage == START:
        show_start_screen()
    elif stage == LOSE:
        show_lose_screen()
    elif stage == WIN:
        show_win_screen()
    
    # Update screen
    pygame.display.update()

    # Limit refresh rate of game loop 
    clock.tick(FPS)

# Close window and quit
pygame.quit()
