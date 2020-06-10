import os
import sys
import traceback

from configs import cfg

modules = []

plugin_folder_files = os.listdir("modules")
if not plugin_folder_files:
    print("Нет установленных модулей.")
    exit()

sys.path.insert(0, "modules")
for file in plugin_folder_files:
    if file.startswith("__") and file.endswith(".py"):
        continue
    try:
        modules.append(__import__(os.path.splitext(file)[0]).main)
    except Exception:
        pass


def main():
    for x in modules:
        print(x())


if __name__ == '__main__':
    main()
