import threading

class Keyboard():
	def __init__(self, kbd_delay=0, **kwargs):
		self.on = True
		
		self.kbd_delay = kbd_delay
		
		self.row = 4
		self.col = 4
		self.size = self.row * self.col
		
		self.map = [
			0x1, 0x2, 0x3, 0xc,
			0x4, 0x5, 0x6, 0xd,
			0x7, 0x8, 0x9, 0xe,
			0xa, 0x0, 0xb, 0xf,
		]
		
		self.cv = threading.Condition()
		
		# system keys
		self.syskeys = {
			'shutdown': False,
		}
		
		self.release()
		
	def press(self, i):
		if type(i) is str:
			self.press_sys(i)
			return
			
		with self.cv:
			self.key = i
			self.cv.notify()
			
	def press_sys(self, i):
		# release cou in case it is waiting for key
		if i == 'shutdown':
			with self.cv:
				self.on = False
				self.cv.notify()
		
		self.syskeys[i] = True
		
	def pressed(self, i):
		if type(i) is str:
			return self.syskeys[i]
		
		with self.cv:
			return self.key == i
		
	def release(self, i = None):
		if type(i) is str:
			self.syskeys[i] = False
			return
			
		with self.cv:
			self.key = None
			
	def label(self, key):
		return self.map[key]
	
	def wait(self):
		with self.cv:
			while self.on and self.key == None:
				self.cv.wait(0.2)
			return self.map[self.key] if self.on else 0
			
	def peek(self, i):
		# emulate key fetch delay
		for _ in range(self.kbd_delay):
			continue
		return self.pressed(self.map.index(i))
