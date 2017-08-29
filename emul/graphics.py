import ui
from scene import *

class Graphics(Scene):
	def __init__(self, kbd, height=32, width=64, gfx_show_fps=False, gfx_frame_intvl=1, gfx_keysz=48, **kwargs):
		super(Graphics, self).__init__()
		
		self.height = height
		self.width = width
		
		self.show_fps = gfx_show_fps
		self.frame_intvl = gfx_frame_intvl
		self.keysz = gfx_keysz
		
		self.extended = False
		
		self.kbd = kbd
		self.kpos = [(0, 0) for _ in range(kbd.size)]
		
		self.clear()
	
	def setup(self):
		self.background_color = 'black'
		
	def show(self):
		run(self, orientation=PORTRAIT, show_fps=self.show_fps, frame_interval=self.frame_intvl, multi_touch = False)
		
	def draw(self):
		sw, sh = ui.get_screen_size()
		scale = sw / self.width
		
		# draw title
		text('Chip-8 Emulator', x = 10, y = 20, alignment = 9)
		
		# update key positions
		self.keysz = self.keysz
		shh = sh - self.height * scale
		for x in range(self.kbd.col):
			for y in range(self.kbd.row):
				px = int(sw / 2) + (x - 2) * self.keysz
				py = int(shh / 2) - (y - 2) * self.keysz
				self.kpos[x + y * self.kbd.col] = (px, py)
		
		# draw keys
		for i in range(self.kbd.size):
			fill('#beb8b6' if self.kbd.pressed(i) else 'white')
			rect(int(self.kpos[i][0]), int(self.kpos[i][1]), self.keysz - 4, self.keysz - 4)
			
			off = self.keysz / 2
			tint(0, 0, 0)
			text(
				'%x'%self.kbd.label(i), x=int(self.kpos[i][0] + off), y=int(self.kpos[i][1] + off),
				font_name='Courier',
			)
		
		# draw screen
		fill('white')
		for x in range(self.width):
			for y in range(self.height):
				if self.map[x + y * self.width]:
					rect(int(x * scale), int(sh - (y + 1) * scale), scale, scale)
			
	def touch_began(self, touch):
		x, y = touch.location
		
		for i in range(self.kbd.size):
			px = self.kpos[i][0]
			py = self.kpos[i][1]
			if px < x < px + self.keysz and py < y < py + self.keysz:
				self.kbd.press(i)
	
	def touch_ended(self, touch):
		self.kbd.release()
		
	def stop(self):
		self.kbd.press('shutdown')

	def set(self, x, y, c):
		self.map[int(x + self.width * y)] = c

	def get(self, x, y):
		return self.map[int(x + self.width * y)]

	def clear(self):
		self.map = [False for _ in range(self.width * self.height)]

	def down(self, lines):
		# TODO
		return

	def left(self):
		# TODO
		return

	def right(self):
		# TODO
		return

	def extend(self, on = True):
		self.extended = on
		# TODO
