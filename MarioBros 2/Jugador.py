from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
from multiprocessing import Value
pygame.font.init()
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
X = 0
Y = 1
SIZE = (728, 410)

MARIO = 0
LUIGI = 1
FPS = 50

turno = ["first", "second"]
billbala_num = 3
up_num = 1

class Player():
    def __init__(self, numberp):
        self.numberp = numberp
        self.pos = [None, None]
        self.face = None
    def get_pos(self):
        return self.pos

    def get_numberp(self):
        return self.numberp

    def set_pos(self, pos):
        self.pos = pos
        
    def set_face(self, face):
        self.face = face
    
    def get_face(self):
        return self.face
        
    def __str__(self):
        return f"P<{turno[self.numberp], self.pos}>"


class billbala():
    def __init__(self,number):
        self.pos = [None,None]
        self.number = number
    
    def get_pos(self):
        return self.pos

    def set_pos(self,pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

class up():
    def __init__(self,number):
        self.pos = [None,None]
        self.number = number
    
    def get_pos(self):
        return self.pos

    def set_pos(self,pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.billbala = [billbala(i) for i in range(billbala_num)]      
        self.up = [up(i) for i in range(up_num)] 
        self.life = [5,5]
        self.running = True

    def get_player(self, numberp):
        return self.players[numberp]

    def get_billbala(self,i):
        return self.billbala[i]
    
    def get_up(self,i):
        return self.up[i]
    
    def get_life(self):
        return self.life

    def set_pos_player(self, numberp, pos):
        self.players[numberp].set_pos(pos)
        
    def set_face_player(self, numberp, face):
        self.players[numberp].set_face(face)
        
    def set_billbala_pos(self, i, pos):
        self.billbala[i].pos = pos
        
    def set_up_pos(self, i, pos):
        self.up[i].pos = pos
        
    def set_life(self, life):
        self.life = life

    def update(self, gameinfo):
        self.set_pos_player(MARIO, gameinfo['pos_Mario'])
        self.set_pos_player(LUIGI, gameinfo['pos_Luigi'])
        for i in range(billbala_num):
            self.set_billbala_pos(i, gameinfo['pos_billbala_list'][i]) 
        for i in range(up_num):
            self.set_up_pos(i, gameinfo['pos_up_list'][i]) 
        self.set_life(gameinfo['life'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[LUIGI]}:{self.players[MARIO]}>"

lista =['mario_dcha.png', 'luigi_izq.png']
right = ['mario_dcha.png', 'luigi_dcha.png']
left = ['mario_izq.png', 'luigi_izq.png']

class Mapa(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        imagen = lista[self.player.get_numberp()]
        self.image = pygame.image.load(imagen)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.player.get_pos()  
        if self.player.get_face() == 'Left':
            imagen = left[self.player.get_numberp()]
            self.image = pygame.image.load(imagen)
        elif self.player.get_face() == 'Right':
            imagen = right[self.player.get_numberp()]
            self.image = pygame.image.load(imagen)
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class billbalaSprite(pygame.sprite.Sprite):
    def __init__(self, billbala):
        super().__init__()
        self.billbala = billbala
        self.image = pygame.image.load('Bill_Bala.png')
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.billbala.get_pos()
        self.rect.centerx, self.rect.centery = pos

class upSprite(pygame.sprite.Sprite):
    def __init__(self, up):
        super().__init__()
        self.up= up
        self.image = pygame.image.load('UP.png')
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.up.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img, img_rect)

listavidas = ['vida_mario.png','vida_luigi.png']
img1 = pygame.image.load(listavidas[0])
miniimg1 = pygame.transform.scale(img1, (50, 38))
img2 = pygame.image.load(listavidas[1])
miniimg2 = pygame.transform.scale(img2, (50, 38))

class Display():
    def __init__(self, game, face):    
        self.game = game
        self.mapas = [Mapa(self.game.get_player(i)) for i in range(2)]
        self.billbala = [billbalaSprite(self.game.get_billbala(i)) for i in range(billbala_num)]  
        self.up = [upSprite(self.game.get_up(i)) for i in range(up_num)] 
        self.all_sprites = pygame.sprite.Group()
        self.mapa_group = pygame.sprite.Group()
        for mapa in self.mapas:
            self.all_sprites.add(mapa)
            self.mapa_group.add(mapa)  
        for bul in self.billbala:
            self.all_sprites.add(bul) 
        for bul in self.up:
            self.all_sprites.add(bul)
        self.screen = pygame.display.set_mode(SIZE) 
        self.clock =  pygame.time.Clock() 
        self.background = pygame.image.load('Fondo.png')
        pygame.init()

    def analyze_events(self, numberp):
        events = []    
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
            elif event.type == pygame.QUIT:
                events.append("quit")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
           events.append("left")
           self.game.set_face_player(numberp, 'Left') 
        elif keys[pygame.K_RIGHT]:
           events.append("right") 
           self.game.set_face_player(numberp, 'Right') 
        for i in range(billbala_num):
            if pygame.sprite.collide_rect(self.billbala[i], self.mapas[numberp]):
                events.append("collidebillbala"+f"{i}")
        for i in range(up_num):
            if pygame.sprite.collide_rect(self.up[i], self.mapas[numberp]):
                events.append("collideup"+f"{i}")
        if self.game.life[numberp] == 0:
            events.append("death"+f"{numberp}")      
        return events

    def refresh(self):
        life = self.game.get_life()
        self.screen.blit(self.background, (0, 0)) 
        self.all_sprites.draw(self.screen)
        draw_lives(self.screen, 20, 5, life[MARIO], miniimg1)
        draw_lives(self.screen, 500, 5, life[LUIGI], miniimg2)
        pygame.display.flip()
        self.all_sprites.update()
 
        

    def tick(self):
        self.clock.tick(FPS)
    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            face = None
            numberp,gameinfo = conn.recv()
            print(f"You are playing {turno[numberp]}. Good luck!")
            game.update(gameinfo)
            display = Display(game,face)
            while game.is_running():
                events = display.analyze_events(numberp)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)