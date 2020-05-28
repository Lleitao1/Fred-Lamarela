import pygame
import math
import numpy as np
import numpy.linalg as npl
import os
import time

ROOT = os.getcwd()
fps = 60.0
speed_limit = 100.0
total_limit = 100.0
class Car(pygame.sprite.Sprite):

    obstacles = []

    def __init__(self,rect_center,v,a,angle,size,car_stats,image,is_obstacle=False):
        pygame.sprite.Sprite.__init__(self)

        self.car_stats = car_stats

        self.pos = np.array(rect_center)*1.0

        self.size = size

        self.angle = angle
        self.turn = None
        self.I = 3300.0 * self.car_stats[0]
        self.w = 0.0
        self.angle_change = 0
        self.direction = np.array([ np.sin(math.radians(self.angle)), np.cos(math.radians(self.angle)) ])

        self.car_vel = np.array(v)
        self.colision_vel = np.zeros(2)
        self.v = np.zeros(2)

        self.a = np.array(a)
        self.action = None


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

        self.place = None


        self.mass = 2000.0 * car_stats[0]



    #Linear Changes


    def car_acel(self):
        status= self.action
        if status == None :
            return np.array([0.0, 0.0])
        elif status == "up":
            return -2.0*self.direction*self.car_stats[2]
        elif status == "down":
            return 2.0*self.direction*self.car_stats[2]

    def update_carVel(self):
        if np.dot(self.car_vel, self.direction) >0:
            self.car_vel = npl.norm(self.car_vel)*self.direction
        else:
            self.car_vel = -1.0*npl.norm(self.car_vel)*self.direction

    def update_vel(self,vel,acel):
        global speed_limit
        if not self.is_obstacle:
            if npl.norm(vel) <= self.car_stats[1]*speed_limit:
            	vel += acel+ self.friction(vel)

            elif npl.norm(vel) > self.car_stats[1]*speed_limit:
                vel = self.car_stats[1]*speed_limit*vel/npl.norm(vel)

            if npl.norm(vel) < 1.0:
                vel = np.zeros(2)

            elif abs(vel[0]) < 0.2:
                vel[0] = 0.0
            elif abs(vel[1]) < 0.2:
                vel[1] = 0.0
        else:
            if npl.norm(vel) <= self.car_stats[1]*speed_limit:
            	vel += acel

            elif npl.norm(vel) > self.car_stats[1]*speed_limit:
                vel = 40*vel/npl.norm(vel)

            if npl.norm(vel) < 1.0:
                vel = np.zeros(2)

            elif abs(vel[0]) < 0.2:
                vel[0] = 0.0
            elif abs(vel[1]) < 0.2:
                vel[1] = 0.0
        return vel

    def friction(self,vel,scaler = 1.0):
        if npl.norm(vel) > 0.2:
            return -1.0*scaler*vel/npl.norm(vel)
        else:
            return np.zeros(2)


    def update_speed(self):
        global total_limit

        self.update_carVel()

        self.car_vel = self.update_vel(self.car_vel,self.car_acel())
        if not self.is_obstacle:
            self.colision_vel = self.update_vel(self.colision_vel,np.zeros(2))
        elif self.is_obstacle:
            self.colision_vel = self.update_vel(self.colision_vel,self.friction(self.colision_vel,0.4))


        if npl.norm(self.v) <= total_limit:
            self.v = self.car_vel + self.colision_vel


        if npl.norm(self.v) > total_limit:
            self.v = total_limit*self.v/npl.norm(self.v)

        if npl.norm(self.v) < 1.0:
            self.v = np.zeros(2)

        elif abs(self.v[0]) < 0.2:
            self.v[0] = 0.0
        elif abs(self.v[1]) < 0.2:
            self.v[1] = 0.0


    def update_cords(self):
        self.pos += self.v

    def update_direction(self):
        self.direction = np.array([ np.sin(math.radians(self.angle)), np.cos(math.radians(self.angle)) ])

    #Angular Changes

    def car_turn(self):
        if npl.norm(self.v) < 0.1 or self.turn == None:
            return 0
        elif self.turn == "left":
            if np.dot(self.v,self.direction) > 0:
                return -3.0*(-self.car_stats[0] + 1)
            elif np.dot(self.v,self.direction) < 0:
                return 3.0*(-self.car_stats[0] + 1)

        elif self.turn == "right":
            if np.dot(self.v,self.direction) > 0:
                return 3.0*(-self.car_stats[0] + 1)
            elif np.dot(self.v,self.direction) < 0:
                return -3.0*(-self.car_stats[0] + 1)



    def update_angle(self):
        self.angle += self.angle_change
        if self.angle < -360:
                self.angle += 360
        if self.angle > 360:
            self.angle -= 360

    def update_angleChange(self):
        if abs(self.w) > 0.2:
            self.w -= 0.5*self.w/abs(self.w)
        elif abs(self.w) < 0.2:
            self.w = 0.0
        self.angle_change = self.w/2.0 + self.car_turn()
        if abs(self.angle_change) < 0.2:
            self.angle_change = 0.0
            self.w = 0.0



    #Image Changes


    def rotate(self,point):
        origin = self.pos[0],self.pos[1]
        originPoint = (point[0] - origin[0], point[1] - origin[1])
        rotatedX = originPoint[0] * math.cos(math.radians(-1*self.angle)) - originPoint[1] * math.sin(math.radians(-1*self.angle))
        rotatedY = originPoint[0] * math.sin(math.radians(-1*self.angle)) + originPoint[1] * math.cos(math.radians(-1*self.angle))
        return (rotatedX + origin[0], rotatedY + origin[1])



    def update_image(self):
    	oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.imageMaster,self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter



    def update_hitbox(self):
        x,y = self.pos[0] - self.size[0]/2,self.pos[1] - self.size[1]/2
        size_x,size_y = self.size[0], self.size[1] - 70
        self.hitbox = [self.rotate((x,y)),self.rotate((x,y+size_y)),
                       self.rotate((x+size_x,y+size_y)),self.rotate((x+size_x,y))]



    def update_relative(self,cameraX,cameraY):
        self.rect.center = self.pos[0] - cameraX, self.pos[1] - cameraY


    #Complete Update

    def update(self):
    	self.update_angle()
        self.update_angleChange()
        self.update_direction()
    	self.update_speed()
    	self.update_cords()
        self.update_hitbox()
    	self.update_image()


    #CollisionHandling

    def check_collision(self,target):
        "Self sofre a colisao (possui o lado)"
        a = [i[0] for i in self.hitbox]
        b = [i[1] for i in self.hitbox]
        x1_max,x1_min,y1_max,y1_min = max(a),min(a),max(b),min(b)
        for i in target.hitbox:
            if i[0] <= x1_max and i[0] >= x1_min:
                if i[1] <= y1_max and i[1] >= y1_min:
                    if self.is_obstacle == True and target.is_obstacle == True:
                        self.emparelhar(target)
                    else:
                        self.collision(target,np.array(i))
                        return True

        a = []
        b = []
        "Target recebe a colisao (possui o lado)"
        a = [i[0] for i in target.hitbox]
        b = [i[1] for i in target.hitbox]
        x1_max,x1_min,y1_max,y1_min = max(a),min(a),max(b),min(b)
        for i in self.hitbox:
            if i[0] <= x1_max and i[0] >= x1_min:
                if i[1] <= y1_max and i[1] >= y1_min:
                    if self.is_obstacle == True and target.is_obstacle == True:
                        self.emparelhar(target)
                        return True
                    target.collision(self,np.array(i))
                    return True

        return False





    def vertices_colisao(self,target,p):
        dist = []
        hitbox_alteravel = self.hitbox[:]
        for i in hitbox_alteravel:
            dist.append( npl.norm(np.array(i)-p ) )
        dist_min = min(dist)
        dist_max = max(dist)
        for i in hitbox_alteravel:
            if npl.norm(np.array(i)-p) == dist_min:
                v1 = np.array(i)
            elif npl.norm(np.array(i)-p) == dist_max:
                hitbox_alteravel.remove(i)


        dot=[]
        for i in hitbox_alteravel:
            if i != (v1[0],v1[1]):
                vetor = p - v1
                lado = np.array(i) - v1
                dot.append(abs(np.dot(vetor/npl.norm(vetor),lado/npl.norm(lado) ) ) )
        dot_max = max(dot)
        for i in hitbox_alteravel:
            if i != (v1[0],v1[1]):
                vetor = p - v1
                lado = np.array(i) - v1
                if abs(np.dot(vetor/npl.norm(vetor),lado/npl.norm(lado) ) ) == dot_max:
                    v2 = np.array(i)
                    break

        s = v2 - v1
        n = np.array([s[1],-1.0*s[0]])
        n = n/npl.norm(n)
        #print s,n


        a = [i[0] for i in self.hitbox]
        b = [i[1] for i in self.hitbox]
        x1_max,x1_min,y1_max,y1_min = max(a),min(a),max(b),min(b)
        novo_p = p + (self.size[0]/1.5 )*n
        if novo_p[0] <= x1_max and novo_p[0] >= x1_min:
            if novo_p[1] <= y1_max and novo_p[1] >= y1_min:
                n = -1.0*n
        return n







    def collision(self,target,p):
        global fps
        n = self.vertices_colisao(target,p)
        n = np.r_[n,0.0]

        ra = p - self.pos
        ra = np.r_ [ra , 0.0]
        rb = p - target.pos
        rb = np.r_ [rb , 0.0]


        self.pos -= 1.5*self.v
        self.angle -=1.5*self.angle_change
        self.update_hitbox()
    	self.update_image()
        target.pos -= 2.0*target.v
        target.angle -= 2.0*target.angle_change
        target.update_hitbox()
    	target.update_image()

        resizer = np.array([2.0/self.size[0],4.0/self.size[1],1.0])
        ra = ra*resizer
        rb = rb*resizer
        n = n*resizer
        n = n/npl.norm(n)




        e = 1.0

        Ia = self.I
        Ib = target.I
        w_object = np.array([0.0,0.0,-fps*math.radians(self.angle_change)])
        w_target = np.array([0.0,0.0,-fps*math.radians(target.angle_change)])

        v_obj = self.v
        v_target = target.v

        v_obj = np.r_[v_obj, 0.0]
        v_target = np.r_[v_target, 0.0]


        v_obj = v_obj*resizer*fps + np.cross(w_object,ra)
        v_target = v_target*resizer*fps +np.cross(w_target,rb)



        v_rel = v_obj - v_target

        j = -1.0*(1.0+e)*np.dot(v_rel,n) / ( (1/self.mass + 1/target.mass) + np.dot( (np.cross(np.cross(ra,n),ra)/Ia + np.cross(np.cross(rb,n),rb)/Ib) ,n) )

        self.car_vel = np.zeros(2)
        target.car_vel = np.zeros(2)

        """v_obj = v_obj/resizer/fps
        v_target = v_target/resizer/fps"""


        wf_object = w_object - j*np.cross(ra,n)/Ia
        wf_target = w_target + j*np.cross(rb,n)/Ib

        vf_obj_mais = v_obj + abs(j)/self.mass*n
        vf_obj_menos = v_obj - abs(j)/self.mass*n
        vf_target_mais = v_target + abs(j)/target.mass*n
        vf_target_menos = v_target - abs(j)/target.mass*n



        vf_obj_mais = vf_obj_mais/fps/resizer
        vf_obj_menos = vf_obj_menos/fps/resizer
        vf_target_mais = vf_target_mais/fps/resizer
        vf_target_menos = vf_target_menos/fps/resizer



        vf_obj_mais = np.delete(vf_obj_mais,(2))
        vf_obj_menos = np.delete(vf_obj_menos,(2))
        vf_target_mais = np.delete(vf_target_mais,(2))
        vf_target_menos = np.delete(vf_target_menos,(2))




        if np.dot(v_obj,n) < 0.0:
            self.colision_vel = vf_obj_mais
            target.colision_vel = vf_target_menos

        elif np.dot(v_obj,n) > 0.0:
            self.colision_vel = vf_obj_menos
            target.colision_vel = vf_target_mais

        elif np.dot(v_obj,n) == 0.0:
            if np.dot(v_target,n) < 0.0:
                self.colision_vel = vf_obj_menos
                target.colision_vel = vf_target_mais
            elif np.dot(v_target,n) > 0.0:
                self.colision_vel = vf_obj_mais
                target.colision_vel = vf_target_menos

        #print (self.v,self.colision_vel),(target.v,target.colision_vel)

        """vf_obj = v_obj - j/self.mass*n
        vf_target = v_target + j/target.mass*n

        vf_obj = vf_obj/fps/resizer
        vf_target = vf_target/fps/resizer

        vf_obj = np.delete(vf_obj,(2))
        vf_target = np.delete(vf_target,(2))


        self.colision_vel = vf_obj
        target.colision_vel = vf_target"""


        self.w = math.degrees(wf_object[2])/fps
        target.w = math.degrees(wf_target[2])/fps
        "print self.w,target.w"
        self.update()
        target.update()
        "time.sleep(2)"




    def emparelhar(self,target):
        """
        if npl.norm(self.v)>0:
            v_min = min(npl.norm(self.v),npl.norm(target.v) )
        elif npl.norm(self.v)<0:
            v_min = max(npl.norm(self.v),npl.norm(target.v))
        self.a = np.zeros(2)
        target.a = np.zeros(2)
        self.v = v_min*self.v/npl.norm(self.v)
        target.v = v_min*target.v/npl.norm(target.v)
        """

        if self.car_vel[1] < 0:
            v_min = max(self.car_vel[1],target.car_vel[1])
            self.car_vel[1] = v_min
            target.car_vel[1] = v_min
        if self.pos[1] > target.pos[1]:
            self.pos[1] += 30
        else:
            target.pos[1] += 30

        pass
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
