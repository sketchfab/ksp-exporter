#KSP exporter to Sketchfab#

This exporter allows you to publish your craft from Kerbal Space Program to Sketchfab.
Uses Python3 and PyQt5

## Execute in command line ##

The exporter can be launched in command line through kspmanager.py.

###Parameters###
`-g`      set your game directory if different of "C:\Kerbal Space Program"

`-l`      list all the existing crafts from the game

`-u`      upload the craft that has the index INDEX in the list

*Sketchfab parameters*

`--token`        set the sketchfab api token of the sketchfab account to upload the craft to. Your Sketchfab API token can be found in your Sketchfab profile : `Settings -> Password & API`

`--name`        the name to give to the sketchfab model


`--description`   provide a description of the model

`--tags`         add tags to the model

`--draft`         set model as draft (don't publish immediately)

`--private`         set model as private (PRO accounts only)

`--password`        protect a private model with a password (PRO accounts only)

### List craft files that are available in the game
`python kspmanager.py [-g GAME_DIRECTORY] -l`

### Upload a craft ###
```
python kspmanager.py -u 2 --token 1234567890ABCDEFGHIJKLMNOPQRSTUV
    --name "Super lander"
    --description "This is my first craft"
    --tags "Lander kerbalspaceprogram"
```

## Build EXE with pyinstaller ##

Common qt binaries directory: `C:/Qt/5.7/msvc2015/bin`

`pyinstaller -F -w --paths 'C:/Qt/5.7/msvc2015/bin' -i 'resources/ksp2skfb_256.ico' ksp2sketchfab.py`
