# This is a sample Python script.
import sys
import time
import yaml
import src.bot_spg
from src.bot_commons import go_to_account
from src.images_manager import load_images, positions, move_to_with_randomness, show, addRandomness
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']

def to_set_accounts(accounts):
    result = dict()
    for i, k in enumerate(accounts):
        tempo = time.time()
        if c["conta_" + str(i)]['now']: tempo = 0
        result[i] = {
            "name": c["conta_" + str(i)]['nome'],
            "chrome": k,
            "login": tempo,
            "spg_login": time.time(),
            "heroes": [],
            "space": c["conta_" + str(i)]['spg']
        }
    return result


def main():
    """Main execution setup and loop"""
    images = load_images()
    accounts = positions(images['chrome'], threshold=ct['chrome'])
    accounts = to_set_accounts(accounts)
    number_of_accounts = len(accounts)
    index = 0
    while True:
        account = accounts[index % number_of_accounts]
        if len(accounts) > 1: go_to_account(account)
        if account['space']:
            src.bot_spg.main(account)
        index += 1
        time.sleep(60)


if __name__ == '__main__':
    main()
