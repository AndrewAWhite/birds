# import the pygame module, so you can use it
import pygame
import pygame_menu
import random
import math

MENU_W = 300
SCREEN_W = 1800	
SCREEN_H = 980
WINDOW_W = SCREEN_W - MENU_W

BIRDS=None
BIRD_COUNT=250

MAX_ACCELERATION = 100
ACCELERATION = 0.01
REPULSIVE_DISTANCE = 40
REPULSIVE_POWER = 1
MAX_SPEED = 100
MOUSE_ATTRACTION = 0.001

MOUSE_X, MOUSE_Y = 0, 0

def get_random_direction():
	return -1^(random.randint(1, 2))

def find_closest_birds(b, birds):
	return sorted(birds, key=lambda cb: math.sqrt((math.pow((cb.x-b.x), 2) + math.pow((cb.y - b.y), 2))))[:2]

class Bird(pygame.sprite.Sprite):
	def __init__(self, i, grid):
		super().__init__()
		self.i = i
		self.grid = grid
		self.x = random.randint(MENU_W, WINDOW_W-10)
		self.y = random.randint(1, SCREEN_H-10)
		self.v = [0, 0]
		self.grid_key = self.get_grid_key()
		self.update_grid()
		self.surf = pygame.Surface((3, 3))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(center = (3, 3))
		self.neigbours = None
		self.get_neighbours()

	def get_grid_key(self):
		x = math.floor(self.x / WINDOW_W)*100
		y = math.floor(self.y/SCREEN_W)*100
		return (x,y)

	def update_grid(self):
		cur_spot = self.grid.get(self.grid_key, set())
		if self in cur_spot:
			cur_spot.remove(self)
		self.grid[self.grid_key] = cur_spot
		new_key = self.get_grid_key()
		neighbours = self.grid.get(new_key, set())
		neighbours.add(self)
		self.grid[new_key] = neighbours
		self.grid_key = new_key

	def get_distance(self, x, y):
		dx = x - self.x
		dy = y - self.y
		d = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
		return d

	def get_neighbours(self):
		neighbours =  self.grid.get(self.grid_key, set())
		if len(neighbours) == 0:
			pass
		self.neigbours = [cb for cb in neighbours if cb.i != self.i][:4]
			
	def get_attraction(self, x, y, mult=ACCELERATION):
		ax =  mult * math.pow((x - self.x)/5, 2)
		ay = mult * math.pow((y - self.y)/5, 2)
		if ax > MAX_ACCELERATION:
			ax = MAX_ACCELERATION
		if ay > MAX_ACCELERATION:
			ay = MAX_ACCELERATION
		if x - self.x < 0:
			ax *= -1
		if y - self.y < 0:
			ay *= -1
		return ax, ay

	def get_repulsion(self, x, y):
		try:
			ax = REPULSIVE_POWER / (1-math.pow(2, -(abs(self.x-x))))
		except OverflowError:
			ax = MAX_ACCELERATION
		except ZeroDivisionError:
			ax = MAX_ACCELERATION
		try:
			ay = REPULSIVE_POWER / (1-math.pow(2, -(abs(self.y-y))))
		except OverflowError:
			ay = MAX_ACCELERATION
		except ZeroDivisionError:
			ay = MAX_ACCELERATION
		if ax > MAX_ACCELERATION:
			ax = MAX_ACCELERATION
		if ay > MAX_ACCELERATION:
			ay = MAX_ACCELERATION
		if x - self.x > 0:
			ax *= -1
		if y - self.y > 0:
			ay *= -1
		return ax, ay

	def determine_acceleration(self, x, y):
		ax, ay = self.get_attraction(x, y)
		rx, ry = self.get_repulsion(x, y)
		mx, my = self.get_attraction(MOUSE_X, MOUSE_Y, mult=MOUSE_ATTRACTION) 
		return ax+rx+mx, ay+ry+my

	def accelerate(self):
		self.get_neighbours()
		mx = sum([cb.x for cb in self.neigbours])/4
		my = sum([cb.y for cb in self.neigbours])/4
		accel_x, accel_y = self.determine_acceleration(mx, my)
		self.v[0] += accel_x
		self.v[1] += accel_y
		try:
			speed = math.sqrt(math.pow(self.v[0], 2) + math.pow(self.v[1], 2))
		except OverflowError:
			speed = MAX_SPEED
		if speed > (MAX_SPEED):
			if self.v[0] == 0:
				t = math.pi/2
			else:
				t = math.atan(self.v[1]/self.v[0])
			self.v[0] = (MAX_SPEED/100) * math.cos(t)
			self.v[1] = (MAX_SPEED/100) * math.sin(t)
		elif speed < 1:
			self.v[0] = 100*random.random()
			self.v[1] = 100*random.random()

	def check_bounds(self):
		if self.x > SCREEN_W and self.v[0] > 0:
			self.v[0] *= 0.9
			self.x = MENU_W
		if self.x < MENU_W and self.v[0] < 0:
			self.v[0] *= 0.9
			self.x = SCREEN_W
		if self.y > SCREEN_H and self.v[1] > 0:
			self.v[1] *= 0.9
			self.y = 0
		if self.y < 0 and self.v[1] < 0:
			self.v[1] *= 0.9
			self.y = SCREEN_H

	def move(self):
		self.x += int(self.v[0]/100)
		self.y += int(self.v[1]/100)
		self.check_bounds()
		self.update_grid()
		self.accelerate()
		
		

def get_theme():
	theme = pygame_menu.Theme(
		background_color=(0,0,0,0),
		widget_font=pygame_menu.font.FONT_NEVIS,
		widget_alignment=pygame_menu.locals.ALIGN_LEFT,
		title_font_size=20,
		widget_font_size=10,
		border_color=((255, 255, 255, 255)),
		border_width=1,
		widget_border_width=0,
		widget_offset=(2, 2),
		widget_selection_effect=pygame_menu.widgets.NoneSelection()
	)
	return theme

def reset_birds():
	global BIRDS
	grid = {}
	BIRDS = [Bird(i, grid) for i in range(int(BIRD_COUNT))]


def get_menu():
	theme = get_theme()
	menu = pygame_menu.Menu('Birds', MENU_W, SCREEN_H, theme=theme, position=(0, 0))
	menu.add.range_slider('bird count', BIRD_COUNT, [20,1000], 1, rangeslider_id='bird_count', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('Acceleration', ACCELERATION, [0,ACCELERATION*100], 0.001, rangeslider_id='acceleration', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('repulsive distance', REPULSIVE_DISTANCE, [0,100], 1, rangeslider_id='repulsive_distance', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('repulsive power', REPULSIVE_POWER, [0,100], 1, rangeslider_id='repulsive_power', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('max speed', MAX_SPEED, [0,MAX_SPEED*10], 1, rangeslider_id='max_speed', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('mouse attraction', MOUSE_ATTRACTION, [0, MOUSE_ATTRACTION*100], 0.001, rangeslider_id='mouse_attraction', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.button('reset', reset_birds)
	return menu

def scale_slider_pos(slider_val):
	return int(MENU_W + slider_val * (SCREEN_W-MENU_W)/100)


def set_widget_vals(menu):
	global ACCELERATION, REPULSIVE_DISTANCE, MAX_SPEED, REPULSIVE_POWER, BIRD_COUNT, MOUSE_ATTRACTION
	ACCELERATION = menu.get_widget('acceleration').get_value()
	REPULSIVE_DISTANCE = menu.get_widget('repulsive_distance').get_value()
	REPULSIVE_POWER = menu.get_widget('repulsive_power').get_value()
	MAX_SPEED = menu.get_widget('max_speed').get_value()
	BIRD_COUNT = menu.get_widget('bird_count').get_value()
	MOUSE_ATTRACTION = menu.get_widget('mouse_attraction').get_value()

# define a main function
def main():
	global MOUSE_X, MOUSE_Y
	FramePerSec = pygame.time.Clock()
	# initialize the pygame module
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
	pygame.display.set_caption("birds")
	menu = get_menu()
	# define a variable to control the main loop
	running = True
	reset_birds()
	# main loop
	while running:
		screen.fill((0,0,0))
		MOUSE_X, MOUSE_Y = pygame.mouse.get_pos()
		for b in BIRDS:
			b.move()
			screen.blit(b.surf, (b.x, b.y))
		set_widget_vals(menu)
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