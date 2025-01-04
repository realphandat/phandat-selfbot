import logging
import logging.handlers

from modules.general.color import Color

class CustomFormatter(logging.Formatter):
	console_template = "\x1b[43m%(asctime)s\x1b[0m - \x1b[38;5;212m%(name)s\x1b[0m - {}[%(levelname)s]{} %(message)s"
	file_template = "%(asctime)s - %(name)s - [%(levelname)s] %(message)s"

	formats = {
		logging.DEBUG: console_template.format(Color.gray, Color.reset) + " (%(filename)s : %(lineno)d)",
		logging.INFO: console_template.format(Color.blue, Color.reset),
		logging.WARNING: console_template.format(Color.yellow, Color.reset),
		logging.ERROR: console_template.format(Color.red, Color.reset) + " (%(filename)s : %(lineno)d)",
		logging.CRITICAL: console_template.format(Color.purple, Color.reset) + " (%(filename)s : %(lineno)d)",
	}

	def __init__(self, is_file = False):
		super().__init__(datefmt = "%d %b %Y %H:%M:%S")
		self.is_file = is_file

	def format(self, record):
		log_fmt = self.file_template if self.is_file else self.formats.get(record.levelno)
		formatter = logging.Formatter(fmt = log_fmt, datefmt = self.datefmt)
		return formatter.format(record)

class Log:
	def __init__(self, client):
		self.client = client

	async def create(self, name, file_mode, file_directory):
		logger = logging.getLogger(f"[{name.upper()}] - {str(self.client.user.name)}")
		logger.setLevel(logging.DEBUG)
		console_handler = logging.StreamHandler()
		console_handler.setFormatter(CustomFormatter())
		logger.addHandler(console_handler)
		if file_mode:
			file = f"{file_directory}{str(self.client.user.name)}.txt"
			file_handler = logging.handlers.WatchedFileHandler(file, encoding = "utf-8", mode = "a+")
			file_handler.setFormatter(CustomFormatter(is_file = True))
			logger.addHandler(file_handler)
			logger.info(f"Created {file}")
		return logger