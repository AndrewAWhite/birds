# import the pygame module, so you can use it
import pygame
import pygame_menu
import random
import math

SCREEN_W = 1800	
SCREEN_H = 980

def get_random_direction():
	return -1^(random.randint(1, 2))

def find_closest_birds(b, birds):
	return sorted(birds, key=lambda cb: math.sqrt((math.pow((cb.x-b.x), 2) + math.pow((cb.y - b.y), 2))))[:2]

class Bird(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__() 
		self.x = random.randint(300, SCREEN_W-50)
		self.y = random.randint(0, SCREEN_H-50)
		self.v = [0, 0]
		self.surf = pygame.Surface((100, 100))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(center = (100, 100))


# define a main function
def main():
	FramePerSec = pygame.time.Clock()
	# initialize the pygame module
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
	pygame.display.set_caption("birds")
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
	menu = pygame_menu.Menu('Birds', 300, SCREEN_H, theme=theme, position=(0, 0))
	menu.add.range_slider('stickiness', 10, [0,100], 1, rangeslider_id='stickiness', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	menu.add.range_slider('trickiness', 10, [0,100], 1, rangeslider_id='trickiness', border_width=0, border_position=pygame_menu.locals.POSITION_NORTH)
	# define a variable to control the main loop
	running = True
	b1 = Bird()
	b2 = Bird()
	# main loop
	while running:
		screen.fill((0,0,0))
		b1.x = menu.get_widget('stickiness').get_value() + 300
		screen.blit(b1.surf, (b1.x, b1.y))
		screen.blit(b2.surf, (b2.x, b2.y))
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