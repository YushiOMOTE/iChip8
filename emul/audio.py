import sound

class Audio:
	def boot(self):
		sound.play_effect('game:Woosh_1')
	
	def effect(self):
		sound.play_effect('game:Beep')
		
	def shutdown(self):
		sound.play_effect('game:Woosh_2')
