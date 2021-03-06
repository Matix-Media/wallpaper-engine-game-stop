﻿from winreg import *
import platform
from os import path
import psutil
from time import sleep
from urllib import request
import urllib.error
from json import load as load_json, loads as load_json_str, JSONDecodeError
from os import system as run_subproc
from sys import argv as startup_args
import ctypes
from winreg import *


print("Booting...\n")

if len(startup_args) > 1:
    if startup_args[1] == "--hidden":
        print("App started in hidden mode.\n")
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Check if windows
if platform.architecture()[1] != "WindowsPE":
    print("This script is only for windows available.")
    exit(1)


# Reading settings
settings = {"check_delay": 20, "get_online_database": True}
print("Loading settings...")
try:
    with open("settings.json") as json_file:
        data = load_json(json_file)
        settings = data
except (JSONDecodeError, FileNotFoundError, FileExistsError) as e:
    print("Using built in settings.")


# Load games
games = []
print("Loading games...")
try:
    with open("games.json") as json_file:
        data = load_json(json_file)
        games = data
except (JSONDecodeError, FileNotFoundError, FileExistsError) as e:
    print("Using online game files.")

if settings["get_online_database"]:
    try:
        result = ""
        for line in urllib.request.urlopen("https://raw.githubusercontent.com/Matix-Media/wallpaper-engine-game-stop/master/games.json"):
            result += line.decode("utf-8") + "\n"
        data = load_json_str(result)
        for game in data:
            games.append(game)

    except urllib.error as e:
        print("Could not get online game files.")


# Get reg path
print("Detecting Platform...")
if not platform.machine().endswith('64'):
    aKey = "SOFTWARE\\Valve\\Steam"
else:
    aKey = "SOFTWARE\\Wow6432Node\\Valve\\Steam"


# Get key
aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)


print("Getting Steam Installation Folder...")


# Get value
aKey = OpenKey(aReg, aKey)

result = QueryValueEx(aKey, "InstallPath")

steam_path = result[0]


# Generating WPA Path
wpa_path = path.join(
    steam_path, "steamapps\\common\\wallpaper_engine", "wallpaper32.exe")


# Checking if wpa exists
print("Cheching if Wallpaper engine is installed...")
if not path.exists(wpa_path):
    print("Wallpaper engine is not installed in this system.")
    exit(1)
else:
    pass


print("\n\n")
# Main loop
pause_lasted = False
while True:
    processes = psutil.process_iter()
    games_running = False
    running_game = ""

    for p in processes:
        for game in games:
            try:
                if p.name() == game:
                    games_running = True
                    running_game = game
                    break
            except:
                pass

        if games_running:
            break

    if games_running:
        if not pause_lasted:
            print(
                f"Found \"{running_game}\" - stopping Wallpaper Engine")
            proc = run_subproc("\"" + wpa_path + "\" -control pause")
            pause_lasted = True
        else:
            pass
    else:
        if pause_lasted:
            proc = run_subproc("\"" + wpa_path + "\" -control play")
            pause_lasted = False
            print(f"Nothing found - playing Wallpaper Engine")
        else:
            pass

    sleep(settings["check_delay"])
