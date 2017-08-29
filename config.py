import dialogs
import pickle
import pprint
import json

class Config():
	def __init__(self):
		self.vars = [
			('ROM', [
				{
					'key'    : 'rom_base_url',
					'type'   : 'url',
					'value'  : 'http://45.76.213.9/rom/',
					'title'  : 'URL Base',
				},
				{
					'key'    : 'rom_list',
					'type'   : 'text',
					'value'  : 'rom-list',
					'title'  : 'ROM List',
				},
				{
					'key'    : 'rom_dl_timeout',
					'type'   : 'number',
					'value'  : 3,
					'title'  : 'Download Timeout',
				},
			]),
			('RAM', [
				{
					'key'    : 'ram_sz',
					'type'   : 'number',
					'value'  : 4096,
					'title'  : 'RAM Size',
				},
			]),
			('CPU', [
				{
					'key'    : 'cpu_delay',
					'type'   : 'number',
					'value'  : 5000,
					'title'  : 'Fetch Delay',
				},
				{
					'key'    : 'cpu_delay_hz',
					'type'   : 'number',
					'value'  : 60,
					'title'  : 'Delay Timer Hz',
				},
				{
					'key'    : 'cpu_sound_hz',
					'type'   : 'number',
					'value'  : 60,
					'title'  : 'Sound Timer Hz',
				},
				{
					'key'    : 'cpu_entry',
					'type'   : 'number',
					'value'  : 512,
					'title'  : 'Entry Point',
				},
				{
					'key'    : 'cpu_ld_addr',
					'type'   : 'number',
					'value'  : 512,
					'title'  : 'Program Offset',
				},
				{
					'key'    : 'cpu_stack_sz',
					'type'   : 'number',
					'value'  : 24,
					'title'  : 'Stack Size',
				},
				{
					'key'    : 'cpu_trace',
					'type'   : 'switch',
					'value'  : False,
					'title'  : 'Instruction Trace',
				},
			]),
			('Keyboard', [
				{
					'key'    : 'kbd_delay',
					'type'   : 'number',
					'value'  : 200000,
					'title'  : 'Fetch Delay',
				},
			]),
			('Graphics', [
				{
					'key'    : 'gfx_show_fps',
					'type'   : 'switch',
					'value'  : True,
					'title'  : 'Show FPS',
				},
				{
					'key'    : 'gfx_frame_intvl',
					'type'   : 'number',
					'value'  : 1,
					'title'  : 'Frame Interval',
				},
				{
					'key'    : 'gfx_keysz',
					'type'   : 'number',
					'value'  : 48,
					'title'  : 'Key Size',
				},
			])
		]
		
		self.load()
		
	def load(self):
		try:
			with open('config.json', 'r') as f:
				self.from_dict(json.loads(f.read()))
		except IOError:
			pass
			
	def save(self):
		try:
			with open('config.json', 'w') as f:
				f.write(json.dumps(
					self.as_dict(), 
					indent=4, 
					sort_keys=True))
		except IOError:
			pass
			
	def as_dict(self):
		res = {}
		for _, a in self.vars:
			for d in a:
				res[d['key']] = d['value']
		return res
		
	def from_dict(self, dict):
		for k, v in dict.items():
			for i, t in enumerate(self.vars):
				for j, d in enumerate(t[1]):
					if d['key'] == k:
						self.vars[i][1][j]['value'] = v
	
	def __getattr__(self, key):
		for _, a in self.vars:
			for d in a:
				if d['key'] == key:
					return d['value']
		raise KeyError(key)
		
	def dialog(self):
		sections = [(k,[{
			'key': d['key'],
			'type': d['type'],
			'value': str(d['value']) if d['type'] == 'number' else d['value'],
			'title': d['title']
		} for d in a]) for k, a in self.vars]
		
		res = dialogs.form_dialog('Settings', sections = sections)
		
		if not res:
			return
			
		for _, a in self.vars:
			for d in a:
				if d['type'] == 'number':
					d['value'] = int(res[d['key']])
				else:
					d['value'] = res[d['key']]
		
		# pprint.pprint(self.vars)
		
		self.save()
