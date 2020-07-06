import PySimpleGUI as sg
import json 
import os
from pathlib import Path
import subprocess
import glob
from shutil import copyfile
import zipfile
import rarfile
import time

# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
def get_custom_maps(path_):
    maps = {}
    maps['Default'] =  '/Game/Tutorial/Intro/MAP_EntryPoint'
    if os.path.exists(path_):
        for path in Path(path_).rglob('*.umap'):
            maps[path.name.split(".umap")[0]] = os.path.split(path)[0]
    return maps

def update_session_config(path_, map):
    if map == 'Default':
        str_ = '﻿[/Script/EngineSettings.GameMapsSettings]\n\
GameDefaultMap = /Game/Tutorial/Intro/MAP_EntryPoint\n\
[/Script/Engine.PhysicsSettings]\n\
DefaultGravityZ = -980\n\
\n\
[/Script/Engine.RendererSettings]\n\
r.LightPropagationVolume = False\n\
r.DBuffer = True'
    else:
        str_ = '﻿[/Script/EngineSettings.GameMapsSettings]\n\
GameDefaultMap = /Game/Art/Env/NYC/' + map + '\n\
[/Script/Engine.PhysicsSettings]\n\
DefaultGravityZ = -980\n\
\n\
[/Script/Engine.RendererSettings]\n\
r.LightPropagationVolume = False\n\
r.DBuffer = True'
    with open(session_path + session_config_path, 'w') as file:
        file.write(str_)

def get_current_map(session_config_path):
    with open(session_config_path, 'r') as file:
        config = []
        for line in file:
            config.append(line)
        map = config[1].split('/')[-1]
        if map == 'MAP_EntryPoint':
            return 'Default'
        else:
            return map



# ---------------------------------------------------------
# Initialisation 
# ---------------------------------------------------------

home = str(Path.home())
log_file_loc = home + '/.smm/log.log'
config_file_loc = home + '/.smm/config.json'
content_path = "/SessionGame/Content"
current_map_path = "/SessionGame/Content/Art/Env/NYC"
session_config_path = "/SessionGame/Config/UserEngine.ini"
game_patch_path = "/SessionGame/Binaries/Win64/dxgi.dll"

default_config = '{"paths": {"session_game": ""}}'

try: 
    os.makedirs(home + '/.smm')
except OSError:
    pass
else:
    print('Creating ~/.smm directory')

if not  os.path.exists(config_file_loc):
    with open(config_file_loc, 'w') as config_file:
        config_file.write(default_config)

with open(config_file_loc, 'r') as config_file:
    config = config_file.read()
    js = json.loads(config)
session_path = js["paths"]["session_game"]
maps = get_custom_maps(session_path + content_path)
try:
    current_map = get_current_map(session_path + session_config_path)
except (FileNotFoundError, IndexError) as e:
    current_map = ""

if os.path.exists(session_path + game_patch_path):
    is_patched = 'Game is Patched'
    color = 'green'
else: 
    is_patched = 'Game is not Patched'
    color = 'red'


version = '0.0.1'
title = 'Session Mod Manager'
sg.theme('DarkAmber')
# Window Layout
col1 = [    [sg.Button('Reload Maps', key='reload'), sg.FileBrowse('Import Map', file_types=(('Zip Files','*.zip'),), key='import', target='zip')],
            [sg.Listbox(values=[*maps], size=(35, 10), key='maps')],
            [sg.Button('Load Map'), sg.Button('Start Session')],
            [sg.Text('Current Loaded Map: ' + current_map, key='current', size=(35,1))]]
col2 = [    [sg.Button('Clear')],
            [sg.Output(size=(35, 10), key='output')],
            [sg.Button('Patch Game'), sg.Button('Unpatch Game')],
            [sg.Text(is_patched, text_color=color, key='patched', size=(35,1))]]
layout = [  [sg.Text('Path to Session'), sg.In(session_path, key='input', enable_events=True), sg.FolderBrowse('...', target='input')],
            [sg.Column(col1), sg.Column(col2)],
            [sg.In(key='zip', visible=False, enable_events=True)],
            [sg.ProgressBar(1, orientation='h', size=(50, 7), key='progress')]]

# Create the Window
window = sg.Window(title + ' v' + version, layout)

# ---------------------------------------------------------
# Main Loop
# ---------------------------------------------------------
while True:
    event, values = window.read()
    if event in (None, sg.WINDOW_CLOSED):	# if user closes window or clicks cancel
        break

    if event in ('reload'):
        maps = get_custom_maps(session_path + content_path)
        window.FindElement('maps').Update(values=[*maps])


    if event in ('Load Map'):
        try:
            selected_map = values['maps'][0]
            map_path = maps[selected_map]
            # delete existing map
            files = glob.glob(session_path + current_map_path + '/*')
            for f in files:
                os.remove(f)
            # copy new map
            files = glob.glob(map_path + '/*')
            for f in files:
                file_name = os.path.split(f)[1]
                try:
                    copyfile(f, session_path + current_map_path + '/' + file_name)
                except IsADirectoryError:
                    pass
            update_session_config(session_path + session_config_path, selected_map)
            current_map = get_current_map(session_path + session_config_path)
            window.FindElement('current').Update('Current Loaded Map: ' + current_map)
            print(selected_map + ' Loaded!')
        except IndexError:
            print('No map selected')
        
    if event in ('Start Session'):
        print('Launching Session')
        subprocess.run(['steam', '-applaunch', '861650'])

    if event in ('input'):
        print('Session game path updated')
        session_path = values["input"]
        js["paths"]["session_game"] = session_path
        config = json.dumps(js)
        with open(config_file_loc, 'w') as config_file:
            config_file.write(config)
            maps = get_custom_maps(session_path + content_path)
            window.FindElement('maps').Update(values=[*maps])

    if event in ('Clear'):
        window.FindElement('output').Update('')

    if event in ('Patch Game'):
        copyfile('dxgi.dll', session_path + game_patch_path)
        is_patched = 'Game is Patched'
        color = 'green'
        window.FindElement('patched').Update(is_patched, text_color=color)
        print('Game Patched')
    if event in ('Unpatch Game'):
        os.remove(session_path + game_patch_path)
        is_patched = 'Game is not Patched'
        color = 'red'
        window.FindElement('patched').Update(is_patched, text_color=color)
        print("Game unpatched")
    if event in ('import'):
        print('Coming Soon!')
    if event in ('zip'):
        print('Importing ' + values['zip'])
        with zipfile.ZipFile(values['zip'], 'r') as zip:
            uncompress_size = sum((file.file_size for file in zip.infolist()))
            extracted_size = 0
            for file in zip.infolist():
                print('Extracting ' + file.filename)
                extracted_size += file.file_size
                window.FindElement('progress').UpdateBar(extracted_size, uncompress_size)
                zip.extract(file, session_path + content_path)
        maps = get_custom_maps(session_path + content_path)
        window.FindElement('maps').Update(values=[*maps]) 
        print('Import Completed')


   
        
    

window.close()