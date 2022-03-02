import pyautogui

from src.images_manager import move_to_with_randomness
from src.logger import logger, logger_with_positions


def go_to_account(account,  telegram='./telegram.conf'):
    x, y, w, h = account["chrome"]
    pos_click_x = x + w / 2
    pos_click_y = y + h / 2
    move_to_with_randomness(pos_click_x, pos_click_y, 1)
    pyautogui.click()
    pass
