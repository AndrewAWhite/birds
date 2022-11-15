# import the pygame module, so you can use it
import pygame
import pygame_menu
import random
import math

MENU_W = 300
SCREEN_W = 1800	
SCREEN_H = 980

def get_random_direction():
	return -1^(random.randint(1, 2))

def find_closest_birds(b, birds):
	return sorted(birds, key=lambda cb: math.sqrt((math.pow((cb.x-b.x), 2) + math.pow((cb.y - b.y), 2))))[:2]

class Bird(pygame.sprite.Sprite):
	def __init__(self, i, space):
		super().__init__()
		self.i = i
		self.x = random.randint(MENU_W, SCREEN_W-MENU_W-10)
		self.y = random.randint(1, SCREEN_H-10)
		self.space = space
		while self.space[self.x][self.y] is not None:
			self.x = random.randint(MENU_W, SCREEN_W-MENU_W-10)
			self.y = random.randint(1, SCREEN_H-10)
		self.space[self.x][self.y] = self
		self.v = [0, 0]
		self.surf = pygame.Surface((3, 3))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(center = (3, 3))

	def get_neighbours(self):
		closest_birds = []
		for cb in self.space[self.x][self.y:]:
			if cb is not None and cb.i != self.i:
				closest_birds.append(cb)
				break
		for cb in reversed(self.space[self.x][:self.y]):
			if cb is not None and cb.i != self.i:
				closest_birds.append(cb)
				break
		ob = False
		for sr in reversed(self.space[:self.x]):
			for cb in sr[self.y:]:
				if cb is not None and cb.i != self.i:
					closest_birds.append(cb)
					ob = True
					break
			for cb in reversed(sr[:self.y]):
				if cb is not None and cb.i != self.i:
					closest_birds.append(cb)
					ob = True
					break
			if ob:
				break
		ob = False
		for sr in self.space[self.x:]:
			for cb in sr[self.y:]:
				if cb is not None and cb.i != self.i:
					closest_birds.append(cb)
					ob = True
					break
			for cb in reversed(sr[:self.y]):
				if cb is not None and cb.i != self.i:
					closest_birds.append(cb)
					ob = True
					break
			if ob:
				break
		return closest_birds

	def get_accel_fn(self, d):
		return  ((1 / (1 + math.pow(2, -(abs(d)-2)))) - 0.5)

	def determine_attraction(self, cb):
		dx = cb.x - self.x
		dy = cb.y - self.y
		accel_x = self.get_accel_fn(dx)
		accel_y = self.get_accel_fn(dy)
		if dx < 0:
			accel_x *= -1
		if dy < 0:
			accel_y *= -1
		return accel_x, accel_y

	def accelerate(self):
		closest_birds = self.get_neighbours()
		for cb in closest_birds:
			accel_x, accel_y = self.determine_attraction(cb)
			self.v[0] += accel_x
			self.v[1] += accel_y

	def move(self):
		self.accelerate()
		self.x += int(self.v[0])
		self.y += int(self.v[1])


def get_theme():
	theme = pygame_menu.Theme(
		background_color=(0,0,0,0),
		widget_font=pygame_menu.font.FONT_NEVIS,
		widget_alignment=pygame_menu.locals.ALIGN_LEFT,
		title_font_size=20,
		widget_font_size=20,
		border_color=((255, 255, 255, 255)),
		border_width=1,
		widget_border_width=0,
		widget_offset=(2, 2),
		widget_selection_effect=pygame_menu.widgets.NoneSelection()
	)
	return theme

def get_menu():
	theme = get_theme()
	menu = pygame_menu.Menu('Birds', MENU_W, SCREEN_H, theme=theme, position=(0, 0))
	menu.add.range_slider('stickiness', 10, [0,100], 1, rangeslider_id='stickiness', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('trickiness', 10, [0,100], 1, rangeslider_id='trickiness', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	return menu

def scale_slider_pos(slider_val):
	return int(MENU_W + slider_val * (SCREEN_W-MENU_W)/100)

# define a main function
def main():
	FramePerSec = pygame.time.Clock()
	# initialize the pygame module
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
	pygame.display.set_caption("birds")
	menu = get_menu()
	# define a variable to control the main loop
	running = True
	space = [[None for _ in range(SCREEN_H)] for _ in range(SCREEN_W-MENU_W)]
	birds = [Bird(i, space) for i in range(2)]
	# main loop
	while running:
		screen.fill((0,0,0))
		for b in birds:
			b.move()
			screen.blit(b.surf, (b.x, b.y))
		#pygame.display.flip()
		# event handling, gets all event from the event queue
		events = pygame.event.get()
		for event in events:
			# only do something if the event is of type QUIT
			if event.type == pygame.QUIT:
				# change the value to False, to exit the main loop
				running = False
		menu.update(events)
		menu.draw(screen)
		pygame.display.update()
		FramePerSec.tick(120)
	 
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
	# call the main function
	main()