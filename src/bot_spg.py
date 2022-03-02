import sys
import time
import pyautogui
import telegram_send
import yaml
import webbrowser
import numpy as np

from src.bot_commons import go_to_account
from src.images_manager import load_images, positions, move_to_with_randomness, show, addRandomness, click_btn
from src.logger import logger, logger_with_positions

stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause


def open_game(account):
    logger('🎉 Opening game!', account, telegram="./telegram_spg.conf")
    webbrowser.open("https://play.spacecrypto.io/")


def connect_game(account):
    images = load_images("./spg_targets/")
    logger('🎉 Searching for connect wallet button!', account, telegram="./telegram_spg.conf")
    click_btn(images['connect-wallet'], timeout=120)
    error = click_btn(images['close_error'], timeout=3)
    if error:
        connect_game(account)
        return None
    logger('🎉 Searching for metamask signin button!', account, telegram="./telegram_spg.conf")
    click_btn(images['select-wallet'], timeout=20)


def go_to_boss_hunt(account):
    images = load_images("./spg_targets/")
    logger('🎉 going to game home!', account, telegram="./telegram_spg.conf")
    click_btn(images['play-game'], timeout=120)


def scroll(acc):
    images = load_images("./spg_targets/")
    commoms = positions(images['order'], threshold=ct['energy'])
    if (len(commoms) == 0):
        return
    x, y, w, h = commoms[len(commoms) - 1]
    #
    move_to_with_randomness(x + 100, y + 400, 1)
    pyautogui.dragRel(0, -300, duration=4, button='left')
    time.sleep(1)


def select_spaceship(account):
    time.sleep(addRandomness(3, 1))
    images = load_images("./spg_targets/")
    remove_spaceships(account)
    working = 0
    logger_with_positions('🎉 selecting Spacechips  !'.format(working), [], account, telegram="./telegram_spg.conf")

    for i in range(c['spg_scroll_times'] + 1):
        spacechips = positions(images['fight'], threshold=ct['energy'])
        while working <= c['spg_team_members_max'] and len(spacechips) > 0:
            x, y, w, h = spacechips[0]
            move_to_with_randomness(x + (w / 2), y + (h / 2), 1)
            pyautogui.click()
            account['heroes'].append(spacechips[0])
            working += 1
            time.sleep(addRandomness(1))
            spacechips = positions(images['fight'], threshold=ct['energy'])
        if working >= c['spg_team_members_max']:
            break
        scroll(account)
    logger_with_positions('🎉 {} Spacechips selected !'.format(working), [], account, telegram="./telegram_spg.conf")
    if working <= (c['spg_team_members_max'] /2):
        return 0
    return working


def remove_spaceships(account):
    time.sleep(addRandomness(3, 1))
    images = load_images("./spg_targets/")
    spacechips = positions(images['remove'], threshold=ct['energy'])
    logger_with_positions('🎉 removing Spacechips  !', [], account, telegram="./telegram_spg.conf")
    while len(spacechips) > 0:
        x, y, w, h = spacechips[0]
        move_to_with_randomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        time.sleep(addRandomness(1))
        spacechips = positions(images['remove'], threshold=ct['energy'])
    account['heroes'] = []
    logger_with_positions('🎉 Spacechips removed !', [], account, telegram="./telegram_spg.conf")



def wait_finish_boss(account):
    time.sleep(addRandomness(3, 1))
    images = load_images("./spg_targets/")
    lose = click_btn(images['confirm-lose'], threshold=ct['start_boss_hunt'])
    win_counter = 0
    timeout = 10*60
    start = time.time()
    while (not lose) and timeout > (time.time() - start):
        win = positions(images['confirm-win'], threshold=ct['energy'])
        if len(win) > 0:
            win_counter += 1
            logger_with_positions("{} BATTLE WIN! ".format(win_counter), win, account, telegram="./telegram_spg.conf")
            click_btn(images['confirm-win'], threshold=ct['start_boss_hunt'], timeout=5)
        lose = click_btn(images['confirm-lose'], threshold=ct['start_boss_hunt'], timeout=5)
    time.sleep(addRandomness(5, 1))
    logger_with_positions('🎉 Boss finished!', [], account, telegram="./telegram_spg.conf")
    go_home = click_btn(images['go_home'], threshold=ct['start_boss_hunt'], timeout=5)
    start = time.time()
    plus = 0
    while go_home and (timeout/10) > (time.time() - start) and plus == 0:
        time.sleep(addRandomness(3, 1))
        go_home = click_btn(images['go_home'], threshold=ct['start_boss_hunt'], timeout=5)
        plus = len(positions(images['plus'], threshold=ct['energy']))


def start_boss_fight(account):
    time.sleep(addRandomness(3, 1))
    logger_with_positions('🎉 Starting boss fight!', [], account, telegram="./telegram_spg.conf")
    images = load_images("./spg_targets/")
    click_btn(images['fight-boss'], threshold=ct['start_boss_hunt'])
    click_btn(images['confirm-lose'], threshold=ct['start_boss_hunt'])
    wait_finish_boss(account)
    remove_spaceships(account)


def game(account):
    while select_spaceship(account) > 0:
        start_boss_fight(account)


def close_game(account):
    logger('🎉 Closing game!', account, telegram="./telegram_spg.conf")
    pyautogui.hotkey('ctrl', 'w')


def main(account):
    t = c['time_intervals']
    now = time.time()
    if now - account["spg_login"] > addRandomness(t['check_for_game'] * 60):
        sys.stdout.flush()
        open_game(account)
        connect_game(account)
        go_to_boss_hunt(account)
        game(account)
        close_game(account)
        account["spg_login"] = time.time()
