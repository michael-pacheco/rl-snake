'''
MiniSnake.py

A game of self.snake in one .py file


This program by Daniel Westbrook
website: www.pixelatedawesome.com
email: thepixelator72@gmail.com
	   (or whatever email I list on my site, if I stop using that one)

Legal shit:
	Copyright (C) 2008 Daniel Westbrook

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Lesser General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Lesser General Public License for more details.

	You should have received a copy of the GNU Lesser General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import pygame
from pygame.locals import *
import random
from config import reward_in_env, reward_on_eat, death_reward

# ---------- constants ---------- #
SCREENSIZE = (300, 300)
SCREENRECT = pygame.Rect(0, 0, SCREENSIZE[0], SCREENSIZE[1])
CAPTION = 'MiniSnake'
FPS = 40

START_TILE = (20, 20)
START_SEGMENTS = 7

MOVE_RATE = 2
DIFFICULTY_INCREASE_RATE = .05
MOVE_THRESHOLD = 5 # when moverate counts up to this the self.snake moves
BLOCK_SPAWN_RATE = 2

TILE_SIZE = (10, 10)
TILE_RECT = pygame.Rect(0, 0, TILE_SIZE[0], TILE_SIZE[1])

SCREENTILES = ((SCREENSIZE[0] / TILE_SIZE[0]) - 1, (SCREENSIZE[1] / TILE_SIZE[1]) - 1)

SNAKE_HEAD_RADIUS = 5
SNAKE_SEGMENT_RADIUS = 4
FOOD_RADIUS = 4

BACKGROUND_COLOR = (255, 255, 255)
SNAKE_HEAD_COLOR = (150, 1, 1)
SNAKE_SEGMENT_COLOR = (255, 1, 1)
FOOD_COLOR = (1, 255, 1)
BLOCK_COLOR = (1, 1, 150)
COLORKEY_COLOR = (255, 255, 1)

SCORE_COLOR = (1, 1, 1)
SCORE_POS = (20, 20)
SCORE_PREFIX = ''

MOVE_VECTORS = {'left' : (-1, 0),
				'right' : (1, 0),
				'up' : (0, -1),
				'down' : (0, 1)
				}
MOVE_VECTORS_PIXELS = {'left' : (-TILE_SIZE[0], 0),
					   'right' : (TILE_SIZE[0], 0),
					   'up' : (0, -TILE_SIZE[1]),
					   'down' : (0, TILE_SIZE[1])
					   }


# ----------- game objects ----------- #
class snake_segment(pygame.sprite.Sprite):
	def __init__(self, tilepos, segment_groups, color = SNAKE_SEGMENT_COLOR, radius = SNAKE_SEGMENT_RADIUS):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, color, TILE_RECT.center, radius)

		self.tilepos = tilepos

		self.rect = self.image.get_rect()
		self.rect.topleft = (tilepos[0] * TILE_SIZE[0], tilepos[1] * TILE_SIZE[1])

		self.segment_groups = segment_groups
		for group in segment_groups:
			group.add(self)

		self.behind_segment = None

		self.movedir = 'left'

	def add_segment(self):
		seg = self
		while True:
			if seg.behind_segment == None:
				x = seg.tilepos[0]
				y = seg.tilepos[1]
				if seg.movedir == 'left':
					x += 1
				elif seg.movedir == 'right':
					x -= 1
				elif seg.movedir == 'up':
					y += 1
				elif seg.movedir == 'down':
					y -= 1
				seg.behind_segment = snake_segment((x, y), seg.segment_groups)
				seg.behind_segment.movedir = seg.movedir
				break
			else:
				seg = seg.behind_segment

	def update(self):
		pass

	def move(self):
		self.tilepos = (self.tilepos[0] + MOVE_VECTORS[self.movedir][0], self.tilepos[1] + MOVE_VECTORS[self.movedir][1])
		self.rect.move_ip(MOVE_VECTORS_PIXELS[self.movedir])
		if self.behind_segment != None:
			self.behind_segment.move()
			self.behind_segment.movedir = self.movedir

class snake_head(snake_segment):
	def __init__(self, tilepos, movedir, segment_groups):
		snake_segment.__init__(self, tilepos, segment_groups, color = SNAKE_HEAD_COLOR, radius = SNAKE_HEAD_RADIUS)
		self.movedir = movedir
		self.movecount = 0

	def update(self):
		self.movecount += MOVE_RATE
		if self.movecount > MOVE_THRESHOLD:
			self.move()
			self.movecount = 0

class food(pygame.sprite.Sprite):
	def __init__(self, takenupgroup):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, FOOD_COLOR, TILE_RECT.center, FOOD_RADIUS)

		self.rect = self.image.get_rect()
		while True:
			self.rect.topleft = (random.randint(0, SCREENTILES[0]) * TILE_SIZE[0], random.randint(0, SCREENTILES[1]) * TILE_SIZE[1])
			for sprt in takenupgroup:
				if self.rect.colliderect(sprt):
					continue # collision, food cant go here
			break # no collision, food can go here

class block(pygame.sprite.Sprite):
	def __init__(self, takenupgroup):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(BLOCK_COLOR)

		self.rect = self.image.get_rect()
		while True:
			self.rect.topleft = (random.randint(0, SCREENTILES[0]) * TILE_SIZE[0], random.randint(0, SCREENTILES[1]) * TILE_SIZE[1])
			for sprt in takenupgroup:
				if self.rect.colliderect(sprt):
					continue # collision, food cant go here
			break # no collision, food can go here


class game():
	def __init__(self):
		pygame.init()
		self.prev_key = 0
		self.screen = pygame.display.set_mode(SCREENSIZE)
		pygame.display.set_caption(CAPTION)
		self.bg = pygame.Surface(SCREENSIZE).convert()
		self.bg.fill(BACKGROUND_COLOR)
		self.screen.blit(self.bg, (0, 0))

		self.snakegroup = pygame.sprite.Group()
		self.snakeheadgroup = pygame.sprite.Group()
		self.foodgroup = pygame.sprite.Group()
		self.blockgroup = pygame.sprite.Group()
		self.takenupgroup = pygame.sprite.Group()
		self.all = pygame.sprite.RenderUpdates()

		self.snake = snake_head(START_TILE, 'right', [self.snakegroup, self.all, self.takenupgroup])
		self.snakeheadgroup.add(self.snake)
		for index in range(START_SEGMENTS):
			self.snake.add_segment()

		self.currentfood = 'no food'

		self.block_frame = 0

		self.currentscore = 0

		pygame.display.flip()

		# mainloop
		self.quit = False
		self.clock = pygame.time.Clock()
		self.lose = False


	def play(self, action):
		#init reward
		reward = reward_in_env


		#if dead, restart
		if self.lose:
			self.__init__()

		#interpret keypress
		if self.prev_key != action:
			pygame.event.post(pygame.event.Event(KEYUP, key=self.prev_key))
			pygame.event.post(pygame.event.Event(KEYDOWN, key=action))

		self.prev_key = action
		pygame.event.pump()
		# events
		for event in pygame.event.get():
			if event.type == self.quit:
				self.quit = True
			elif event.type == KEYDOWN:
				currentmovedir = self.snake.movedir
				if event.key == K_UP:
					tomove = 'up'
					dontmove = 'down'
				elif event.key == K_DOWN:
					tomove = 'down'
					dontmove = 'up'
				elif event.key == K_LEFT:
					tomove = 'left'
					dontmove = 'right'
				elif event.key == K_RIGHT:
					tomove = 'right'
					dontmove = 'left'
				else:
					raise Exception(RuntimeError, 'not expected')
				if not currentmovedir == dontmove:
					self.snake.movedir = tomove

		# clearing
		self.all.clear(self.screen, self.bg)

		# updates
		self.all.update()

		if self.currentfood == 'no food':
			self.currentfood = food(self.takenupgroup)
			self.foodgroup.add(self.currentfood)
			self.takenupgroup.add(self.currentfood)
			self.all.add(self.currentfood)

		pos = self.snake.rect.topleft
		if pos[0] < 0:
			self.quit = True
			self.lose = True
		if pos[0] >= SCREENSIZE[0]:
			self.quit = True
			self.lose = True
		if pos[1] < 0:
			self.quit = True
			self.lose = True
		if pos[1] >= SCREENSIZE[1]:
			self.quit = True
			self.lose = True

		# collisions
		# head -> tail
		col = pygame.sprite.groupcollide(self.snakeheadgroup, self.snakegroup, False, False)
		for head in col:
			for tail in col[head]:
				if not tail is self.snake:
					self.quit = True
					self.lose = True
		# head -> food
		col = pygame.sprite.groupcollide(self.snakeheadgroup, self.foodgroup, False, True)
		for head in col:
			for tail in col[head]:
				self.currentfood = 'no food'
				self.snake.add_segment()
				self.currentscore += 1
				global MOVE_RATE, DIFFICULTY_INCREASE_RATE
				MOVE_RATE += DIFFICULTY_INCREASE_RATE
				self.block_frame += 1
				reward = reward_on_eat
				if self.block_frame >= BLOCK_SPAWN_RATE:
					self.block_frame = 0
					b = block(self.takenupgroup)
					self.blockgroup.add(b)
					self.takenupgroup.add(b)
					self.all.add(b)
		# head -> blocks
		col = pygame.sprite.groupcollide(self.snakeheadgroup, self.blockgroup, False, False)
		for head in col:
			for collidedblock in col[head]:
				self.quit = True
				self.lose = True

		# score
		d = self.screen.blit(self.bg, SCORE_POS, pygame.Rect(SCORE_POS, (50, 100)))
		f = pygame.font.Font(None, 12)
		scoreimage = f.render(SCORE_PREFIX, True, SCORE_COLOR)
		d2 = self.screen.blit(scoreimage, SCORE_POS)

		# drawing
		dirty = self.all.draw(self.screen)
		dirty.append(d)
		dirty.append(d2)

		# updating
		pygame.display.update(dirty)

		# waiting
		self.clock.tick(FPS)
		if self.lose:
			reward = death_reward

		image_data = pygame.surfarray.array3d(pygame.display.get_surface())

		return reward, image_data, self.lose




def main():
	game_engine = game()
	while True:
		reward, image, death = game_engine.play()
		print(reward, death)


if __name__ == "__main__":
	main()
