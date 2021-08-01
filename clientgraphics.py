import pygame
import config
import os
import config
from pynput.keyboard import Key, Controller
from moviepy.editor import *
from random import randint
from PIL import Image, ImageOps
import numpy as np
import colorsys
import threading
import time
import sys

class clientgraphics():
    # Initialize
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((0, 0 ),pygame.FULLSCREEN) 
        
        pygame.display.set_caption(config.WINDOW_CAPTION) 
        pygame.display.set_icon(pygame.image.load(config.WINDOW_ICON))
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        
        self.image = pygame.image.load(config.MAP_PIC) 
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.cnt = 0
        self.Clock = pygame.time.Clock()
        self.alive = True
        self.screen = config.SCREEN_NORMAL
        self.condition = config.SCREEN_NORMAL
        self.timer = time.time()
        self.vote = config.VOTE_DEFAULT
    
    # Updating the screen
    def update(self, coords, Ecoords, whereTo, legal):
        try:
            if Ecoords != "" and Ecoords != None:
                # Getting the personal stuff
                Personal = Ecoords.split(config.NETWORK_MESSAGE_DIV)[len(Ecoords.split(config.NETWORK_MESSAGE_DIV))-1].split(config.NETWORK_FIELD_DIV)
                IsImpost = Personal[0]
                self.alive = (Personal[1] == "1")
                
                # De-activating a meeting
                if self.screen == 9 and int(Personal[2]) == 0:
                    self.screen = config.SCREEN_NORMAL
                    self.vote = config.VOTE_DEFAULT
                    self.condition = config.SCREEN_NORMAL
                
                # Activating a mission / meeting
                if self.screen == config.SCREEN_NORMAL and self.alive:
                    self.screen = int(Personal[2])
                Ecoords = Ecoords[:len(Ecoords)-len(Personal)*2]
                if self.screen != config.SCREEN_NORMAL:
                    self.mission(Ecoords)
                    pygame.display.update()
                    return True
                
                # Regular Screen
                self.condition = config.SCREEN_NORMAL
                if self.alive:
                    CopyImage = self.image.copy()
                    self.drawother(Ecoords, CopyImage)
                    C = self.getcorrectsize(int(coords[0]-(config.LOAD_X/2)),int(coords[1]-(config.LOAD_Y/2)))
                    size = self.getcorrectsize(config.LOAD_X, config.LOAD_Y)
                    subsurface = CopyImage.subsurface(C[0], C[1], size[0], size[1])
                    subsurface = pygame.transform.scale(subsurface, (self.width, self.height))
                    self.display_surface.blit(subsurface, (0, 0)) 
                    
                    num = whereTo[1]
                    picture = pygame.image.load(r'char' + str(num) + '.png')
                    if whereTo[0] == config.LEFT:
                        picture = pygame.transform.flip(picture, True, False)
                        self.drawchar(picture)
                    elif whereTo[0] == config.RIGHT:
                        self.drawchar(picture)
                    elif whereTo[0][0] == config.UP:
                        if whereTo[0][1] == config.LEFT:
                            picture = pygame.transform.flip(picture, True, False)
                            self.drawchar(picture)
                        elif whereTo[0][1] == config.RIGHT:
                            self.drawchar(picture)
                    elif whereTo[0][0] == config.DOWN:
                        if whereTo[0][1] == config.LEFT:
                            picture = pygame.transform.flip(picture, True, False)
                            self.drawchar(picture)
                        elif whereTo[0][1] == config.RIGHT:
                            self.drawchar(picture)
                    self.drawRole(IsImpost)
                    self.drawStatus()
                
                # Spectator mode
                else:
                    CopyImage = self.image.copy()
                    self.drawother(Ecoords, CopyImage)
                    CopyImage = pygame.transform.scale(CopyImage, (self.width, self.height))
                    self.display_surface.blit(CopyImage, (0, 0))
                    self.drawRole(IsImpost)
                    self.drawStatus()
                
            pygame.display.update() 
            return True
        except Exception as e:
            print(e)
            return False
    
                
    def IsAlive(self):
        return self.alive
    
    def GetScreen(self):
        return self.condition
        
    def GetVote(self):
        return self.vote
    
    # Sends to a mission (mouse maze)
    def mission(self, Ecoords):
        if not self.alive:
            self.screen = config.SCREEN_NORMAL
            self.condition = config.SCREEN_NORMAL
            return
        if self.screen == 1:
            self.mission_1()
        elif self.screen == 2:
            self.mission_2()
        elif self.screen == 3:
            self.mission_3()
        elif self.screen == 4:
            self.mission_4()
        elif self.screen == 5:
            self.mission_5()
        elif self.screen == 6:
            self.mission_6()
        elif self.screen == 7:
            self.mission_7()
        elif self.screen == 8:
            self.mission_8()
        elif self.screen == 9:
            self.emergency(Ecoords)
    
    def mission_1(self):
        try:
            self.pump()
            # Activates "ON-MISSION" status
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            
            # Load
            picture = pygame.image.load(r'm1.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            
            # Checks if not outside the line
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(350,1005))
            
            # Checks if complete
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            
            # Delay of a second
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
    
    def mission_2(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm2.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(965,36))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
    
    def mission_3(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm3.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(160,1306))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
    
    def mission_4(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm4.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(785,1230))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
    
    def mission_5(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm5.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(350,1005))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
            
    def mission_6(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(1000,1000))
            picture = pygame.image.load(r'm6.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(1183,1214))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
            
    def mission_7(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm7.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(350,1005))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
            
    def mission_8(self):
        try:
            self.pump()
            if self.condition == config.SCREEN_NORMAL:
                self.condition = config.SCREEN_IN_MISSION
                pygame.mouse.set_pos(self.getcorrectsize(0,0))
            picture = pygame.image.load(r'm8.png')
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture ,(0,0))
            pygame.display.update()
            pos = pygame.mouse.get_pos()
            if self.display_surface.get_at(pos) == config.MISSION_BORDER:
                pygame.mouse.set_pos(self.getcorrectsize(350,1005))
            elif self.display_surface.get_at(pos) == config.MISSION_COMPLETE and self.condition != config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_MISSION_COMPLETED
                self.timer = time.time()
            if self.condition == config.SCREEN_MISSION_COMPLETED:
                if abs(self.timer - time.time()) > 1:
                    self.condition = config.SCREEN_NORMAL
                    self.screen = config.SCREEN_NORMAL
                    pygame.mouse.set_pos(self.getcorrectsize(0,0))
        except Exception as e:
            pass
    
    def emergency(self, Ecoords):
        try:
            # Activates "IN-MEETING" status
            if self.condition == config.SCREEN_NORMAL or self.condition == config.SCREEN_MISSION_COMPLETED:
                self.condition = config.SCREEN_IN_MEETING
            picture = pygame.image.load(config.EMERGENCY_BACK)
            picture = pygame.transform.scale(picture, (self.width, self.height))
            self.display_surface.blit(picture, (0,0))
            
            # Load
            picture = pygame.image.load(config.EMERGENCY_SQUARE)
            
            # Creates a rect and button for living characters
            if Ecoords == "":
                return
            XYlist = Ecoords.split(config.NETWORK_MESSAGE_DIV)
            ButtonList = []
            Start = [490, 327]
            for j in XYlist:
                if j.split(config.NETWORK_FIELD_DIV)[5] == "1":
                    pic = self.pilImageToSurface(self.colorize(Image.open(config.MEETING_PLAYER), int(Ecoords.split(config.NETWORK_MESSAGE_DIV)[XYlist.index(j)].split(config.NETWORK_FIELD_DIV)[4])))
                    self.display_surface.blit(picture, self.getcorrectsize(Start[0], Start[1] + 100 * XYlist.index(j)))
                    self.display_surface.blit(pic, self.getcorrectsize(Start[0]+20, Start[1] + 100 * XYlist.index(j)+self.getcorrectsizeY(9)))
            
            # Updating the vote
            temp = self.getclick(config.GETCLICK_EMERGENCY, XYlist)
            if temp != None:
                self.vote = temp
            pygame.display.update()
        except Exception as e:
            pass
    
    # Draw Role Screen Side
    def drawRole(self, Role):
        font = pygame.font.Font('el.ttf', self.getcorrectsizeX(100))
        text = font.render('Role:', True, (255,255,255))
        self.display_surface.blit(text, self.getcorrectsize(120,50))
        
        if Role == "1":
            text = font.render('Impostor', True, (255,0,0))
        else:
            text = font.render('Innocent', True, (0,255,0))
        self.display_surface.blit(text, self.getcorrectsize(425,50))
    
    # Draw Status Screen Side
    def drawStatus(self):
        font = pygame.font.Font('el.ttf', self.getcorrectsizeX(100))
        text = font.render('Status:', True, (255,255,255))
        self.display_surface.blit(text, (120,self.height-self.getcorrectsizeY(150)))
        
        if not self.alive:
            text = font.render('Dead', True, (255,0,0))
        else:
            text = font.render('Alive', True, (0,255,0))
        self.display_surface.blit(text, (550,self.height-self.getcorrectsizeY(150)))
    
    # Draws your character
    def drawchar(self, picture):
        size = picture.get_rect().size
        size = self.getcorrectsize(size[0], size[1])
        picture = pygame.transform.scale(picture, size)
        
        self.display_surface.blit(picture, (int((self.width/2)-self.getcorrectsizeX(125)),int((self.height/2)-self.getcorrectsizeY(165))))
    
    # Draw other characters on screen
    def drawotherchar(self, picture, X, Y, Pic):
        picture.set_colorkey((0,0,0,0))
        Pic.blit(picture, (X, Y))
    
    # Checks if a move is legal
    def legal(self, WhereTo):
        border = (61, 72, 74, 255)
        X, Y = int((self.width/2)-self.getcorrectsizeX(125)),int((self.height/2)-self.getcorrectsizeY(165))
        if WhereTo[0][0] == "L":
            for i in range(self.getcorrectsizeY(330)):
                for g in range(3):
                    if self.display_surface.get_at((X-g,Y+i)) == border:
                        return False
        elif WhereTo[0][0] == "R":
            X = X+ self.getcorrectsizeX(250)
            for i in range(self.getcorrectsizeY(330)):
                for g in range(3):
                    if self.display_surface.get_at((X+g,Y+i)) == border:
                        return False
        elif WhereTo[0][0] == "U":
            for i in range(self.getcorrectsizeX(250)):
                for g in range(3):
                    if self.display_surface.get_at((X+i,Y-g)) == border:
                        return False
        elif WhereTo[0][0] == "D":
            Y = Y + self.getcorrectsizeY(330)
            for i in range(self.getcorrectsizeX(250)):
                for g in range(3):
                    if self.display_surface.get_at((X+i,Y+g)) == border:
                        return False
        return True

    # Drawing other chars
    def drawother(self, Ecoords, Pic):
        try:
            if Ecoords == "":
                return
            XYlist = Ecoords.split(config.NETWORK_MESSAGE_DIV)
            for XY in XYlist:
                if XY == "":
                    continue
                All = XY.split(config.NETWORK_FIELD_DIV)
                X = int(All[0])
                Y = int(All[1])
                X,Y = self.getcorrectsize(X,Y)
                Direction = All[2]
                Walking = All[3]
                Hue = (int(All[4]))
                Alive = All[5]
                num = 0
                if int(Walking) == 1:
                    num = 3
                else:
                    num = 2
                picture = ""
                if Alive == "0":
                    picture = Image.open(config.DEAD)
                else:
                    picture = Image.open(r'char' + str(num) + '.png')
                
                picture = self.colorize(picture, Hue)
                picture = self.pilImageToSurface(picture)
                picture = pygame.transform.scale(picture, self.getcorrectsizetupple(picture.get_rect().size))
                if Direction == "L" and Alive == "1":
                    picture = pygame.transform.flip(picture, True, False)
                
                self.drawotherchar(picture, X, Y, Pic)
        except Exception as e:
            print(e)
            return
            
    # Change Hue
    def shift_hue(self, arr, hout):
        rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
        hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
        r, g, b, a = np.rollaxis(arr, axis=-1)
        h, s, v = rgb_to_hsv(r, g, b)
        h = hout
        r, g, b = hsv_to_rgb(h, s, v)
        arr = np.dstack((r, g, b, a))
        return arr

    def colorize(self, image, hue):
        """
         PIL image `original` with the given
        `hue` (hue within 0-360); returns another PIL image.
        """
        img = image.convert('RGBA')
        arr = np.array(np.asarray(img).astype('float'))
        new_img = Image.fromarray(self.shift_hue(arr, hue/360.).astype('uint8'), 'RGBA')

        return new_img
    
    def pilImageToSurface(self, pilImage):
        return pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
    
    def SurfaceToPILImage(self, pysurface):
        return Image.frombytes("RGBA",(pysurface.get_rect().size),pygame.image.tostring(pysurface, "RGBA",False))
    
    # Blitting opening screen
    def openingscreen(self):
        picture = pygame.image.load("open.png")
        picture = pygame.transform.scale(picture, (self.width, self.height))
        self.display_surface.blit(picture, (0, 0))
        pygame.display.update()
    
    # Getting the size according to screen
    def getcorrectsizetupple(self, tup):
        return (int(tup[0]*self.width/config.DEFAULT[0]), int(tup[1]*self.height/config.DEFAULT[1]))
    
    def getcorrectsize(self, X, Y):
        return (int(X*self.width/config.DEFAULT[0]), int(Y*self.height/config.DEFAULT[1]))
    
    def getcorrectsizeX(self, X):
        return int(X*self.width/config.DEFAULT[0])
    
    def getcorrectsizeY(self, Y):
        return int(Y*self.height/config.DEFAULT[1])
    
    # Gets if clicked and / or hovered and colors
    def getclick(self, mode, playernum = []):
        if mode == config.GETCLICK_OPENING:
            PlayButton = pygame.Rect(self.getcorrectsize(805,854), self.getcorrectsize(474*2,94*2))
            HOW_TOButton = pygame.Rect(self.getcorrectsize(805,1080), self.getcorrectsize(474*2,120))
            EXIT_Button = pygame.Rect(self.getcorrectsize(33,1308), self.getcorrectsize(226,112))
            
            self.Clock.tick(2)

            self.cnt = (self.cnt + 1) % 255
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  # gets mouse position
                    # checks if mouse position is over the button
                    if PlayButton.collidepoint(mouse_pos):
                        pygame.display.update()
                        return False
                    if HOW_TOButton.collidepoint(mouse_pos):
                        self.play_HOWTO()
                        self.openingscreen()
                    if EXIT_Button.collidepoint(mouse_pos):
                        return True
                    
                    
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    new_surface = self.display_surface.copy()
                    if PlayButton.collidepoint(mouse_pos):
                        if self.display_surface.get_at(self.getcorrectsize(880,860)) == config.HOVERED_WHITE:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(880), self.getcorrectsizeY(860), (0,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()
                    else:
                        if self.display_surface.get_at(self.getcorrectsize(880,860)) == config.HOVERED_AQUA:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(880), self.getcorrectsizeY(860), (255,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()
                    
                    if HOW_TOButton.collidepoint(mouse_pos):
                        if self.display_surface.get_at(self.getcorrectsize(880,1084)) == config.HOVERED_WHITE:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(880), self.getcorrectsizeY(1084), (0,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()     
                    else:
                        if self.display_surface.get_at(self.getcorrectsize(880,1084)) == config.HOVERED_AQUA:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(880), self.getcorrectsizeY(1084), (255,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()
                    
                    if EXIT_Button.collidepoint(mouse_pos):
                        if self.display_surface.get_at(self.getcorrectsize(50,1300)) == config.HOVERED_WHITE:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(50), self.getcorrectsizeY(1300), (0,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()
                    else:
                        if self.display_surface.get_at(self.getcorrectsize(50,1300)) == config.HOVERED_AQUA:
                            new_surface = self.flood_fill(new_surface,  self.getcorrectsizeX(50), self.getcorrectsizeY(1300), (255,255,255))
                            self.display_surface.blit(new_surface, (0,0))
                            pygame.display.update()
        elif mode == config.GETCLICK_EMERGENCY:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    Start = [490, 327]
                    for i in playernum:
                        if i.split(config.NETWORK_FIELD_DIV)[5] == "1":
                            Button = pygame.Rect(self.getcorrectsize(Start[0], Start[1] + 100 * playernum.index(i)), self.getcorrectsize(232,40))
                            if Button.collidepoint(event.pos):
                                return playernum.index(i)
                    
                    
    # replaces all points of same starting colour, 
    # with a new colour, up to a border with 
    # different starting colour
    def flood_fill(self, surface, x, y, newColor):
        theStack = [(x, y)]
        oldColor = surface.get_at((x,y))    # Get starting colour
        while len(theStack) > 0:
            x, y = theStack.pop()
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                continue
            if surface.get_at((x,y)) != oldColor:
                continue
            surface.set_at((x,y),newColor)
            # pygame.display.update()   # Show fill - very slow
            theStack.append( (x + 1, y) )  # right
            theStack.append( (x - 1, y) )  # left
            theStack.append( (x, y + 1) )  # down
            theStack.append( (x, y - 1) )  # up
        return surface
    
    # Plays Clips
    def play_HOWTO(self):
        clip = VideoFileClip(config.HOWTO_VIDEO)
        clip = clip.volumex(1)
        clip = clip.resize((self.width,self.height))
        clip.preview()
    
    def play_START(self):
        clip = VideoFileClip(config.START_VIDEO)
        clip = clip.volumex(1)
        clip = clip.resize((self.width,self.height))
        clip.preview()
    
    def tick(self, ticks = 60):
        self.Clock.tick(ticks)
    
    # Draw shiny circles when cant connect to server
    def Glow(self, ticks):
        for i in range(ticks):
            self.cnt = (self.cnt + 1) %40
            pygame.draw.circle(self.display_surface, (randint(0,255),randint(0,255),randint(0,255)), (int(self.width/2),int(self.height/2)), self.cnt)
            pygame.display.update()
    
    # Pumps events
    def pump(self):
        pygame.event.pump()
    
    # Displays waiting screen
    def WaitingScreen(self, Players):
        self.display_surface.fill((0,0,1))
        font = pygame.font.Font('freesansbold.ttf', self.getcorrectsizeX(128))
        text = font.render('There are:', True, (255,255,255))
        self.display_surface.blit(text, self.getcorrectsize(900,300))#, self.getcorrectsize(480,853))
        
        Otherfont = pygame.font.Font('freesansbold.ttf', self.getcorrectsizeX(400))
        text = Otherfont.render(f'{Players}', True, (255,255,255))
        self.display_surface.blit(text, self.getcorrectsize(1100,450))
        
        text = font.render('Players Online (Waiting for 3)', True, (255,255,255))
        self.display_surface.blit(text, self.getcorrectsize(400,1000))
        
        pygame.display.update()
    
    # Displays end screen
    def EndScreen(self, Winner):
        if Winner == "Crew":
            pic = pygame.image.load(config.END_CREW)
            pic = pygame.transform.scale(pic, (self.width, self.height))
            self.display_surface.blit(pic, (0,0))
            pygame.display.update()
            
        else:
            pic = pygame.image.load(config.END_IMPOST)
            pic = pygame.transform.scale(pic, (self.width, self.height))
            self.display_surface.blit(pic, (0,0))
            pygame.display.update()
            
    
    def Quit(self):
        pygame.quit()
        