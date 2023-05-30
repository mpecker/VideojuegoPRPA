from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random

MARIO = 0
LUIGI = 1
turno = ["primero", "segundo"]
turno1 = ["primero", "segundo"]
SIZE = (728, 410) 
X=0
Y=1
DELTA = 10
billbala_num = 20
up_num = 20

class Player():
    def __init__(self, numberp):
        self.numberp = numberp
        if numberp == MARIO:
            self.pos = [30, SIZE[Y]-45]
        else:
            self.pos = [SIZE[X] - 30, SIZE[Y]-45]

    def get_pos(self):
        return self.pos

    def get_numberp(self):
        return self.numberp

    
    def moveRight(self):
        self.pos[X] += DELTA
        if self.pos[X] > SIZE[X]:
            self.pos[X] = SIZE[X]

    def moveLeft(self):
        self.pos[X] -= DELTA
        if self.pos[X] < 0:
            self.pos[X] = 0

    def __str__(self):
        return f"P<{turno1[self.numberp]}, {self.pos}>"


class billbala():
    def __init__(self, number,velocity):
        self.pos=[ random.randint(0,700) , 0 ]
        self.velocity = velocity
        self.number = number

    def get_pos(self):
        return self.pos

    def get_number(self):
        return self.number

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def edge(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, numberp):        
        self.pos[X] = random.randint(0,2)
        self.pos[Y] = 0

    def __str__(self):
        return f"B<{self.pos, self.velocity}>"

class up():
    def __init__(self, number,velocity):
        self.pos=[ random.randint(0,700) , 0 ]
        self.velocity = velocity
        self.number = number

    def get_pos(self):
        return self.pos

    def get_number(self):
        return self.number

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def edge(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, numberp):        
        self.pos[X] = random.randint(0,2)
        self.pos[Y] = 0

    def __str__(self):
        return f"B<{self.pos, self.velocity}>"


class Game():
    def __init__(self, manager):
        self.players = manager.list( [Player(MARIO), Player(LUIGI)] )
        self.life = manager.list( [5,5] )
        self.billbala = manager.list([billbala(i,[random.randint(-3,3),random.randint(5,7)]) for i in range(billbala_num)])
        self.up = manager.list([up(i,[random.randint(-3,3),random.randint(5,7)]) for i in range(up_num)])
        self.billbala_pos = manager.list([self.billbala[i].get_pos() for i in range(billbala_num)])
        self.up_pos = manager.list([self.up[i].get_pos() for i in range(up_num)])
        self.running = Value('i', 1)
        self.lock = Lock()

    def get_player(self, numberp):
        return self.players[numberp]

    def get_billbala(self,i):
        return self.billbala[i]
    
    def get_up(self,i):
        return self.up[i]
    
    def get_life(self):
        return list(self.life)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0
        
    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()
    
    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()

    def billbala_collide(self,i, playernumberp):
        self.lock.acquire()
        billbala = self.billbala[i]
        billbala.collide_player(playernumberp)    
        self.billbala[i] = billbala
        self.lock.release()
      
    def up_collide(self,i, playernumberp):
        self.lock.acquire()
        up = self.billbala[i]
        up.collide_player(playernumberp)    
        self.up[i] = up
        self.lock.release()
          
    
    def get_info(self):
        info = {
            'pos_Mario': self.players[MARIO].get_pos(),
            'pos_Luigi': self.players[LUIGI].get_pos(),
            'life' : list(self.life),
            'is_running': self.running.value == 1,
            'pos_billbala_list': list(self.billbala_pos),
            'pos_up_list': list(self.up_pos)
        }
        return info

    def move_billbala(self,i):
        self.lock.acquire()
        billbala = self.billbala[i]
        billbala.update()
        pos = billbala.get_pos()
        if pos[Y]<0 or pos[Y]>SIZE[Y]:
            pos[Y] = 0        
            pos[X] = random.randint(10,700)
        self.billbala[i]=billbala
        self.billbala_pos[i] = [pos[X],pos[Y]]
        self.lock.release()
        
    def move_up(self,i):
        self.lock.acquire()
        up = self.up[i]
        up.update()
        pos = up.get_pos()
        if pos[Y]<0 or pos[Y]>SIZE[Y]:
            pos[Y] = 0        
            pos[X] = random.randint(10,700)
        self.up[i]=up
        self.up_pos[i] = [pos[X],pos[Y]]
        self.lock.release()

    def __str__(self):
        return f"G<{self.players[LUIGI]}:{self.players[MARIO]}:{self.running.value}>"

def player(numberp, conn, game):
    try:
        print(f"starting player {turno[numberp]}:{game.get_info()}")
        conn.send( (numberp, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "right":
                    game.moveRight(numberp)
                elif command == "left":
                    game.moveLeft(numberp)
                elif "collidebillbala" in command:
                    i = int(command[15]) 
                    game.billbala_collide(i,numberp)
                    game.life[numberp] -=1   
                elif "collideup" in command:
                    i = int(command[9]) 
                    game.up_collide(i,numberp)
                    if game.life[numberp] < 6:
                        game.life[numberp] += 1
                elif command == "quit":
                    game.stop()
                elif "death" in command:
                    game.stop()
                    print('El jugador ' + f'{numberp + 1}' + ' murió')
                    if numberp == 0 :
                        print('El jugador ' + f'{2}' + ' ha ganado')
                    else: 
                        print('El jugador ' + f'{1}' + ' ha ganado')
                elif "victory" in command:
                    game.stop()
                    print('El jugador ' + f'{numberp + 1}' + ' ha ganado')
            if numberp == 1:
                for i in range(billbala_num):
                    game.move_billbala(i)
                for i in range(up_num):
                    game.move_up(i)

            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Se acabó {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f'accepting connection {n_player}')
                conn = listener.accept()
                players[n_player] = Process(target=player, args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)
    except Exception as e:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
