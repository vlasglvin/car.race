from pygame import *
import random
import pygame_menu

init()
font.init()
font1 = font.Font("race_font.otf",40)
font2 = font.Font("race_font.otf",80)
mixer.init()
mixer.music.load("the_mighty_god-police.wav")
mixer.music.set_volume(0.3)
TEXT_COLOR = (221, 245, 66)
WIDTH, HEIGHT = 1500, 1200
window = display.set_mode(size=(WIDTH,HEIGHT),flags=FULLSCREEN)
WIDTH, HEIGHT = display.get_window_size()
clock = time.Clock() 
FPS = 60

bg_image = image.load("road.png")
player_image = image.load("cars/Black_viper.png")
enemy1_image = image.load("cars/Police.png")
display.set_caption("street racing game")
cars_images = [
                "cars/Ambulance.png",
                "cars/Audi.png",
                "cars/Car.png",
                "cars/Mini_truck.png",
                "cars/Mini_van.png",
                "cars/taxi.png",
                "cars/truck.png"
               ]


cars_loaded = []
for car in cars_images:
    cars_loaded.append(image.load(car))

class GameSprite(sprite.Sprite):
    def __init__(self,image,x,y,width,height):
        super().__init__()
        self.image = transform.scale(image,(width,height)) 
        self.rect = self.image.get_rect() # промокутна область картинки (хітбокс)
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)
        sprites.add(self)

    def draw(self):
        # відрисовуємо картинку self.image в кооординатах self.rect
        window.blit(self.image,self.rect)

class Player(GameSprite):
    def __init__(self):
        super().__init__(player_image,WIDTH / 2,HEIGHT / 2,300,300)
        self.speed = 0
        self.max_speed = 20
        self.hp_amount = 3
        self.distance = 0
        self.frames = 0
        self.orig_image = self.image

        
    def update(self):
        if heal_timer:
            self.frames += 1
            if self.frames == 15:
                self.image = Surface((300,300),SRCALPHA).convert_alpha()
            elif self.frames == 30:
                self.image = self.orig_image
                self.frames=0

        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y >0 and self.speed < self.max_speed:
            # self.rect.y -= self.speed
            self.speed += 0.5 
        if not keys[K_UP] and self.speed > 0:
            self.speed -= 0.2
            
        if keys[K_DOWN] and self.rect.bottom < HEIGHT and self.speed > 0:
            self.speed -=1
            
        if keys[K_LEFT] and self.rect.x > WIDTH/8 and self.speed > 0:
            self.rect.x -= self.speed
            # print(self.rect.x)
        if keys[K_RIGHT] and self.rect.right < WIDTH - WIDTH/8 and self.speed > 0:
            self.rect.x += self.speed

        if self.speed < 0:
            self.speed = 0

class Police_car(GameSprite):
    def __init__(self,x,y):
        super().__init__(enemy1_image,x,y,300,300)
        self.speed = 7
        self.max_speed = 15
        
    def update(self):
        if self.speed <= self.max_speed and self.rect.y > HEIGHT -150:
            self.speed += 0.5  
            self.rect.y -= self.speed 
        if player.rect.x  > self.rect.x:
            self.rect.x += 5

        if player.rect.x  < self.rect.x:
            self.rect.x -= 5

        


class Car(GameSprite):
    def __init__(self,x,y,car_image):
        super().__init__(car_image,x,y,300,300)
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()


def car_spawner():
    random_smuga = random.randint(1,4)
    if random_smuga == 1:
        x = 270
    elif random_smuga == 2:
        x = 550
    elif random_smuga == 3:
        x = 770
    else:
        x = 1050
    random_image = random.choice(cars_loaded)
    cars.add(Car(x,-400,random_image))


def set_difficulty(value, difficulty):
    global totalchase_time, hp_label
    if difficulty == 1:
        totalchase_time = 5
        player.hp_amount = 4
        player.max_speed = 15
    elif difficulty == 2:
        totalchase_time = 10
        player.hp_amount = 3
        player.max_speed = 20
    else:
        totalchase_time = 20   
        player.hp_amount = 1
        player.max_speed = 30
    hp_label = font1.render("hp:" +str(player.hp_amount), True, (0, 255, 68))

def start_the_game():
    game_start()
    menu.disable()

def restart():
    game_start()
    menu2.disable()
    
menu = pygame_menu.Menu('racer pacer', WIDTH, HEIGHT,
                       theme = pygame_menu.themes.THEME_DARK)

menu.add.text_input('Name :', default='nutter beater')
menu.add.button('Play', start_the_game)
menu.add.selector('Difficulty :', [('Easy', 1),('Medium', 2),('Hard', 3)], onchange=set_difficulty)
menu.add.button('Quit', pygame_menu.events.EXIT)



menu2 = pygame_menu.Menu('racer pacer', WIDTH, HEIGHT,
                       theme = pygame_menu.themes.THEME_DARK)

menu2.add.button('Restart', restart)
menu2.add.selector('Difficulty :', [('Easy', 1),('Medium', 2),('Hard', 3)], onchange=set_difficulty)
menu2.add.button('Quit', pygame_menu.events.EXIT)


def game_start():
    global sprites, heal_timer, player, cars, police_car
    sprites = sprite.Group()
    player = Player()
    cars = sprite.Group()
    hp_label = font1.render("hp:" +str(player.hp_amount), True, (0, 255, 68))
    defeat_message = font2.render("YOU LOST!!!", True, (209, 245, 66))
    defeat_rect = defeat_message.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    distance = font1.render("distance" +str(player.distance), True, (61, 110, 74))
    bg_y1 = 0
    bg_y2 = -HEIGHT

    bg = transform.scale(bg_image,(WIDTH,HEIGHT))

    finish = False
    game = True


    spawn_interval = random.randint(3000,5000)
    last_spawntime = time.get_ticks()
    police_timer = time.get_ticks()
    totalchase_time = 10
    heal_timer = None
    finish_timer = 0
    police_chase = False
    # Do the job here !
    menu.disable()
    while game: # основний ігровий цикл
        
        for e in event.get(): # перевіряємо кожну подію
            if e.type == QUIT: # якщо ми натиснули на хрестик
                game = False # гра завершується
            if e.type== KEYDOWN and e.key == K_ESCAPE :
                menu.enable()
                menu.mainloop(window)
        if finish == False:    
            window.blit(bg,(0,bg_y1))
            window.blit(bg,(0,bg_y2))
            bg_y1 += player.speed
            bg_y2 += player.speed
            if player.speed > 0:
                player.distance += int(player.speed * 0.1)
                distance = font1.render("distance" +str(player.distance), True, (247, 247, 2))


            if  bg_y1 > HEIGHT:
                bg_y1 = -HEIGHT
            if  bg_y2 > HEIGHT:
                bg_y2 = -HEIGHT
            now = time.get_ticks()
            if now - last_spawntime > spawn_interval:
                car_spawner()
                spawn_interval = random.randint(3000,5000)
                last_spawntime = time.get_ticks()

            if player.speed < 7 and not police_chase:
                police_timer = time.get_ticks()
                police_chase = True
                police_car = Police_car(750,HEIGHT)
                mixer.music.play(-1)

            if police_chase:
                chase_time = (time.get_ticks() - police_timer) / 1000
                if player.speed <= 7 and chase_time > totalchase_time:
                    finish = True
                    finish_timer = time.get_ticks()
                if chase_time > totalchase_time:
                    police_chase = False
                    police_car.kill()

            sprites.update()
            if heal_timer:
                heal_time = (time.get_ticks() - heal_timer) / 1000
                if heal_time > 3:
                    heal_timer = None
                    player.image = player.orig_image
            else:
                hits = sprite.spritecollide(player, cars, False, sprite.collide_mask)
                for hit in hits:
                    player.hp_amount -= 1
                    if player.hp_amount == 0:
                        finish = True
                        finish_timer = time.get_ticks()
                    hp_label = font1.render("hp:" +str(player.hp_amount), True, (0, 255, 68))
                    heal_timer = time.get_ticks()

    
        sprites.draw(window)
        window.blit(hp_label,(WIDTH - 200,30))
        window.blit(distance,(50,30))
        if finish == True:
            window.blit(defeat_message,defeat_rect)
            if time.get_ticks() - finish_timer > 3000:
                menu2.enable()
                menu2.mainloop(window)

        display.update() # оновлення екрану
        clock.tick(FPS) # контроль FPS


menu.mainloop(window)