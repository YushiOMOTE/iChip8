import unittest
import logging

from emul.cpu import *
from emul.keyboard import *
from emul.graphics import *
from emul.timer import *
from emul.audio import *
from emul.ram import *

class CpuTest(unittest.TestCase):
	def setUp(self):
		super(unittest.TestCase, self).__init__()
		
		# logging.basicConfig(level=logging.DEBUG, format='%(message)s')
		
		self.kbd = Keyboard()
		
		self.audio = Audio()
		self.gfx = Graphics(self.kbd)
		
		self.ram = Ram()
		self.cpu = CPU(ram=self.ram, kbd=self.kbd, gfx=self.gfx, audio=self.audio)
		
	def test_dec(self):
		self.assertEqual(dec1(0x1234), 0x4)
		self.assertEqual(dec2(0x1234), 0x3)
		self.assertEqual(dec3(0x1234), 0x2)
		self.assertEqual(dec4(0x1234), 0x1)
		self.assertEqual(decl(0x1234), 0x34)
		self.assertEqual(deca(0x1234), 0x234)
	
	def test_op_call(self):
		self.cpu.pc = 0x2a0
		self.cpu.sp = 0
		self.cpu.exe(0x2230)
		self.assertEqual(self.cpu.pc, 0x230)
		self.assertEqual(self.cpu.stack[0], 0x2a0)
		self.assertEqual(self.cpu.sp, 1)
	
	def test_rop_ret(self):
		self.test_op_call()
		self.cpu.exe(0x00ee)
		self.assertEqual(self.cpu.pc, 0x2a0)
		self.assertEqual(self.cpu.sp, 0)
		
	def test_op_add(self):
		# 3 + 0xff = 1
		self.cpu.V[1] = 3
		self.cpu.exe(0x71ff)
		self.assertEqual(self.cpu.V[1], 0x02)
	
	def test_lop_xor(self):
		# 0xab ^ 0xfb = 0x50
		self.cpu.V[1] = 0xab
		self.cpu.V[5] = 0xfb
		self.cpu.exe(0x8153)
		self.assertEqual(self.cpu.V[1], 0x50)
		self.assertEqual(self.cpu.V[5], 0xfb)
	
	def test_lop_add(self):
		# 3 + 0xff = 2 (cf = 1)
		self.cpu.V[1] = 3
		self.cpu.V[5] = 255
		self.cpu.exe(0x8154)
		self.assertEqual(self.cpu.V[1], 2)
		self.assertEqual(self.cpu.V[5], 255)
		self.assertEqual(self.cpu.V[0xf], 1)
		
		# 56 + 23 = 79 (cf = 0)
		self.cpu.V[10] = 56
		self.cpu.V[12] = 23
		self.cpu.exe(0x8ac4)
		self.assertEqual(self.cpu.V[10], 79)
		self.assertEqual(self.cpu.V[12], 23)
		self.assertEqual(self.cpu.V[0xf], 0)
		
	def test_lop_sub(self):
		# 3 - 255 = (256 + 3) - 255 = 4
		self.cpu.V[1] = 3
		self.cpu.V[5] = 255
		self.cpu.exe(0x8155)
		self.assertEqual(self.cpu.V[1], 4)
		self.assertEqual(self.cpu.V[5], 255)
		self.assertEqual(self.cpu.V[0xf], 0)
		
		# 255 - 120 = 135
		self.cpu.V[8] = 255
		self.cpu.V[5] = 120
		self.cpu.exe(0x8855)
		self.assertEqual(self.cpu.V[8], 135)
		self.assertEqual(self.cpu.V[5], 120)
		self.assertEqual(self.cpu.V[0xf], 1)
	
	def test_lop_subn(self):
		# 255 - 3 = 252
		self.cpu.V[5] = 3
		self.cpu.V[1] = 255
		self.cpu.exe(0x8517)
		self.assertEqual(self.cpu.V[5], 252)
		self.assertEqual(self.cpu.V[1], 255)
		self.assertEqual(self.cpu.V[0xf], 1)
		
		# 120 - 255 = (256 + 120) - 255 = 121
		self.cpu.V[5] = 255
		self.cpu.V[8] = 120
		self.cpu.exe(0x8587)
		self.assertEqual(self.cpu.V[5], 121)
		self.assertEqual(self.cpu.V[8], 120)
		self.assertEqual(self.cpu.V[0xf], 0)
	
	def test_lop_shr(self):
		# 3 >> 1 = 1
		self.cpu.V[2] = 3
		self.cpu.exe(0x8206)
		self.assertEqual(self.cpu.V[2], 1)
		self.assertEqual(self.cpu.V[0xf], 1)
		
		# 128 >> 1 = 64
		self.cpu.V[2] = 128
		self.cpu.exe(0x8206)
		self.assertEqual(self.cpu.V[2], 64)
		self.assertEqual(self.cpu.V[0xf], 0)
		
	def test_lop_shl(self):
		# 255 << 1 = 1
		self.cpu.V[8] = 255
		self.cpu.exe(0x880e)
		self.assertEqual(self.cpu.V[8], 254)
		self.assertEqual(self.cpu.V[0xf], 1)
	
		# 8 << 1 = 16
		self.cpu.V[8] = 8
		self.cpu.exe(0x880e)
		self.assertEqual(self.cpu.V[8], 16)
		self.assertEqual(self.cpu.V[0xf], 0)
		
	def test_mop_store(self):
		for i in range(16):
			self.cpu.V[i] = i
			self.cpu.ram[0x420 + i] = 39
		self.cpu.I = 0x420
		self.cpu.exe(0xf955)
		self.assertEqual(self.cpu.I, 0x420)
		for i in range(16):
			if i <= 9:
				self.assertEqual(self.cpu.ram[0x420 + i], i)
			else:
				self.assertEqual(self.cpu.ram[0x420 + i], 39)
	
	def test_mop_load(self):
		for i in range(16):
			self.cpu.V[i] = 39
			self.cpu.ram[0x500 + i] = i * 3
		self.cpu.I = 0x500
		self.cpu.exe(0xfb65)
		self.assertEqual(self.cpu.I, 0x500)
		for i in range(16):
			if i <= 0xb:
				self.assertEqual(self.cpu.V[i], i * 3)
			else:
				self.assertEqual(self.cpu.V[i], 39)
		
	def test_mop_store_bcd(self):
		self.cpu.V[6] = 935
		self.cpu.I = 0x780
		self.cpu.exe(0xf633)
		self.assertEqual(self.cpu.ram[0x780], 9)
		self.assertEqual(self.cpu.ram[0x781], 3)
		self.assertEqual(self.cpu.ram[0x782], 5)
	
	def test_op_load_index(self):
		self.cpu.I = 0xfff
		self.cpu.exe(0xabbb)
		self.assertEqual(self.cpu.I, 0xbbb)

	def test_op_jump_index(self):
		self.cpu.pc = 77
		self.cpu.V[0] = 29
		self.cpu.exe(0xb122)
		self.assertEqual(self.cpu.pc, 0x122 + 29)
	
if __name__ == '__main__':
	unittest.main()
