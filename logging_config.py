import logging
from colorama import Fore, Style

# Цветной форматтер для консоли
class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        if record.levelno in self.COLORS:
            record.levelname = (f"{self.COLORS[record.levelno]}"
                                f"{record.levelname}{Style.RESET_ALL}")
            record.msg = (f"{self.COLORS[record.levelno]}"
                          f"{record.msg}{Style.RESET_ALL}")
        return super().format(record)

# Основной логгер
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)  # Уровень логгера

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Обработчик для логов уровня INFO и DEBUG
info_handler = logging.FileHandler("logs/info.log")
info_handler.setLevel(logging.DEBUG)  # Логи от DEBUG и выше
info_formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
info_handler.setFormatter(info_formatter)

# Обработчик для логов уровня ERROR и выше
error_handler = logging.FileHandler("logs/error.log")
error_handler.setLevel(logging.ERROR)  # Логи от ERROR и выше
error_formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
error_handler.setFormatter(error_formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(info_handler)
logger.addHandler(error_handler)

# Пример логов для проверки
logger.debug("Debug message")         # Появится в info.log и в консоли
logger.info("Info message")           # Появится в info.log и в консоли
logger.warning("Warning message")     # Появится в info.log и в консоли
logger.error("Error message")         # Появится в error.log и в консоли
logger.critical("Critical message")   # Появится в error.log и в консоли
