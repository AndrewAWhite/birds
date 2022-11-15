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
BIRD_COUNT=500


ACCELERATION = 1
REPULSIVE_DISTANCE = 2
REPULSIVE_POWER = 2
MAX_SPEED = 10000
MAX_DISTANCE = 200

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
		x = math.floor(self.x / WINDOW_W)*10
		y = math.floor(self.y/SCREEN_W)*10
		return (x,y)

	def update_grid(self):
		cur_spot = self.grid.get(self.grid_key, set())
		if self in cur_spot:
			cur_spot.remove(self)
		self.grid[self.grid_key] = cur_spot
		neighbours = self.grid.get(self.get_grid_key(), set())
		neighbours.add(self)
		self.grid[self.get_grid_key()] = neighbours
		self.grid_key = self.get_grid_key()

	def get_distance(self, x, y):
		dx = x - self.x
		dy = y - self.y
		d = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
		return d

	def get_neighbours(self):
		if self.neigbours is None:
			neighbours =  self.grid.get(self.grid_key, set())
			if len(neighbours) == 0:
				pass
			self.neigbours = [cb for cb in neighbours if cb.i != self.i and self.get_distance(cb.x, cb.y) < MAX_DISTANCE][:10]
		for cb in self.neigbours:
			if self.get_distance(cb.x, cb.y) < MAX_DISTANCE:
				continue
			self.neigbours.remove(cb)
			neighbours =  self.grid.get(self.grid_key, set())
			candidates = sorted(self.neigbours, key=lambda cb: self.get_distance(cb.x, cb.y))
			if candidates:
				self.neigbours.append(candidates[0])
			
	def get_attraction(self, x, y):
		ax =  ACCELERATION * math.pow(x - self.x, 2)
		ay = ACCELERATION * math.pow(y - self.y, 2)
		if x - self.x < 0:
			ax *= -1
		if y - self.y < 0:
			ay *= -1
		return ax, ay

	def get_repulsion(self, x, y):
		try:
			ax = ACCELERATION / (1-math.pow(2, -abs(self.x-x)))
		except:
			ax = 100
		try:
			ay = ACCELERATION / (1-math.pow(2, -abs(self.y-y)))
		except:
			ay = 100
		if x - self.x < 0:
			ax *= -1
		if y - self.y < 0:
			ay *= -1
		return ax, ay

	def determine_acceleration(self, x, y):
		ax, ay = self.get_attraction(x, y)
		return ax, ay

	def accelerate(self):
		self.get_neighbours()
		for cb in self.neigbours:
			accel_x, accel_y = self.determine_acceleration(cb.x, cb.y)
			self.v[0] += accel_x
			self.v[1] += accel_y 
		speed = math.sqrt(math.pow(self.v[0], 2) + math.pow(self.v[1], 2))
		mx, my = pygame.mouse.get_pos()
		amx, amy = self.get_repulsion(mx, my)
		self.v[0] -= 10*amx
		self.v[1] -= 10*amy
		if speed > (MAX_SPEED/100):
			if self.v[0] == 0:
				t = math.pi/2
			else:
				t = math.atan(self.v[1]/self.v[0])
			self.v[0] = (MAX_SPEED/1000) * math.cos(t)
			self.v[1] = (MAX_SPEED/1000) * math.sin(t)
		elif speed < 1:
			self.v[0] = 100*random.random()
			self.v[1] = 100*random.random()

	def move(self):
		self.x += int(self.v[0])
		self.y += int(self.v[1])
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

def randomise_sliders(menu, sliders):
	for slider in sliders:
		new_val = random.randint(*slider['range_values'])
		menu.get_widget(slider['rangeslider_id'])._value[0] = new_val
	

def get_menu():
	global menu
	theme = get_theme()
	menu = pygame_menu.Menu('Birds', MENU_W, SCREEN_H, theme=theme, position=(0, 0))
	sliders = [
		{'title': 'bird count', 'default_value': 500, 'range_values': [20,1000], 'rangeslider_id': 'bird_count'},
		{'title': 'Acceleration', 'default_value': 5, 'range_values': [0,100], 'rangeslider_id': 'acceleration'},
		{'title': 'repulsive distance', 'default_value': 10, 'range_values': [0,100], 'rangeslider_id': 'repulsive_distance'},
		{'title': 'repulsive power', 'default_value': 10, 'range_values': [0,100], 'rangeslider_id': 'repulsive_power'},
		{'title': 'max speed', 'default_value': 10000, 'range_values': [0,10000], 'rangeslider_id': 'max_speed'},
		{'title': 'max distance', 'default_value': 250, 'range_values': [50, 300], 'rangeslider_id': 'max_distance'},
	]
	for slider in sliders:
		menu.add.range_slider(
			slider['title'],
			slider['default_value'],
			slider['range_values'], 
			1, 
			rangeslider_id=slider['rangeslider_id'],
			border_width=0,
			border_position=pygame_menu.locals.POSITION_NORTH
		)
	menu.add.button('reset', reset_birds)
	menu.add.button('randomise', randomise_sliders, menu, sliders)
	return menu

def scale_slider_pos(slider_val):
	return int(MENU_W + slider_val * (SCREEN_W-MENU_W)/100)


def set_widget_vals(menu):
	global ACCELERATION, REPULSIVE_DISTANCE, MAX_SPEED, REPULSIVE_POWER, BIRD_COUNT, MAX_DISTANCE
	ACCELERATION = menu.get_widget('acceleration').get_value()
	REPULSIVE_DISTANCE = menu.get_widget('repulsive_distance').get_value()
	REPULSIVE_POWER = menu.get_widget('repulsive_power').get_value()
	MAX_SPEED = menu.get_widget('max_speed').get_value()
	BIRD_COUNT = menu.get_widget('bird_count').get_value()
	MAX_DISTANCE = menu.get_widget('max_distance').get_value()

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
	reset_birds()
	# main loop
	while running:
		screen.fill((0,0,0))
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