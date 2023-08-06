import os


def guhify():
    for dir in os.listdir():
        os.rename(dir, "guh")
