import pygame
import pygame_menu
import random
import math

MENU_W = 300
SCREEN_W = 1800	
SCREEN_H = 980
WINDOW_W = SCREEN_W - MENU_W

BIRD_COUNT=400
NEIGHBOUR_COUNT = 12

MAX_ACCELERATION = 50
HAWK_ACCELERATION = 90
ATTRACTIVE_POWER = 0.067
RANDOM_ELEMENT = 5
REPULSIVE_POWER = 1.333
MAX_SPEED = 1500
HAWK_MAX_SPEED = 2000
MOUSE_ATTRACTION = 0.002

RANDOM_MOUSE = 1


MOUSE_X, MOUSE_Y, MOUSE_Z = random.randint(MENU_W, SCREEN_W), random.randint(0, SCREEN_H), random.randint(0, SCREEN_H)

def get_random_direction():
	return -1^(random.randint(1, 2))

class Bird(pygame.sprite.Sprite):
	def __init__(self, i, grid):
		super().__init__()
		self.i = i
		self.grid = grid
		self.is_hawk = False
		self.x = random.randint(MENU_W, WINDOW_W-10)
		self.y = random.randint(1, SCREEN_H-10)
		self.z = random.randint(0, SCREEN_H-10)
		self.v = [0, 0, 0]
		self.max_speed = MAX_SPEED
		self.max_acceleration = MAX_ACCELERATION
		if self.i != -1:
			self.grid_key = self.get_grid_key()
			self.update_grid()
			self.rect = self.surf.get_rect(center = (3, 3))
			self.neighbours = None
			self.get_neighbours()

	@property
	def surf(self):
		size = int(self.z * (10/SCREEN_H))
		surf = pygame.Surface((size, size))
		col = int(self.z * (255/SCREEN_H))
		surf.fill((col,col,col))
		return surf

	def get_grid_key(self):
		if self.is_hawk:
			return (-1,-1,-1)
		else:
			x = math.floor(self.x / WINDOW_W)*10
			y = math.floor(self.y/SCREEN_H)*10
			z = math.floor(self.z/SCREEN_H)*10
			return (x,y,z)

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

	def get_distance(self, x, y, z):
		dx = x - self.x
		dy = y - self.y
		dz = z - self.z
		d = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))
		return d

	def get_neighbours(self):
		neighbours =  self.grid.get(self.grid_key, set())
		if len(neighbours) == 0:
			pass
		self.neighbours = [cb for cb in neighbours if cb.i != self.i][:int(NEIGHBOUR_COUNT)]
			
	def get_attraction(self, x, y, z, mult=ATTRACTIVE_POWER):
		ax =  mult * math.pow((x - self.x)/5, 2)
		ay = mult * math.pow((y - self.y)/5, 2)
		az = mult * math.pow((z - self.z)/5, 2)
		if ax > self.max_acceleration:
			ax = self.max_acceleration
		if ay > self.max_acceleration:
			ay = self.max_acceleration
		if az > self.max_acceleration:
			az = self.max_acceleration
		if x - self.x < 0:
			ax *= -1
		if y - self.y < 0:
			ay *= -1
		if z - self.z < 0:
			az *= -1
		return ax, ay, az

	def get_repulsion(self, x, y, z, mult=1):
		try:
			ax = REPULSIVE_POWER / (1-math.pow(2, -(abs(self.x-x))))
		except OverflowError:
			ax = self.max_acceleration
		except ZeroDivisionError:
			ax = self.max_acceleration
		try:
			ay = REPULSIVE_POWER / (1-math.pow(2, -(abs(self.y-y))))
		except OverflowError:
			ay = self.max_acceleration
		except ZeroDivisionError:
			ay = self.max_acceleration
		try:
			az = REPULSIVE_POWER / (1-math.pow(2, -(abs(self.z-z))))
		except OverflowError:
			az = self.max_acceleration
		except ZeroDivisionError:
			az = self.max_acceleration
		if ax > self.max_acceleration:
			ax = self.max_acceleration
		if ay > self.max_acceleration:
			ay = self.max_acceleration
		if az > self.max_acceleration:
			az = self.max_acceleration
		if x - self.x > 0:
			ax *= -1
		if y - self.y > 0:
			ay *= -1
		if z - self.z > 0:
			az *= -1
		return mult*ax, mult*ay, mult*az

	def get_hawk_avoidance(self):
		hawk = next(iter(self.grid[(-1,-1,-1)]))
		return self.get_repulsion(hawk.x, hawk.y, hawk.z, mult=20)

	def determine_virtual_distance(self, size, self_d, d, min_size=0):
		if (d-min_size) < (size/4) and self_d > 3*size/4:
			d = min_size + size + d
		elif d > 3*(min_size + size)/4 and (self_d-min_size) < size/4:
			d = min_size - d
		return d
		
	def determine_acceleration(self, x, y, z):
		x = self.determine_virtual_distance(WINDOW_W, self.x, x, MENU_W)
		y = self.determine_virtual_distance(SCREEN_H, self.y, y)
		z = self.determine_virtual_distance(SCREEN_H, self.z, z)
		ax, ay, az = self.get_attraction(x, y, z)
		rx, ry, rz = self.get_repulsion(x, y, z)
		mx, my, mz = self.get_attraction(MOUSE_X, MOUSE_Y, MOUSE_Z, mult=MOUSE_ATTRACTION)
		hx, hy, hz = self.get_hawk_avoidance()
		return ax+rx+mx+hx, ay+ry+my+hy, az+rz+mz+hz

	def accelerate(self):
		self.get_neighbours()
		if len(self.neighbours) == 0:
			mx = self.x + random.randint(-100, 100)
			my = self.y + random.randint(-100, 100)
			mz = self.z + random.randint(-100, 100)
		else:
			mx = sum([cb.x for cb in self.neighbours])/len(self.neighbours)
			my = sum([cb.y for cb in self.neighbours])/len(self.neighbours)
			mz = sum([cb.z for cb in self.neighbours])/len(self.neighbours)
		if not self.is_hawk:
			mx += get_random_direction()*random.randint(0, int(RANDOM_ELEMENT))
			my += get_random_direction()*random.randint(0, int(RANDOM_ELEMENT))
			mz += get_random_direction()*random.randint(0, int(RANDOM_ELEMENT))
		accel_x, accel_y, accel_z = self.determine_acceleration(mx, my, mz)
		self.v[0] += accel_x
		self.v[1] += accel_y
		self.v[2] += accel_z
		try:
			speed = math.sqrt(math.pow(self.v[0], 2) + math.pow(self.v[1], 2) + math.pow(self.v[2], 2))
		except OverflowError:
			speed = self.max_speed
		if speed > (self.max_speed):
			if self.v[0] == 0:
				t = math.pi/2
			else:
				t = math.atan(self.v[1]/self.v[0])
			if self.v[1] == 0:
				t2 = math.pi/2
			else:
				t2 = math.atan(self.v[2]/self.v[1])
			self.v[0] = (self.max_speed/100) * math.cos(t)
			self.v[1] = (self.max_speed/100) * math.sin(t)
			self.v[2] = (self.max_speed/100) * math.sin(t2)
		elif speed < 1:
			self.v[0] = 100*random.random()
			self.v[1] = 100*random.random()
			self.v[2] = 100*random.random()

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
		if self.z < 0 and self.v[2] < 0:
			self.v[2] *= 0.9
			self.z = SCREEN_H
		if self.z > SCREEN_H and self.v[2] > 0:
			self.v[2] *= 0.9
			self.z = 0

	def move(self):
		self.x += int(self.v[0]/100)
		self.y += int(self.v[1]/100)
		self.z += int(self.v[2]/100)
		self.check_bounds()
		self.update_grid()
		self.accelerate()
		

class Hawk(Bird):
	def __init__(self, i, grid):
		super(self.__class__, self).__init__(i, grid)
		self.is_hawk = True
		self.grid_key = self.get_grid_key()
		self.update_grid()
		self.rect = self.surf.get_rect(center = (3, 3))
		self.neighbours = None
		self.get_neighbours()
		self.max_acceleration = HAWK_ACCELERATION
		self.max_speed = HAWK_MAX_SPEED

	@property
	def surf(self):
		size = int(self.z * (20/SCREEN_H))
		if hasattr(self, 'neighbours') and len(self.neighbours) > 0:
			tgt = self.target
			d = self.get_distance(tgt.x, tgt.y, tgt.z)
			if d < 50:
				surf = pygame.Surface((size*2, size*2))
				surf.fill((0, 150, 255))
				return surf
		surf = pygame.Surface((size, size))
		surf.fill((138, 51, 36))
		return surf

	@property
	def target(self):
		if len(self.neighbours) > 0:
			return next(iter(self.neighbours))

	def get_neighbours(self):
		if not self.neighbours:
			flock = [v for k, v in self.grid.items() if k!=(-1,-1,-1) and len(v) > 0]
			if len(flock) == 0:
				self.neighbours = []
			else:
				birds = [random.choice(flock)]
				self.neighbours = [b for b in birds][0]
	
	def determine_acceleration(self, x, y, z):
		tgt = self.target
		x = self.determine_virtual_distance(WINDOW_W, self.x, tgt.x, MENU_W)
		y = self.determine_virtual_distance(SCREEN_H, self.y, tgt.y)
		z = self.determine_virtual_distance(SCREEN_H, self.z, tgt.z)
		return self.get_attraction(x, y, z)

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
	BIRDS = [Hawk(-1, grid)]
	BIRDS.extend(Bird(i, grid) for i in range(int(BIRD_COUNT)))


def generate_slider_range(slider):
	i = slider['range_values'][0]
	vals = [i]
	while i < slider['range_values'][1]:
		i += slider['increment']
		vals.append(i)
	return vals

def randomise_sliders(menu, sliders):
	for slider in sliders:
		vals = generate_slider_range(slider)
		new_val = random.choice(vals)
		menu.get_widget(slider['rangeslider_id'])._value[0] = new_val
	

def get_menu():
	theme = get_theme()
	menu = pygame_menu.Menu('Birds', MENU_W, SCREEN_H, theme=theme, position=(0, 0))
	sliders = [
		{'title': 'bird count', 'default_value': BIRD_COUNT, 'range_values': [20,1000], 'increment': 1, 'rangeslider_id': 'bird_count'},
		{'title': 'neighbour count', 'default_value': NEIGHBOUR_COUNT, 'range_values': [0,100], 'increment': 1, 'rangeslider_id': 'neighbour_count'},
		{'title': 'random element', 'default_value': RANDOM_ELEMENT, 'range_values': [0,100],'increment': 1, 'rangeslider_id': 'random_element'},
		{'title': 'attractive power', 'default_value': ATTRACTIVE_POWER, 'range_values': [0, 0.1],'increment': 0.01, 'rangeslider_id': 'attractive_power'},
		{'title': 'repulsive power', 'default_value': REPULSIVE_POWER, 'range_values': [0,100],'increment': 1, 'rangeslider_id': 'repulsive_power'},
		{'title': 'max speed', 'default_value': MAX_SPEED, 'range_values': [0,10000],'increment': 1, 'rangeslider_id': 'max_speed'},
		{'title': 'mouse attraction', 'default_value': MOUSE_ATTRACTION, 'range_values': [0, 0.01],'increment': 0.001, 'rangeslider_id': 'mouse_attraction'},
		{'title': 'max acceleration', 'default_value': MAX_ACCELERATION, 'range_values': [0, 1000],'increment': 1, 'rangeslider_id': 'max_acceleration'},
	]
	for slider in sliders:
		menu.add.range_slider(
			slider['title'],
			slider['default_value'],
			slider['range_values'], 
			slider['increment'], 
			rangeslider_id=slider['rangeslider_id'],
			border_width=0,
			border_position=pygame_menu.locals.POSITION_NORTH
		)
	menu.add.button('reset', reset_birds)
	menu.add.button('randomise', randomise_sliders, menu, sliders)
	menu.add.toggle_switch('random mouse', default=RANDOM_MOUSE, toggleswitch_id='random_mouse')
	return menu

def scale_slider_pos(slider_val):
	return int(MENU_W + slider_val * (SCREEN_W-MENU_W)/100)


def set_widget_vals(menu):
	global ATTRACTIVE_POWER, RANDOM_ELEMENT, MAX_SPEED, REPULSIVE_POWER, \
		BIRD_COUNT, MOUSE_ATTRACTION, NEIGHBOUR_COUNT, MAX_ACCELERATION, RANDOM_MOUSE
	ATTRACTIVE_POWER = menu.get_widget('attractive_power').get_value()
	RANDOM_ELEMENT = menu.get_widget('random_element').get_value()
	REPULSIVE_POWER = menu.get_widget('repulsive_power').get_value()
	MAX_SPEED = menu.get_widget('max_speed').get_value()
	MAX_ACCELERATION = menu.get_widget('max_acceleration').get_value()
	BIRD_COUNT = menu.get_widget('bird_count').get_value()
	MOUSE_ATTRACTION = menu.get_widget('mouse_attraction').get_value()
	NEIGHBOUR_COUNT = menu.get_widget('neighbour_count').get_value()
	RANDOM_MOUSE = menu.get_widget('random_mouse').get_value()

def get_mouse():
	global MOUSE_X, MOUSE_Y, MOUSE_Z
	if RANDOM_MOUSE:
		if int(pygame.time.get_ticks()/1000) % 6 == 0:
			MOUSE_X, MOUSE_Y = random.randint(MENU_W, SCREEN_W), random.randint(0, SCREEN_H)
	else:
		MOUSE_X, MOUSE_Y = pygame.mouse.get_pos()
	MOUSE_Z = random.randint(0, SCREEN_H)

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
	mouse_surf = pygame.Surface((10, 10))
	mouse_surf.fill((120, 0, 120))
	while running:
		get_mouse()
		screen.fill((0,0,0))
		for b in BIRDS:
			b.move()
			screen.blit(b.surf, (b.x, b.y))
		# hawk = BIRDS[0]
		# target = hawk.target
		# if target:
		# 	pygame.draw.line(screen, (0, 255, 0), (hawk.x, hawk.y), (target.x, target.y))
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
	
if __name__=="__main__":
	main()
