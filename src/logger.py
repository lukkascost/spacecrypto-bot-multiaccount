import cv2
import mss
import numpy as np

from src.date import dateFormatted

import sys
import yaml
import telegram_send

stream = open("./config.yaml", 'r')
c = yaml.safe_load(stream)

last_log_is_progress = False

COLOR = {
    'blue': '\033[94m',
    'default': '\033[99m',
    'grey': '\033[90m',
    'yellow': '\033[93m',
    'black': '\033[90m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'magenta': '\033[95m',
    'white': '\033[97m',
    'red': '\033[91m'
}


def logger_with_positions(message, rectangles, account,telegram, progress_indicator=False, color='default'):
    global last_log_is_progress
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    color_formatted = COLOR.get(color.lower(), COLOR['default'])

    formatted_datetime = dateFormatted()
    formatted_message = "[{}] [{}] => {}".format(account['name'], formatted_datetime, message)
    formatted_message_colored = color_formatted + formatted_message + '\033[0m'

    # Start progress indicator and append dots to in subsequent progress calls
    if progress_indicator:
        if not last_log_is_progress:
            last_log_is_progress = True
            formatted_message = color_formatted + "[{}] => {}".format(formatted_datetime, '⬆️ Processing last action..')
            sys.stdout.write(formatted_message)
            sys.stdout.flush()
        else:
            sys.stdout.write(color_formatted + '.')
            sys.stdout.flush()
        return

    if last_log_is_progress:
        sys.stdout.write('\n')
        sys.stdout.flush()
        last_log_is_progress = False

    print(formatted_message_colored)
    cv2.imwrite('tmp.png', img)
    try:
        telegram_send.send(messages=[formatted_message], images=[open("tmp.png", "rb")], conf=telegram)
    except Exception:
        pass
    if (c['save_log_to_file'] == True):
        logger_file = open("./logs/logger.log", "a", encoding='utf-8')
        logger_file.write(formatted_message + '\n')
        logger_file.close()

    return True


def logger(message, account, telegram, progress_indicator=False, color='default'):
    global last_log_is_progress
    color_formatted = COLOR.get(color.lower(), COLOR['default'])

    formatted_datetime = dateFormatted()
    formatted_message = "[{}] [{}] => {}".format(account['name'], formatted_datetime, message)
    formatted_message_colored = color_formatted + formatted_message + '\033[0m'

    # Start progress indicator and append dots to in subsequent progress calls
    if progress_indicator:
        if not last_log_is_progress:
            last_log_is_progress = True
            formatted_message = color_formatted + "[{}] => {}".format(formatted_datetime, '⬆️ Processing last action..')
            sys.stdout.write(formatted_message)
            sys.stdout.flush()
        else:
            sys.stdout.write(color_formatted + '.')
            sys.stdout.flush()
        return

    if last_log_is_progress:
        sys.stdout.write('\n')
        sys.stdout.flush()
        last_log_is_progress = False

    print(formatted_message_colored)
    try:
        telegram_send.send(messages=[formatted_message], conf=telegram)
    except Exception:
        pass
    if (c['save_log_to_file'] == True):
        logger_file = open("./logs/logger.log", "a", encoding='utf-8')
        logger_file.write(formatted_message + '\n')
        logger_file.close()

    return True
