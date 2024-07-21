import pygame
import os

BASE_IMG_PATH='data/images/'

def load_image(path):
    img=pygame.image.load(BASE_IMG_PATH+path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_images(path):
    imgs=[]
    for img_name in os.listdir(BASE_IMG_PATH+path):
        imgs.append(load_image(path+'/'+img_name))
    return imgs

class Animation:
    def __init__(self,imgs,img_dur=5,loop=True):
        self.imgs=imgs
        self.loop=loop
        self.img_dur=img_dur
        self.done=False
        self.frame=0

    def copy(self):
        return Animation(self.imgs,self.img_dur,self.loop)
    
    def update(self):
        if self.loop:
            self.frame=(self.frame+1)%(self.img_dur*len(self.imgs))
        else:
            self.frame=min(self.frame+1,self.img_dur*len(self.imgs)-1)
            if self.frame>=self.img_dur*len(self.imgs)-1:
                self.done=True

    def img(self):
        return self.imgs[int(self.frame/self.img_dur)]
    