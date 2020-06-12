import os
import shutil

nameNewModule = input("Как будет называться новый модуль:").strip()
if nameNewModule in os.listdir("modules"):
    print("Модуль с таким именем уже существует!")
else:
    shutil.copytree('example/TestModule', f'modules/{nameNewModule}')
    print(f"Добавил новый модуль {nameNewModule}.")
