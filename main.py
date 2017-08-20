from cpu import CPU
from graphics import Graphics
import logging

logging.basicConfig(level=logging.DEBUG)

class System:
	def __init__(self):
		self.ram = bytearray(4096)
		self.gfx = Graphics()
		self.cpu = CPU(self.ram, self.gfx)

	def start(self, data):
		entry=0x200
		self.ram[entry:entry+len(data)] = data
		self.cpu.run(entry)

def main():
	sys = System()
	sys.start(bytearray(open("rom.bin", "rb").read()))

if __name__ == '__main__':
		main()

