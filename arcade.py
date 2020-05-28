from car_class_5 import *
from options import *
from pygame.locals import *
from scenario_object_class import *
from muro_class import *
from semaforo import *
import numpy.linalg as npl
import pygame
import time
import threading
import os
import math
import random
import pickle
import numpy as np

ROOT = os.getcwd()

def checkButtonState(buttons,mouse_pos):
    global selection
    c = 0
    for button in buttons:
        t = button.check_state(mouse_pos)
        if type(t) == str:
            selection = button.check_state(mouse_pos)
        else:
            c += 1
    if c == len(buttons):
        selection = False

def control(controls,selection):
    choice = False
    while not choice:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                controls[selection][0] = event.key
                name = pygame.key.name(event.key)
                controls[selection][1].change_text(name)
                choice = True
    return controls

def check_win(pov,race_len):
    global raceEnd
    if pov.pos[1] < -1*race_len*road_size:
        raceEnd = True

def get_places():
    global players_places

    p = []

    for i in players_list:
        p.append((i.pos[1],i))
    p.sort()

    for i in range(len(p)):
        p[i][1].place = i+1

    players_places = p

def get_random_object():
    options = 60*['flores'] + 30*['arvore'] + 10*['animado']
    tipo = random.choice(options)
    if tipo != 'animado':
        options = os.listdir(tipo)
        escolha = random.choice(options)
        os.chdir(tipo)
        return [escolha,tipo]
    else:
        options = os.listdir(tipo)
        escolha = random.choice(options)
        os.chdir(tipo)

        imagens = os.listdir(escolha)
        imagens.sort()
        os.chdir(escolha)
        return imagens + [tipo]

def delete_cars():
    global cars_list
    last_place = players_places[0][-1]
    to_del = [i if Car.obstacles[i].pos[1] > last_place.pos[1] + 2000 else None for i in range(len(Car.obstacles))]
    for i in to_del:
        if i != None:
            try:
                del(Car.obstacles[i])
            except:
                pass
    cars_list = pygame.sprite.OrderedUpdates()
    for i in Car.obstacles:
        cars_list.add(i)

def addScenario():
    global flores,arvores,animados

    os.chdir("Images")

    first_place_y = players_places[0][0]

    lanePositions = [random.randint(-250,-20),random.randint(1550,1800)]
    position = random.choice(lanePositions)

    obstacle_x = position
    obstacle_y = first_place_y - random.randint(800,1500)

    os.chdir("Scenario_Object")
    objeto = get_random_object()


    if objeto[-1] == 'arvore':
        size = 200,200
        objeto.pop(-1)
        newObject = Scenario_Object((obstacle_x,obstacle_y),size,objeto)
        arvores.add(newObject)

    if objeto[-1] == 'flores':
        size = 50,50
        objeto.pop(-1)
        newObject = Scenario_Object((obstacle_x,obstacle_y),size,objeto)
        flores.add(newObject)

    if objeto[-1] == 'animado':
        objeto.pop(-1)
        if 'dog' in objeto[0] or 'gato' in objeto[0] or 'ovelha' in objeto[0]:
            newObject = Scenario_Object((obstacle_x,obstacle_y),(80,80),objeto,True,0,-2)
        if 'dog_front' in objeto[0] or 'gato_front' in objeto[0] or 'ovelha_front' in objeto[0]:
            newObject = Scenario_Object((obstacle_x,obstacle_y),(80,80),objeto,True,0,2)
        if 'Link_Front' in objeto[0]:
            newObject = Scenario_Object((obstacle_x,obstacle_y),(100,100),objeto,True,0,8)
        if 'link_back' in objeto[0]:
            newObject = Scenario_Object((obstacle_x,obstacle_y),(100,100),objeto,True,0,-8)


        if 'bird_front' in objeto[0]:
            x,x1,x2 = random.randint(300,1200),50,-50
            obstacle_y -= 300
            y1,y2 = -50,-50
            vx,vy = 0,3
        if 'bird_back' in objeto[0]:
            x,x1,x2 = random.randint(300,1200),50,-50
            obstacle_y -= 300
            y1,y2 = 50,50
            vx,vy = 0,-10
        if 'bird_direita' in objeto[0]:
            x,x1,x2 = 1600,50,50
            obstacle_y -= 300
            y1,y2 = 50,-50
            vx,vy = -14,0
        if 'bird_esquerda' in objeto[0]:
            x,x1,x2 = -100,-50,-50
            obstacle_y -= 300
            y1,y2 = 50,-50
            vx,vy = 14,0

        if 'bird' in objeto[0]:
            newObject = Scenario_Object((x,obstacle_y),(50,50),objeto,True,vx,vy)
            animados.add(newObject)
            newObject = Scenario_Object((x+x1,obstacle_y+y1),(50,50),objeto,True,vx,vy)
            animados.add(newObject)
            newObject = Scenario_Object((x+x2,obstacle_y+y2),(50,50),objeto,True,vx,vy)
            animados.add(newObject)
            newObject = Scenario_Object((x+2*x1,obstacle_y+2*y1),(50,50),objeto,True,vx,vy)
            animados.add(newObject)
            newObject = Scenario_Object((x+2*x2,obstacle_y+2*y2),(50,50),objeto,True,vx,vy)

        animados.add(newObject)

    os.chdir(ROOT)

def addObstacle():
    global cars_list

    os.chdir("Images")

    lanePositions = [100,300,480,680,870,1070,1250,1450]
    probabilities = 50*[1] + 30*[2] + 15*[3] + 5*[4]
    generate = random.choice(probabilities)

    first_place_y = players_places[0][0]

    for i in range(generate-1):

        position = random.choice(lanePositions)

        if lanePositions.index(position) < 4:
            carAngle = 180
        else:
            carAngle = 0

        vel = random.randint(-30,-10)
        vel = [0.0, vel*np.cos(carAngle)]

        obstacle_x = position
        obstacle_y = first_place_y - random.randint(1800,2500)

        carros = os.listdir("Car")
        pick = random.choice(carros)

        os.chdir("Car")

        car_stas = stats[pick[-5]]
        newObstacle = Car((obstacle_x,obstacle_y),vel,(0.0,0.0),carAngle,(80,200),car_stas,pick,True)

        os.chdir(ROOT)
        os.chdir("Images")

        cars_list.add(newObstacle)

    os.chdir(ROOT)

def addMuro():
    global muros
    os.chdir("Images")

    x = 760
    y = players_places[0][0]

    init = Muro((x,y),"init")
    muros.add(init)

    y += init.size[1]

    for i in range(random.randint(20,80)):
        mid = Muro((x,y))
        muros.add(mid)
        y += mid.size[1]

    end = Muro((x,y),"end")
    muros.add(end)

    os.chdir(ROOT)

def generateScenario(difficulty):
        global old_first_y,timer

    	first_place_y = players_places[0][0]

        numero = random.randint(0,10000)
        if numero > 9950:
            addMuro()

        if timer >= random.randint(difficulty,difficulty+20):
            addObstacle()
            timer = 0

        if first_place_y < old_first_y - random.randint(20,60):
            addScenario()
            old_first_y = first_place_y

        timer += 1

        delete_cars()

def collisions_handle(pov):
    global cars_list,players_list,raceEnd
    cars = [i for i in cars_list]
    cars.extend(players_list)

    collisions = []

    for i in cars:
        for j in cars:
            if i != j:
                if i.check_collision(j) and not((j,i) in collisions):
                    if i == pov or j == pov:
                        raceEnd = True

        if i.pos[0] < 0 or i.pos[0] > road_size*2:
            for k in Muro.muros:
                if i.check_collision(k):
                    raceEnd = True



                    collisions.append((i,j))
    if collisions != []:
        return (True,collisions)
    return (False,False)

def update_camera(gameDisplay,pov):
    global cameraX,cameraY,camera_angle
    if pov.pos[0] > 300 and pov.pos[0] < 1200:
        cameraX  = pov.pos[0] - gameDisplay.x/2
    cameraY  = pov.pos[1] - gameDisplay.y/2 +   6.7*npl.norm(pov.v) - abs(npl.norm(pov.v))**1.47


    for car in cars_list:
        car.update_relative(cameraX,cameraY)
    for car in players_list:
        car.update_relative(cameraX,cameraY)
    for objeto in flores:
    	objeto.update_relative(cameraX,cameraY)
    for objeto in arvores:
    	objeto.update_relative(cameraX,cameraY)
    for objeto in animados:
    	objeto.update_relative(cameraX,cameraY)
    for muro in muros:
        muro.update_relative(cameraX,cameraY)

def update_map(gameDisplay,c,race_len,pov):
    global raceEnd

    gameDisplay.screen.fill(white)

    for i in range(race_len*2):
        gameDisplay.screen.blit(road,(0-cameraX,road_size*i*-1-cameraY))
        gameDisplay.screen.blit(road,(road_size-cameraX,road_size*i*-1-cameraY))
        gameDisplay.screen.blit(grama,(-500-cameraX,grama_size*i*-1-cameraY))
        gameDisplay.screen.blit(grama,(road_size*2-cameraX,grama_size*i*-1-cameraY))

    for i in range(4):
        gameDisplay.screen.blit(finish_line,(road_size/2*i-cameraX,-1*768*race_len-cameraY))



    muros.draw(gameDisplay.screen)
    cars_list.draw(gameDisplay.screen)
    players_list.draw(gameDisplay.screen)
    flores.draw(gameDisplay.screen)
    animados.draw(gameDisplay.screen)
    arvores.draw(gameDisplay.screen)


    '''for car in cars_list:
        for i in car.hitbox:
            pygame.draw.rect(gameDisplay.screen,blue,[i[0]-cameraX,i[1]-cameraY,7,7])
    for car in players_list:
        for i in car.hitbox:
            pygame.draw.rect(gameDisplay.screen,blue,[i[0]-cameraX,i[1]-cameraY,7,7])'''

    '''if c[0]:
        for colision in c[1]:
            for car in colision:
                for i in car.hitbox:
                    pygame.draw.rect(gameDisplay.screen,green,[i[0]-cameraX,i[1]-cameraY,7,7])'''


    if pov.place == 1:
        gameDisplay.screen.blit(first_image,(gameDisplay.x*0.9,gameDisplay.y*0.8))

    if pov.place == 2:
        gameDisplay.screen.blit(second_image,(gameDisplay.x*0.9,gameDisplay.y*0.8))

    if pov.place == 3:
        gameDisplay.screen.blit(third_image,(gameDisplay.x*0.9,gameDisplay.y*0.8))

    if raceEnd:
        gameDisplay.screen.blit(sefudeu,(100,100))

    pygame.display.update()

def update_all(gameDisplay,pov,race_len,difficulty):
    get_places()
    generateScenario(difficulty)

    cars_list.update()
    players_list.update()

    c = collisions_handle(pov)
    check_win(pov,race_len)

    update_camera(gameDisplay,pov)
    update_map(gameDisplay,c,race_len,pov)


    #Colors

def update_controls(gameDisplay,controls,controls_buttons):
    global mousePressed
    buttons = controls_buttons

    mouse_pos = pygame.mouse.get_pos()
    checkButtonState(buttons,mouse_pos)


    buttons.draw(gameDisplay.screen)
    buttons.update(gameDisplay)
    pygame.display.update()

#####################
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
######################

        #Initialize Camera
######################
cameraX = 0
cameraY = 0
camera_angle = 0
######################


    #Initialize Pygame Lists
#####################
players_list = pygame.sprite.OrderedUpdates()
cars_list = pygame.sprite.OrderedUpdates()
flores = pygame.sprite.OrderedUpdates()
arvores = pygame.sprite.OrderedUpdates()
animados = pygame.sprite.OrderedUpdates()
muros = pygame.sprite.OrderedUpdates()
#####################

    #Initialize Map Generation
######################
os.chdir("Images")
road_size = 768
grama_size = 500
road = pygame.image.load("track.jpg")
road = pygame.transform.scale(road,(road_size,road_size))
grama = pygame.image.load("grama.png")
grama = pygame.transform.scale(grama,(grama_size,grama_size))

y = -1000
for i in xrange(1000):
    muro1 = Muro((0,y))
    muro2 = Muro((road_size*2,y))
    muros.add(muro1,muro2)
    y += muro1.size[1]

semaforo1 = Semaforo((200,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
semaforo2 = Semaforo((600,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
semaforo3 = Semaforo((800,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
semaforo4 = Semaforo((1200,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
animados.add(semaforo1,semaforo2,semaforo3,semaforo4)

finish_line = pygame.image.load("finish_line.png")
finish_line = pygame.transform.scale(finish_line,(road_size/2,road_size/2))

os.chdir(ROOT)
######################

    #Initiazize Places
######################
os.chdir("Images")
old_first_y = 0
players_places = []
first_image = pygame.image.load("1_place.png")
first_image = pygame.transform.scale(first_image,(100,100))
second_image = pygame.image.load("2_place.png")
second_image = pygame.transform.scale(second_image,(100,100))
third_image = pygame.image.load("3_place.png")
third_image = pygame.transform.scale(third_image,(100,100))
sefudeu = pygame.image.load('sefudeu.png')
os.chdir(ROOT)
######################



mousePressed = None
selection = None
sel_controls = False
raceEnd = False
gameExit = False
timer = 0
conta = 0
clock = pygame.time.Clock()

stats = {'1':(0.6,0.8,0.8),'2':(0.6,0.75,0.65),'3':(0.8,0.8,0.65),'4':(0.9,0.75,0.55),
         '5':(0.5,0.7,0.8),'6':(0.8,1.2,0.55),'7':(0.45,1.0,0.9)}

def arcade(gameDisplay,controls,controls_buttons,car_image,race_len,difficulty):
    global gameExit,sel_controls,mousePressed,selection,conta,raceEnd,semaforo1,semaforo2,semaforo3,semaforo4
    global players_list,cars_list,flores,arvores,animados,muros

        #Initialize Player
    ######################
    os.chdir("Images")
    os.chdir("Car")
    car_stas = stats[car_image[-5]]
    player_1 = Car((1070,300),np.zeros(2),(0.0,0.0),0,(80,200),car_stas,car_image)
    players_list.add(player_1)
    os.chdir(ROOT)
    ######################


    while not gameExit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True

            if semaforo1.current_image == 2 and not raceEnd:
                player_1.action = "up"
                if event.type == pygame.KEYDOWN:
                    if event.key == controls["left"][0]:
                        player_1.turn = "left"
                    if event.key == controls["right"][0]:
                        player_1.turn = "right"


                if event.type == pygame.KEYUP:
                    if event.key == controls["left"][0]:
                        player_1.turn = None
                    if event.key == controls["right"][0]:
                        player_1.turn = None

                '''if event.type == pygame.KEYDOWN:
                    if event.key == controls["up"][0]:
                        player_1.action = "up"
                    if event.key == controls["down"][0]:
                        player_1.action = "down"


                if event.type == pygame.KEYUP:
                    if event.key == controls["up"][0]:
                        player_1.action = None
                    if event.key == controls["down"][0]:
                        player_1.action = None'''

            if event.type == pygame.KEYUP:
                if event.key == controls["pause"][0]:
                    if not sel_controls:
                        sel_controls = True
                    else:
                        sel_controls = False

            if event.type == pygame.KEYDOWN:

                if event.key == controls["fullscreen"][0]:
                    gameDisplay.toogle_fullscreen()

            if event.type == pygame.VIDEORESIZE:
                gameDisplay.change_screen_size(event.size)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePressed = selection

            if event.type == pygame.MOUSEBUTTONUP:
                    if selection == mousePressed:
                        if selection in controls.keys():
                            controls = control(controls,selection)
                        if selection == "settings":
                            conta = 200

        if not sel_controls:
            update_all(gameDisplay,player_1,race_len,difficulty)
        else:
            update_controls(gameDisplay,controls,controls_buttons)

        if raceEnd and conta == 0:
            conta = 1
        if conta > 0:
            conta += 1
        if conta > 180:
            conta = 0
            raceEnd = False
            mousePressed = None
            selection = None
            sel_controls = False
            players_list = pygame.sprite.OrderedUpdates()
            cars_list = pygame.sprite.OrderedUpdates()
            flores = pygame.sprite.OrderedUpdates()
            arvores = pygame.sprite.OrderedUpdates()
            animados = pygame.sprite.OrderedUpdates()
            muros = pygame.sprite.OrderedUpdates()
            os.chdir("Images")
            semaforo1 = Semaforo((200,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
            semaforo2 = Semaforo((600,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
            semaforo3 = Semaforo((800,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
            semaforo4 = Semaforo((1200,100),(50,100),90,["red_light.png","yellow_light.png","green_light.png"])
            animados.add(semaforo1,semaforo2,semaforo3,semaforo4)
            os.chdir(ROOT)
            return controls

        clock.tick(60)


    pygame.quit()
    exit()
