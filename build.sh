#!/bin/sh

rm -r build dist
pyinstaller -wF smm.py
wine /home/connor/.wine/drive_c/drive_c/python/Scripts/pyinstaller.exe -wF smm.py
