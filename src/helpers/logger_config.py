from loguru import logger

logger.remove()

# Add a new sink that logs to the console with desired settings
logger.add(
    sink=lambda msg: print(msg.strip()),  # Standard output (console)
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",  # Minimum log level to capture
    colorize=True  # Enables colorful logs
)