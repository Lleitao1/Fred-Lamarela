import pygame
import math
import os
#from scipy.spatial import distance


ROOT = os.getcwd()

def euc(a,b):
    return distance.euclidean(a,b)

class Car(pygame.sprite.Sprite):

    obstacles = []

    def __init__(self,rect_center,v,a,angle,size,image,is_obstacle=False):
        pygame.sprite.Sprite.__init__(self)

        self.x = rect_center[0]
        self.y = rect_center[1]

        self.size = size

        self.mass = 200
        self.v = v
        self.vx = 0
        self.vy = 0
        self.a = a
        self.stoping = False
        self.angle = angle
        self.angular_velocity = 0
        self.e = 0.5
        self.moment_inertia = self.mass*(self.size[0]**2 + self.size[1]**2)/12

        self.image_path = image
        self.imageMaster = pygame.image.load(image)
        self.imageMaster = pygame.transform.scale(self.imageMaster,size)

        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        self.rect.center = rect_center[0],rect_center[1]

        self.hitbox = []

        self.is_obstacle = is_obstacle
        if is_obstacle:
            Car.obstacles.append(self)

        self.is_colliding = False
        self.collided = False

        self.place = None

    def move_foward(self):
    	self.a = -0.3
        self.stoping = False

    def move_backwards(self):
    	self.a = 0.3
        self.stoping = False

    def stop(self):
        self.stoping = True
        if self.v < 0:
            self.a = 1
        if self.v > 0:
            self.a = -1

    def turn_left(self):
        if self.v > 0:
            self.angular_velocity = -3.0
        elif self.v < 0:
            self.angular_velocity = 3.0
        else:
            self.angular_velocity = 0

    def turn_right(self):
    	if self.v > 0:
            self.angular_velocity = 3.0
        elif self.v < 0:
            self.angular_velocity = -3.0
        else:
            self.angular_velocity = 0

    def stop_turn(self):
    	self.angular_velocity = 0

    def update_speed(self):
        if self.v >= -60 and self.v <= 60:
        	self.v += self.a

        if self.v > -1 and self.v < 1 and self.stoping:
            self.a = 0
            self.v = 0
            self.stoping = False


    def update_cords(self):
    	self.vx = math.sin(math.radians(self.angle))*self.v
    	self.vy = math.cos(math.radians(self.angle))*self.v
        self.x += self.vx
        self.y += self.vy

    def update(self):
    	self.update_angle()
    	self.update_speed()
    	self.update_cords()
        self.update_hitbox()
    	self.update_image()


    def update_image(self):
    	oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.imageMaster,self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

    def update_angle(self):
        self.angle += self.angular_velocity
        if self.angle < -360:
                self.angle += 360
        if self.angle > 360:
            self.angle -= 360

    def rotate(self,point):
        origin = self.x,self.y
        originPoint = (point[0] - origin[0], point[1] - origin[1])
        rotatedX = originPoint[0] * math.cos(math.radians(-1*self.angle)) - originPoint[1] * math.sin(math.radians(-1*self.angle))
        rotatedY = originPoint[0] * math.sin(math.radians(-1*self.angle)) + originPoint[1] * math.cos(math.radians(-1*self.angle))
        return (rotatedX + origin[0], rotatedY + origin[1])

    def update_hitbox(self):
        x,y = self.x - self.size[0]/2,self.y - self.size[1]/2
        size_x,size_y = self.size[0], self.size[1] - 70
        self.hitbox = [self.rotate((x,y)),self.rotate((x,y+size_y)),
                       self.rotate((x+size_x,y+size_y)),self.rotate((x+size_x,y))]

    def update_relative(self,cameraX,cameraY):
        self.rect.center = self.x - cameraX, self.y - cameraY

    def check_collision(self,target):
        a = [i[0] for i in self.hitbox]
        b = [i[1] for i in self.hitbox]
        x1_max,x1_min,y1_max,y1_min = max(a),min(a),max(b),min(b)

        for i in target.hitbox:
            if i[0] <= x1_max and i[0] >= x1_min:
                if i[1] <= y1_max and i[1] >= y1_min:
                    if self.is_obstacle and target.is_obstacle:
                        self.emparelhar(target)
                    else:
                        self.apply_force(target,(i[0],i[1]))
                        self.collided = True
                        target.collided = True
                        self.is_colliding = True
                        target.is_colliding = True

                        c = [i[0] for i in target.hitbox]
                        d = [i[1] for i in target.hitbox]
                        x2_max,x2_min,y2_max,y2_min = max(c),min(c),max(d),min(d)

                        self.x += (x1_max - x2_min)/40
                        self.y += (y1_max - y2_min)/40

                    return True

        if self.collided and target.collided:
            self.is_colliding = False
            target.is_colliding = False

        if target.collided and not target.is_colliding and self.collided and not self.is_colliding:
            target.collided = False
            self.collided = False
            target.stop_turn()
            self.stop_turn()

        return False

    def apply_force(self,target,p):

        v = ((self.v*self.mass - target.v*target.mass)/target.mass)
        target.v += v

        av = 0

        if p[1] > target.y:
            av = (target.x - p[0])/10
        if p[1] < target.y:
            av = (p[0] - target.x)/10

        av = av*self.mass/target.mass
        target.angular_velocity = av




    def emparelhar(self,target):
        if self.v < 0:
            v_min = max(self.v,target.v)
            self.a = 0
            target.a = 0
            self.v = v_min
            target.v = v_min
        if self.y > target.y:
            self.y += 30
        else:
            target.y += 30


        """
        def reposition_obstacle(self):
            self.stop()
            lanePositions = [100,300,480,670,870,1060,1250,1440]
            distances=[]
            for d in lanePositions:
                distances.append(abs(d-self.x))
                current_lane = distances.index(min(distances))
                old_angle = self.angle
                if current_lane <4:
                    orientation = 180
                else:
                    orientation = 0
                    while abs (self.x - lanePositions[current_lane] ) not in range(10) and orientation == self.angle :
                        "add code to go to right position"
                        "maybe not use while"
                        """
