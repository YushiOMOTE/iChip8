import urllib.request
import dialogs
import console
import time

from emul.system import System
from config import Config

class Menu:
	def __init__(self, cfg):
		self.cfg = cfg
	
	def show(self):
		opts = self.opt_rom() + self.opt_misc()
		
		sel = dialogs.list_dialog('Menu', opts)
		
		# nothing selected; stop the process
		if not sel:
			return False
		
		sel['handler'](sel)
		
		# something selected; keep running
		return True
	
	def opt_rom(self):
		list = self.load_list(
			self.cfg.rom_base_url + self.cfg.rom_list)
			
		if not list:
			console.alert('Error', 'Cannot download ROM list', 'Ok', hide_cancel_button = True)
			return []
	
		return [{
			'title'  : title,
			'image'  : 'iob:game_controller_b_32',
			'handler': self.preset,
		} for title in list]
	
	def opt_misc(self):
		return [{
			'title'    : 'CUSTOM',
			'image'    : 'iob:cloud_32',
			'handler'  : self.custom,
		},{
			'title'    : 'SETTINGS',
			'image'    : 'iob:settings_32',
			'handler'  : self.config,
		}]

	def preset(self, sel):
		url = self.cfg.rom_base_url + sel['title']
		self.emulate(url)
	
	def custom(self, sel):
		try:
			url = console.input_alert('Custom URL', 'Input your custom url')
			self.emulate(url)
		except:
			pass
		
	def config(self, sel):
		self.cfg.dialog()
	
	def emulate(self, url):
		rom = self.load_rom(url)
		
		if not rom:
			console.alert('Error', 'Cannot download ROM', 'Ok', hide_cancel_button = True)
		
		else:
			with System(**self.cfg.as_dict()) as sys:
				sys.start(rom)
			
			time.sleep(0.5)
	
	def load_rom(self, url):
		try:
			return bytearray(urllib.request.urlopen(url, timeout=self.cfg.rom_dl_timeout).read())
		except:
			return None
		
	def load_list(self, url):
		try:
			list = urllib.request.urlopen(url, timeout=self.cfg.rom_dl_timeout).readlines()
			return [i.decode('utf-8').strip() for i in list]
		except:
			return None
