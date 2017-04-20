import random

def get_background():
    lines = open('data/wallpapers.md').read().splitlines()
    line =random.choice(lines)
    return line[4:-1]
