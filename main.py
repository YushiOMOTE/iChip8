import logging

from config import Config
from menu import Menu

def main():
	logging.basicConfig(level=logging.INFO, format='%(message)s')
	
	# instantiate global config
	cfg = Config()
	
	# instantiate menu
	menu = Menu(cfg)
	
	# keep prompting until user cancels
	while menu.show():
		pass
	
if __name__ == '__main__':
		main()

