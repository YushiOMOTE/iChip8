
class Graphics:
	def __init__(self, height = 32, width = 64, scale = 1):
		self.colors = ('white', 'black')
		self.height = height
		self.width = width
		self.scale = scale
		self.extended = False

	def init_display(self):
		return

	def set(self, x, y, c):
		return

	def get(self, x, y):
		return 0

	def clear(self):
		return

	def update(self):
		return

	def down(self, lines):
		return

	def left(self):
		return

	def right(self):
		return

	def extend(self, on = True):
		self.extended = on
		return


