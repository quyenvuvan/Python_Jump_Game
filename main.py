import pygame
import sys
import os

from scripts.entities import *
from scripts.utils import *
from scripts.tilemap import *
from scripts.clouds import *
from scripts.particles import *
from scripts.spark import Spark
from scripts.text import *

class Game:
	def __init__(self):
		pygame.init()

		pygame.display.set_caption("OUR PROJECT")

		self.screen=pygame.display.set_mode((900,600))
		self.display=pygame.Surface((300,200),pygame.SRCALPHA)
		self.display_2=pygame.Surface((300,200))

		self.clock=pygame.time.Clock()

		self.movement=[False,False]

		self.assets={
			'decor': load_images('tiles/decor'),
			'mush': load_images('tiles/mush'),
			'grass1x3': load_images('tiles/grass1x3'),
			'grass3x3': load_images('tiles/grass3x3'),
			'stone': load_images('tiles/stone'),
			'large_decor': load_images('tiles/large_decor'),
			'background':load_image('background.png'),
			'cloud':load_images('clouds'),
			'spawners': load_images('tiles/spawners'),
			'enemy/idle': Animation(load_images('entities/enemy/idle'),img_dur=10),
			'enemy/run': Animation(load_images('entities/enemy/run'),img_dur=4),
			'player/idle': Animation(load_images('entities/player/idle'),img_dur=10),
			'player/run': Animation(load_images('entities/player/run'),img_dur=4),
			'player/jump': Animation(load_images('entities/player/jump')),
			'player/slide': Animation(load_images('entities/player/slide')),
			'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
			'particle/particle': Animation(load_images('particles/particle'),img_dur=6,loop=False),
			'ball': Animation(load_images('entities/ball'),img_dur=8),
			'trap':Animation(load_images('entities/trap'),img_dur=20),
			'gun': load_image('gun.png'),
            'spore': load_image('spore.png'),
		}

		self.clouds=Clouds(self.assets['cloud'],8)
		self.player=Player(self,(0,0),(16,16),anim_offset=(0,2))
		self.balls=[]
		self.tilemap=Tilemap(self,tile_size=16)
		
		self.level=0
		
		self.load_level('0')
		self.screenshake=0

	def load_level(self,map_id):
		self.tilemap.load('data/maps/'+map_id+'.json')
		self.enemies=[]
		self.balls=[]
		self.collected=0
		self.traps=[]
		for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1),('spawners',2),('spawners',3)]):
			if spawner['variant'] == 0:
				self.player.pos=spawner['pos']
				self.player.air_time=0
			elif spawner['variant']==1:
				self.enemies.append(Enemy(self,spawner['pos'],(16,16),anim_offset=(0,2)))
			elif spawner['variant']==2:
				self.balls.append(Ball(self,spawner['pos'],(11,11)))
			elif spawner['variant']==3:
				self.traps.append(Trap(self,spawner['pos'],(15,15)))

		self.non_collected=len(self.balls)
		self.spores=[]
		self.particles=[]
		self.sparks=[]
		
		self.scroll=[0,0]
		self.transition=-30
		self.dead=0
		self.tutorial=True
		self.timing=0

	def run(self):
		while True:
			self.timing+=1
			if not len(self.balls):
				self.transition+=1
				if self.transition>30:
					self.level=min(self.level+1,len(os.listdir('data/maps')))
					self.load_level(str(self.level))
			if self.transition<0:
				self.transition+=1

			if self.dead:
				self.dead+=1
				if self.dead>=10:
					self.transition=min(30,self.transition+1)
				if self.dead>40:
					self.load_level(str(self.level))

			self.display.fill((0,0,0,0))
			self.display_2.blit(self.assets['background'],(0,0))

			self.screenshake=max(0,self.screenshake-1)
						
			self.scroll[0]+=(self.player.rect().centerx-self.display.get_width()/2 - self.scroll[0])/30
			self.scroll[1]+=(self.player.rect().centery/1.5-self.display.get_height()/2 - self.scroll[1])/30
			render_scroll=(int(self.scroll[0]),int(self.scroll[1]))

			self.clouds.update()
			self.clouds.render(self.display_2,render_scroll)

			self.tilemap.render(self.display,offset=render_scroll)

			
			for ball in self.balls:
				ball.render(self.display,offset=render_scroll)
				if self.player.rect().colliderect(ball.rect()):
					for i in range (30):
						angle=random.random()*math.pi*2
						self.particles.append(Particle(self,'particle',ball.rect().center,velocity=[math.cos(angle+math.pi),math.sin(angle+math.pi)],frame=random.randint(0,7)))
					self.balls.remove(ball)
					self.collected+=1
			
			for trap in self.traps:
				trap.render(self.display,offset=render_scroll)
				if trap.rect().colliderect(self.player):
					self.screenshake=max(self.screenshake,50)
					self.traps.remove(trap)
					self.dead+=1
					for i in range(30):
						angle=random.random()*math.pi*2
						speed=random.random()*5
						self.sparks.append(Spark(self.player.rect().center,angle,2+random.random()))
						self.particles.append(Particle(self,'particle',self.player.rect().center,velocity=[math.cos(angle+math.pi)*speed*0.5,math.sin(angle+math.pi)*speed*0.5],frame=random.randint(0,7)))

			if not self.dead:
				self.player.update(self.tilemap,(self.movement[1]-self.movement[0],0)) 
				self.player.render(self.display,offset=render_scroll)

			#[pos,dir,timer]
			for spore in self.spores.copy():
				spore[0][0]+=spore[1]*2
				spore[2]+=1
				img=self.assets['spore']
				self.particles.append(Particle(self,'particle',(spore[0][0]+5,spore[0][1]+img.get_height()/2),velocity=(0,0),frame=random.randint(0,7)))
				self.display.blit(img,(spore[0][0]-img.get_width()/2-render_scroll[0],spore[0][1]-render_scroll[1]))
				if self.tilemap.solid_check(spore[0]):
					self.spores.remove(spore)
					self.particles.pop()
					for i in range(4):
						self.sparks.append(Spark(spore[0],random.random()-0.5+(math.pi if spore[1]>0 else 0),2+random.random()))
				elif spore[2]>360:
					self.spores.remove(spore)
				elif abs(self.player.dashing)<50:
					if self.player.rect().collidepoint(spore[0]):
						self.screenshake=max(self.screenshake,50)
						self.spores.remove(spore)
						self.dead+=1
						for i in range(30):
							angle=random.random()*math.pi*2
							speed=random.random()*5
							self.sparks.append(Spark(self.player.rect().center,angle,2+random.random()))
							self.particles.append(Particle(self,'particle',self.player.rect().center,velocity=[math.cos(angle+math.pi)*speed*0.5,math.sin(angle+math.pi)*speed*0.5],frame=random.randint(0,7)))
			
			for enemy in self.enemies:
				kill=enemy.update(self.tilemap,movement=(0,0))
				enemy.render(self.display,offset=render_scroll)
				if enemy.rect().colliderect(self.player) and not self.player.dashing:
					self.screenshake=max(self.screenshake,50)
					self.enemies.remove(enemy)
					self.dead+=1
					for i in range(30):
						angle=random.random()*math.pi*2
						speed=random.random()*5
						self.sparks.append(Spark(self.player.rect().center,angle,2+random.random()))
						self.particles.append(Particle(self,'particle',self.player.rect().center,velocity=[math.cos(angle+math.pi)*speed*0.5,math.sin(angle+math.pi)*speed*0.5],frame=random.randint(0,7)))
				if kill:
					self.enemies.remove(enemy)

			for spark in self.sparks.copy():
				kill=spark.update()
				spark.render(self.display,offset=render_scroll)
				if kill:
					self.sparks.remove(spark)

			my_font=Font('data/fonts/small_font.png',(255,255,255))
			my_font2=Font('data/fonts/large_font.png',(255,255,255))
			self.display.blit(load_image('ball.png'),(4,6))
			my_font.render(self.display,str(self.collected)+'/'+str(self.non_collected),(13,5))


			tmp= 1 if self.timing % 90 > 80 else 0			
			if self.tutorial:
				my_font.render(self.display,'collect all the balls',(self.player.rect().centerx-render_scroll[0]-my_font.width('collect all the balls')//2,self.player.pos[1]-render_scroll[1]-20+tmp))
			
			for particle in self.particles.copy():
				kill = particle.update()
				particle.render(self.display, offset=render_scroll)
				if kill:
					self.particles.remove(particle)

			#tao mask cho phan noi
			display_mask=pygame.mask.from_surface(self.display)
			display_sillhouette=display_mask.to_surface(setcolor=(0,0,0,180),unsetcolor=(0,0,0,0))
			offset=((0,1),(1,0),(0,-1),(-1,0))
			for o in offset:
				self.display_2.blit(display_sillhouette,o)

			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type==pygame.KEYDOWN:
					self.tutorial=False
					if event.key==pygame.K_LEFT:
						self.movement[0]=True
					if event.key==pygame.K_RIGHT:
						self.movement[1]=True
					if event.key==pygame.K_UP:
						self.player.jump()
					if event.key==pygame.K_SPACE:
						self.player.dash()

				if event.type==pygame.KEYUP:
					if event.key==pygame.K_LEFT:
						self.movement[0]=False
					if event.key==pygame.K_RIGHT:
						self.movement[1]=False
			

			if self.transition:
				transition_surf=pygame.Surface(self.display.get_size())
				pygame.draw.circle(transition_surf,(255,255,255),(self.display.get_width()//2,self.display.get_height()//2),(30-abs(self.transition))*8)
				transition_surf.set_colorkey((255,255,255))
				self.display.blit(transition_surf,(0,0))

			self.display_2.blit(self.display,(0,0))
			screenshake_offset=(random.random()*self.screenshake-self.screenshake/2,random.random()*self.screenshake-self.screenshake/2)
			self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
			pygame.display.update()
			self.clock.tick(60)

Game().run()