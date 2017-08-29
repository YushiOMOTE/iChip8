from emul.cpu import CPU
from emul.audio import Audio
from emul.graphics import Graphics
from emul.keyboard import Keyboard
from emul.ram import Ram

class System:
	def __init__(self, **kwargs):
		self.entry = kwargs['cpu_entry']
		self.ld_addr = kwargs['cpu_ld_addr']
		
		self.kbd = Keyboard(**kwargs)
		
		self.audio = Audio()
		self.gfx = Graphics(self.kbd, **kwargs)
		
		self.ram = Ram(kwargs['ram_sz'])
		
		self.cpu = CPU(
			ram=self.ram, 
			kbd=self.kbd, 
			gfx=self.gfx, 
			audio=self.audio, 
			**kwargs)
	
	def __enter__(self):
		return self
	
	def __exit__(self, val, type, tb):
		pass
		
	def start(self, rom):
		self.audio.boot()
		
		self.gfx.show()
		
		ep = self.entry
		lp = self.ld_addr
		
		self.ram[lp:lp+len(rom)] = rom
		self.cpu.run(ep)
		
		self.audio.shutdown()
