import urllib.request
from struct import *
import random
import logging

fontset=bytearray([
	0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
	0x20, 0x60, 0x20, 0x20, 0x70, # 1
	0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
	0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
	0x90, 0x90, 0xF0, 0x10, 0x10, # 4
	0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
	0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
	0xF0, 0x10, 0x20, 0x40, 0x40, # 7
	0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
	0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
	0xF0, 0x90, 0xF0, 0x90, 0x90, # A
	0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
	0xF0, 0x80, 0x80, 0x80, 0xF0, # C
	0xE0, 0x90, 0x90, 0x90, 0xE0, # D
	0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
	0xF0, 0x80, 0xF0, 0x80, 0x80  # F
])

def dec4(opcode):
	return (opcode & 0xf000) >> 12
def dec3(opcode):
	return (opcode & 0x0f00) >> 8
def dec2(opcode):
	return (opcode & 0x00f0) >> 4
def dec1(opcode):
	return (opcode & 0x000f) >> 0
def decl(opcode):
	return (opcode & 0x00ff)
def deca(opcode):
	return (opcode & 0x0fff)

class CPU:
	def __init__(self, ram, gfx):
		# initialize timers
		self.delay_timer = 0
		self.sound_timer = 0

		# initialize registers
		self.pc = 0
		self.sp = 0
		self.I = 0
		self.V = [0] * 16

		# initialize memory structures
		self.ram = ram
		self.ram[0:0+len(fontset)] = fontset
		self.stack = [0] * 16
		self.rpl = [0] * 16

		# external resources
		self.gfx = gfx
		self.keys = [0] * 16

		self.drawf = True

		self.op = {
			0x0: self.op_exe_cret,
			0x1: self.op_jump,
			0x2: self.op_call,
			0x3: self.op_skip_eq_val,
			0x4: self.op_skip_neq_val,
			0x5: self.op_skip_eq_reg,
			0x6: self.op_move,
			0x7: self.op_add,
			0x8: self.op_exe_logic,
			0x9: self.op_skip_neq_reg,
			0xa: self.op_load_index,
			0xb: self.op_jump_index,
			0xc: self.op_rand,
			0xd: self.op_sprite,
			0xe: self.op_exe_keyboard,
			0xf: self.op_exe_misc,
		}

		self.rop = {
			0xc0: self.rop_down,
			0xc1: self.rop_down,
			0xc2: self.rop_down,
			0xc3: self.rop_down,
			0xc4: self.rop_down,
			0xc5: self.rop_down,
			0xc6: self.rop_down,
			0xc7: self.rop_down,
			0xc8: self.rop_down,
			0xc9: self.rop_down,
			0xca: self.rop_down,
			0xcb: self.rop_down,
			0xcc: self.rop_down,
			0xcd: self.rop_down,
			0xce: self.rop_down,
			0xcf: self.rop_down,
			0xe0: self.rop_clear,
			0xee: self.rop_ret,
			0xfb: self.rop_right,
			0xfc: self.rop_left,
			0xfd: self.rop_pass,
			0xfe: self.rop_ext,
			0xff: self.rop_norm,
		}

		self.lop = {
			0x0: self.lop_move,
			0x1: self.lop_or,
			0x2: self.lop_and,
			0x3: self.lop_xor,
			0x4: self.lop_add,
			0x5: self.lop_sub,
			0x6: self.lop_rsh,
			0x7: self.lop_subn,
			0xe: self.lop_shl,
		}
		
		self.mop = {
			0x07: self.mop_load_delay,
			0x0a: self.mop_keyd,
			0x15: self.mop_store_delay,
			0x18: self.mop_store_sound,
			0x1e: self.mop_add_index,
			0x29: self.mop_load_sp_index,
			0x30: self.mop_load_exsp_index,
			0x33: self.mop_store_bcd,
			0x55: self.mop_store,
			0x65: self.mop_load,
			0x75: self.mop_srpl,
			0x85: self.mop_lrpl,
		}
		
	def __str__(self):
		val = 'PC  [%04x] OP  [%04x] I   [%04x]\n'%(self.pc - 2, self.code, self.I)
		for i in range(0x10):
			val += 'V%02d [%04x] '%(i, self.V[i])
			val += '\n' if i == 7 else ''
		return val

	def run(self, pc):
		self.pc = pc
		while True:
			self.code = self.fetch()
			self.step()
			self.exe(self.code)
			print(self)

	def fetch(self):
		return unpack('>H', self.ram[self.pc:self.pc+2])[0]
		
	def step(self):
		self.pc += 2

	def exe(self, code):
		self.op[dec4(code)](code)

	def op_exe_cret(self, code):
		self.rop[decl(code)](code)

	def op_exe_logic(self, code):
		self.lop[dec1(code)](code)
	
	def op_exe_keyboard(self, code):
		# TODO
		return
	
	def op_exe_misc(self, code):
		self.mop[decl(code)](code)

	def rop_down(self, code):
		self.gfx.down(dec1(code))

	def rop_clear(self, code):
		self.gfx.clear()

	def rop_ret():
		self.sp -= 1
		self.pc = self.ram[self.sp] << 8
		self.sp -= 1
		self.pc += self.ram[self.sp]

	def rop_right():
		self.gfx.right()

	def rop_left():
		self.gfx.left()

	def rop_pass():
		pass

	def rop_ext():
		self.extend(True)

	def rop_norm():
		self.extend(False)

	def op_jump(self, code):
		self.log('JP %04x'%deca(code))
		self.pc = deca(code)

	def op_call(self, code):
		self.log('CALL %04x'%deca(code))
		self.ram[self.sp] = self.pc & 0xff
		self.sp += 1
		self.ram[self.sp] = (self.pc & 0xff00) >> 8
		self.sp += 1
		self.pc = deca(code)

	def op_skip_eq_val(self, code):
		self.log('SE V%d, %04x'%(dec3(code), decl(code)))
		if self.V[dec3(code)] == decl(code):
			self.step()

	def op_skip_neq_val(self, code):
		if self.V[dec3(code)] != decl(code):
			self.step()
			
	def op_skip_eq_reg(self, code):
		if self.V[dec3(code)] == self.V[dec2(code)]:
			self.step()

	def op_skip_neq_reg(self, code):
		if self.V[dec3(code)] != self.V[dec2(code)]:
			self.step()

	def op_move(self, code):
		self.log('LD V%d, %04x'%(dec3(code), decl(code)))
		self.V[dec3(code)] = decl(code)

	def op_add(self, code):
		self.log('ADD V%d, %04x'%(dec3(code), decl(code)))
		sum = self.V[dec3(code)] + decl(code)
		self.V[dec3(code)] = sum & 0xff

	def op_load_index(self, code):
		self.log('LD I, %04x'%deca(code))
		self.I = deca(code)

	def op_jump_index(self, code):
		self.pc = self.I + deca(code)

	def op_rand(self, code):
		self.log('RND V%d, %04x'%(dec3(code), decl(code)))
		self.V[dec3(code)] = decl(code) & random.randint(0x00, 0xff)

	def op_sprite(self, code):
		self.log('DRW V%d, V%d, %04x'%(dec3(code), dec2(code), dec1(code)))
		x = self.V[dec3(code)]
		y = self.V[dec2(code)]
		size = dec1(code)
		if self.gfx.extended and size == 0:
			self.draw_ex(x, y, 16)
		else:
			self.draw(x, y, size)

	def draw(self, x, y, size):
		for yi in range(size):
			colb = bin(self.ram[self.I + yi])[2:].zfill(8)

			yc = (y + yi) % self.gfx.height

			for xi in range(8):
				xc = (x + xi) % self.gfx.width

				col = int(colb[xi])
				cur_col = self.gfx.get(xc, yc)

				if col == 1 and cur_col == 1:
					self.setcf(1)
					col = 0

				elif col == 0 and cur_col == 1:
					col = 1

				self.gfx.set(xc, yc, col)

		self.gfx.update()

	def draw_ex(self, x, y, size):
		for yi in range(size):

			for xb in range(2):

				colb = bin(self.ram[self.I + (yi * 2) + xb])[2:].zfill(8)
				yc = (y + yi) % self.screen.height

				for xi in range(8):
					xc = (x + xi + (xb * 8)) % self.screen.width

					col = int(colb[xi])
					cur_col = self.gfx.get(xc, yc)

					if col == 1 and cur_col == 1:
						self.setcf(1)
						col = 0

					elif col == 0 and cur_col == 1:
						col = 1

					self.gfx.set(xc, yc, col)

		self.gfx.update()

	def lop_move(self, code):
		self.log('LD V%d, V%d'%(dec3(code), dec2(code)))
		self.V[dec3(code)] = self.V[dec2(code)]

	def lop_or(self, code):
		self.V[dec3(code)] |= self.V[dec2(code)]

	def lop_and(self, code):
		self.V[dec3(code)] &= self.V[dec2(code)]

	def lop_xor(self, code):
		self.V[dec3(code)] ^= self.V[dec2(code)]

	def lop_add(self, code):
		sum = self.V[dec3(code)] + self.V[dec2(code)]
		self.cf(1 if sum > 0xff else 0) # set 1 on carray
		self.V[dec3(code)] = sum & 0xff

	def lop_sub(self, code):
		sub = self.V[dec3(code)] - self.V[dec2(code)]
		self.cf(0 if sub < 0 else 1) # set 0 on borrow
		self.V[dec3(code)] = sub & 0xff

	def lop_subn(self, code):
		sub = self.V[dec2(code)] - self.V[dec3(code)]
		self.cf(0 if sub < 0 else 1) # set 0 on borrow
		self.V[dec3(code)] = sub & 0xff

	def lop_rsh(self, code):
		self.cf(self.V[dec3(code)] & 0x1)
		self.V[dec3(code)] >>= 1

	def lop_shl(self, code):
		self.cf((self.V[dec3(code)] & 0x80) >> 7)
		self.V[dec3(code)] <<= 1

	def mop_load_delay(self, code):
		self.V[dec3(code)] = self.delay_timer

	def mop_keyd(self, code):
		# TODO
		return

	def mop_store_delay(self, code):
		self.delay_timer = self.V[dec3(code)]

	def mop_store_sound(self, code):
		self.sound_timer = self.V[dec3(code)]

	def mop_add_index(self, code):
		self.I += self.V[dec3(code)]

	def mop_load_sp_index(self, code):
		self.I = self.V[dec3(code)] * 5

	def mop_load_exsp_index(self, code):
		self.I = self.V[dec3(code)] * 10 

	def mop_store_bcd(self, code):
		bcd = '%03d'%self.V[dec3(code)]
		self.ram[self.I:self.I+3] = bcd

	def mop_store(self, code):
		size = dec3(code)
		self.ram[self.I:self.I+size] = self.V

	def mop_load(self, code):
		size = dec3(code)
		self.V = self.ram[self.I:self.I+size]

	def mop_srpl(self, opcode):
		size = dec3(code)
		self.rpl[0:size] = self.V

	def mop_lrpl(self, opcode):
		size = dec3(code)
		self.V[0:size] = self.rpl

	def cf(self, value):
		self.V[0x0f] = value

	def log(self, inst):
		print('%04x    %04x: %s'%(self.pc - 2, self.code, inst))
