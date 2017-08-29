import threading
import time

class Timer(threading.Thread):
	def __init__(self, freq = 60.0, event = None):
		super(Timer, self).__init__()
		
		self.freq = freq
		self.event = event
		self.lock = threading.Lock()
		self.c = 0
		self.on = True
		
		self.start()
		
	def __del__(self):
		self.on = False
		self.join()
	
	def set(self, c):
		with self.lock:
			self.c = c
			
	def get(self):
		with self.lock:
			return self.c
	
	def run(self):
		while self.on:
			self.delay(1.0 / self.freq)
			
			with self.lock:
				if self.c == 1 and self.event != None:
					self.event()
				
				self.c = self.c - 1 if self.c > 0 else 0
				
	def delay(self, d):
		t = time.time()
		while time.time() <= t + d:
			try:
				time.sleep(d)
			except:
				continue
