import pygame
import sys
import random

WIDTH = 750
HEIDT = 900

BALLON_SIZE_DEFAULT = 27
BALLON_SIZE_MEDUIM = 25
BALLON_SIZE_BIG = 29
BALLON_SIZE_BONUS = 30
BALLON_SIZE_BOMB = 24

BALLON_RED = (176,0,0)
BALLON_ORANGE = (237,118,14)
BALLON_YELLOW = (237,255,33)
BALLON_GREEN = (24,205,81)
BALLON_BRIGHT_BLUE = (47,169,202)
BALLON_BLUE = (20,54,245)
BALLON_VIOLET = (150,47,202)
BALLON_BONUS_COLOR = (101,0,11)
BALLON_BOMB_COLOR = (41,25,33)

SPAWN_BALLON_EVENT = pygame.USEREVENT + 1
SPAWN_BONUS_BALLON = pygame.USEREVENT + 2
SPAWN_BOMB_BALLON = pygame.USEREVENT + 3

TEXT_COLOR_DEFAULT = (52,201,36) 
TEXT_COLOR_SCORE = (255,176,46)

ROP_COLOR = (159,96,56)
ROP_WIDTH = 4
ROP_LEN = 38

GAME_BACKGROUND = (193,232,235)

pygame.mixer.init()
pygame.init()

pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

class Numtxt:
    def __init__(self,x: int,y: int,size: int,score: int,bs: int,phrases: list,color = None):
        self.pos = (x-15,y-15)
        self.size = size
        self.cadr = 0
        self.score = score
        self.font = pygame.font.Font(None,size)
        self.font.set_bold(True)
        self.fontphr = pygame.font.SysFont('Arial',size - 15,bold=True)
        self.bs = bs
        self.angle = random.randint(-20,20)
        self.color = color
        self.phr = random.choice(phrases)

        if random.randint(0,100) in range(75,100):
            self.phr = random.choice(words_default)

    def draw(self) -> bool:
        self.cadr += 1
        if self.cadr < 10:
            col = (255,255,255)
        elif self.cadr < 20:
            col = (248,247,247)
        elif self.cadr < 45:
            col = (244,236,236)
        elif self.cadr < 60:
            col = (239,225,225)
        elif self.cadr < 75:
            col = (231,203,203)
        else:
            col = (226,182,182)
   
        text = f'+{self.score}'
        
        if self.color == BALLON_BOMB_COLOR:
            col = BALLON_BOMB_COLOR
            text =f'{self.score}'

        if self.cadr < 75:
            phr_surface = self.fontphr.render(self.phr,True,(222,76,138))
            phr_surface = pygame.transform.rotate(phr_surface,self.angle)
            screen.blit(phr_surface,(self.pos[0] - 20,self.pos[1] - self.bs - 20))

        text_surface = self.font.render(text,True,col)
        screen.blit(text_surface,self.pos)
        
        if self.cadr > 95:
            return False
        return True

class Rop:
    def __init__(self,start_pos,end_pos,size_rop):
        self.start_pos = pygame.math.Vector2(start_pos) 
        self.midle_pos = pygame.math.Vector2(start_pos[0],start_pos[1] + size_rop//4)
        self.end_pos = pygame.math.Vector2(end_pos)
        self.vel = pygame.math.Vector2(random.randint(-25,25),random.randint(500,800)).normalize()
        self.rot_s = random.randint(-8,8)
        self.rot_e = random.randint(-8,8)

    def draw_move(self):
        global falling_rops
        self.start_pos += self.vel.rotate(self.rot_s)
        self.end_pos += self.vel.rotate(self.rot_e)
        if self.vel[0] < 0:
            self.midle_pos += pygame.math.Vector2(self.vel[0]*1.1,self.vel[1]*1.1)
        else:
            self.midle_pos += pygame.math.Vector2(-self.vel[0]*1.1,self.vel[1]*1.1)
        pygame.draw.lines(screen,ROP_COLOR,False,[self.start_pos,self.midle_pos,self.end_pos],ROP_WIDTH)
        if self.start_pos[1] > HEIDT and self.midle_pos[1] > HEIDT and self.end_pos[1] > HEIDT:
            falling_rops.remove(self)

class Particle:
    def __init__(self,x: int,y: int,ColorValue):
        self.vel = pygame.math.Vector2(random.randint(-250,250),random.randint(-250,250)).normalize()
        self.pos = (x,y)
        self.x = x
        self.y = y
        self.color = random.choice([ColorValue,(255,255,255),(155,155,155)])
        self.vt = round(random.uniform(0.94,0.98),2)

    def draw_moves(self,index: int):
        global particles 
        self.pos -= self.vel
        self.vel *= self.vt
        self.x = self.pos[0]
        self.y = self.pos[1]
        
        particle_rect = pygame.Rect(self.x,self.y,2,2)
        pygame.draw.rect(screen,self.color,particle_rect)
        if self.vel.length() <= 0.05:
            particles[index].remove(self)
        if particles[index] == []:
            del particles[index]

class Ballon:
    def __init__(self,Size: int,ColorValue,Speed: int):
        self.x = random.randint(Size,WIDTH - Size)
        self.y = HEIDT
        self.size = Size
        self.speed = Speed
        self.color = ColorValue
        if player_level > 3:
            self.mx = random.randint(-250,250)
        else:
            self.mx = 0

    def move_x(self):
        if self.mx < 0:
            self.x -= 1
            self.mx += 1
        else:
            self.x += 1
            self.mx -= 1
        if self.x  - self.size < 0:
            self.x += self.size
            self.mx = abs(self.mx)
        elif self.x + self.size > WIDTH:
            self.x -= self.size
            self.mx = -abs(self.mx)

    def turn_x(self):
        if self.mx != 0 and random.randint(0,100) in range(0,2):
            self.mx *= -1

def create_ballon() -> Ballon:
    color = random.choice(colors_ballon)
    size = random.choice(sizes_ballon)
    return Ballon(size,color,random.randint(3,5))

def draw_game(events: list,ballons: list):
    global flying_ballons, spawn_speed_max, spawn_speed_min, player_level, player_score_up_speed, player_speed_up, player_score, particles, nums, current_mode
    keys = pygame.key.get_pressed()
    screen.fill(GAME_BACKGROUND)
    if particles != {}:
        for i,l in list(particles.items()):
            for p in l[:]:
                p.draw_moves(i)

    if falling_rops != []:
        for r in falling_rops:
            r.draw_move()

    ballons_up()
    
    for ballon in ballons[:]:
        if player_level >= 15 and ballon.mx != 0:
            ballon.turn_x()        
        if ballon.mx != 0:
            ballon.move_x()
        pygame.draw.circle(screen,(255,255,255),(ballon.x,ballon.y),ballon.size + 2)
        pygame.draw.line(screen,ROP_COLOR,(ballon.x,ballon.y),(ballon.x,ballon.y + (ballon.size + ROP_LEN)),ROP_WIDTH)
        pygame.draw.circle(screen,ballon.color,(ballon.x,ballon.y),ballon.size) 
        
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for ballon in ballons[:]:
                ballon_rect = pygame.Rect(ballon.x - ballon.size,ballon.y - ballon.size,ballon.size*2,ballon.size*2)
                pop = ballon_rect.collidepoint(mouse_pos)
                if pop and ballon.color != BALLON_BOMB_COLOR:
                    particles.setdefault(random.randint(-1000000,1000000),[Particle(ballon.x,ballon.y,ballon.color) for _ in range(random.randint(35,55))])
                    falling_rops.append(Rop((ballon.x,ballon.y + ballon.size),(ballon.x,ballon.y+ballon.size+ROP_LEN),ROP_LEN))
                    nums.append(Numtxt(ballon.x,ballon.y,sizes_text_score[ballon.size],bonus_score[ballon.size],ballon.size,words_color[ballon.color]))
                    flying_ballons.remove(ballon)
                    player_score += bonus_score[ballon.size]
                    player_score_up_speed += bonus_score[ballon.size]
                    if player_score_up_speed >= player_speed_up:
                        player_speed_up += 4
                        player_level += 1
                        player_score_up_speed = 0
                        if spawn_speed_max < 1500:
                            spawn_speed_max -= 50
                        elif spawn_speed_min < 750:
                            spawn_speed_min -= 25

                elif pop and ballon.color == BALLON_BOMB_COLOR:
                    flying_ballons.remove(ballon)
                    particles.setdefault(random.randint(-1000000,1000000),[Particle(ballon.x,ballon.y,ballon.color) for _ in range(random.randint(35,55))])
                    falling_rops.append(Rop((ballon.x,ballon.y + ballon.size),(ballon.x,ballon.y+ballon.size+ROP_LEN),ROP_LEN))
                    nums.append(Numtxt(ballon.x,ballon.y,34,-4,ballon.size,words_bomb,color=BALLON_BOMB_COLOR))
                    player_score -= 4
                    player_score_up_speed -= 4
                    if player_score_up_speed < 0:
                        player_score_up_speed = 0
                    if player_score < 0 :
                        player_score = 0

                if pop:
                    sound = random.choice(SOUNDS)
                    sound.play()
        
    nums = [n for n in nums if n.draw()]

    text_level = font.render('УРОВЕНЬ:',True,TEXT_COLOR_DEFAULT)
    text_score_level = font.render(f'{player_level}',True,TEXT_COLOR_SCORE)
    screen.blit(text_level,(30,110))
    screen.blit(text_score_level,(260,110))

    text_speed_up = font.render('ПОВЫШЕНИЕ УРОВНЯ ЧЕРЕЗ:',True,TEXT_COLOR_DEFAULT)
    text_score_speed_up = font.render(f'{player_score_up_speed}/{player_speed_up}',True,TEXT_COLOR_SCORE)
    screen.blit(text_speed_up,(30,30))
    screen.blit(text_score_speed_up,(260,30))

    text_allscore = font.render('НАБРАНО ОЧКОВ:',True,TEXT_COLOR_DEFAULT)
    text_score_allscore = font.render(f'{player_score}',True,TEXT_COLOR_SCORE)
    screen.blit(text_allscore,(30,70))
    screen.blit(text_score_allscore,(260,70))

    if keys[pygame.K_r]:
        restart()
    if keys[pygame.K_m] or keys[pygame.K_ESCAPE]:
        current_mode = 'menu'
def restart():
    global flying_ballons, spawn_speed_min, spawn_speed_max, player_score, player_speed_up, player_score_up_speed, player_level, particles, falling_rops, nums
    flying_ballons = []
    pygame.time.set_timer(SPAWN_BALLON_EVENT,random.randint(1000,1500))
    pygame.time.set_timer(SPAWN_BONUS_BALLON,17500)
    pygame.time.set_timer(SPAWN_BOMB_BALLON,10000)
    spawn_speed_max = 3000
    spawn_speed_min = 1000
    player_score = 0
    player_speed_up = 3
    player_score_up_speed = 0
    player_level = 0
    particles = {}
    falling_rops = []
    nums = []

def ballons_up():
    global flying_ballons
    for ballon in flying_ballons:
        ballon.y -= ballon.speed
        if ballon.y < ballon.size*-2 - 25:
            flying_ballons.remove(ballon)

def draw_menu(events: list):
    global current_mode
    screen.fill((26,21,63))
    mouse_pos = pygame.mouse.get_pos()
    for event in events:
       if btn_play_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN: 
        current_mode = 'play'
        restart()
        break
    
    if btn_play_rect.collidepoint(mouse_pos):
        btn_col_pl = (201,181,181)
    else:
        btn_col_pl = (220,220,220)

    pygame.draw.rect(screen,btn_col_pl,btn_play_rect,border_radius=8)
    screen.blit(play_surface,play_surface_cord)
    screen.blit(titul_surface,titul_cord)

sound_1 = pygame.mixer.Sound('pop_1.mp3')
sound_2 = pygame.mixer.Sound('pop_2.mp3')
sound_3 = pygame.mixer.Sound('pop_3.mp3')

SOUNDS = [sound_1,sound_2,sound_3]

screen = pygame.display.set_mode((WIDTH,HEIDT))
pygame.display.set_caption('Лопание шариков')
isDisplay = True
clock = pygame.time.Clock()

font = pygame.font.SysFont('impact',20)

font_menu = pygame.font.SysFont('Arial',25,bold=True)

titul_surface = font_menu.render('Лопай бесконечные шарики',True,(48,186,143))
titul_cord = (180,130)
btn_play_rect = pygame.Rect(120,260,WIDTH - 240,80)
play_surface = font_menu.render('СТАРТ',True,(0,0,0))
play_surface_cord = play_surface.get_rect(center=(btn_play_rect.center))

colors_ballon = [BALLON_RED,BALLON_ORANGE,BALLON_YELLOW,BALLON_GREEN,BALLON_BRIGHT_BLUE,BALLON_BLUE,BALLON_VIOLET]
sizes_ballon = [BALLON_SIZE_DEFAULT,BALLON_SIZE_MEDUIM,BALLON_SIZE_BIG]

bonus_score = {
    BALLON_SIZE_DEFAULT:1,
    BALLON_SIZE_MEDUIM:2,
    BALLON_SIZE_BIG:3,
    BALLON_SIZE_BONUS:8
}

sizes_text_score = {
    BALLON_SIZE_DEFAULT:33,
    BALLON_SIZE_MEDUIM:35,
    BALLON_SIZE_BIG:37,
    BALLON_SIZE_BONUS:39
}

words_default = [
    'Эй!','За что?!','Что я тебе сделал?!',
    "Ой-ой-ой",'Я тут жил!','Ну и ладно',
    'Пока-пока','Лопнул...','Хлоп','BOOM',
    'Ай','Больненько...'
]

words_bomb = [
    'ТЫ ПОПАЛ!','НЕ ТРОГАЙ МЕНЯ!','ГЛУПЕЦ',
    'ТЫ ЧТО НАДЕЛАЛ?!','ОТОМСТИЛ!'
]

words_bonus = [
    'Я не успел...','Я дорогой!','Хватай скорей!',
    'Спасибо!','Ура!','+ 8 очков!'
]

words_color = {
    BALLON_RED : ['Щяс лопну!','Не подходи!','Ты пожалеешь'],
    BALLON_ORANGE : ['Щекотно!','Хи-хи!','Ещё раз!'],
    BALLON_YELLOW : ['Я боюсь!','Мама!','Не надо!'],
    BALLON_GREEN : ['Хоршего дня!','Удачи!','Мир тебе!'],
    BALLON_BRIGHT_BLUE : ['Я лечу...','Свобода!','Как красиво...'],
    BALLON_BLUE : ['Будь внимательнее','Дерзай!','Загадка!'],
    BALLON_VIOLET : ['Шшш...','Тайна','Узнаешь позже...'],
    BALLON_BONUS_COLOR : words_bonus
}

nums = []
particles = {}
flying_ballons = []
current_mode = 'menu'
pygame.time.set_timer(SPAWN_BALLON_EVENT,random.randint(1000,1500))
pygame.time.set_timer(SPAWN_BONUS_BALLON,17500)
pygame.time.set_timer(SPAWN_BOMB_BALLON,10000)
spawn_speed_max = 3000
spawn_speed_min = 1000
player_score = 0
player_speed_up = 3
player_score_up_speed = 0
player_level = 0
falling_rops = []

while isDisplay:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            isDisplay = False
        if event.type == SPAWN_BALLON_EVENT:
            flying_ballons.append(create_ballon())
            pygame.time.set_timer(SPAWN_BALLON_EVENT,random.randint(spawn_speed_min,spawn_speed_max)) 
        if event.type == SPAWN_BONUS_BALLON and player_level >= 15:
            flying_ballons.append(Ballon(BALLON_SIZE_BONUS,BALLON_BONUS_COLOR,8))
            pygame.time.set_timer(SPAWN_BONUS_BALLON,17500)
        if current_mode == 'play':
            if event.type == SPAWN_BOMB_BALLON:
                flying_ballons.append(Ballon(BALLON_SIZE_BOMB,BALLON_BOMB_COLOR,3))
                if player_level <= 10:
                    pygame.time.set_timer(SPAWN_BOMB_BALLON,10000)
                else:
                    pygame.time.set_timer(SPAWN_BOMB_BALLON,7500)
    if current_mode == 'play':
        draw_game(events,flying_ballons)
    elif current_mode == 'menu':
        draw_menu(events)
    clock.tick(60)
    pygame.display.update()


pygame.quit()
sys.exit()