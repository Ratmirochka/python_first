from loguru import logger

def get_logger(file_name):
    logger.remove()
    logger.add(f"logs/{file_name}", level='DEBUG', format="{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message}",
               rotation="500 MB")
    return logger