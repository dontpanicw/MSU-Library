import logging
import colorlog
import inspect

# Создаем объект логгера
logger = logging.getLogger(__name__)

# Создаем объект форматирования логов с цветами
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}
log_formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат времени без долей секунд
    log_colors=log_colors,
)

# Создаем обработчик для вывода на консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Устанавливаем уровень логгирования (можете выбрать свой)
logger.setLevel(logging.DEBUG)

# Добавляем обработчик к логгеру
logger.addHandler(console_handler)
