#KSP exporter to Sketchfab#

This exporter allows you to publish your craft from Kerbal Space Program to Sketchfab.

## Execute in command line ##

The exporter can be launched in command line through kspmanager.py.

### List craft files that are available in the game
`python kspmanager.py [-g GAME_DIRECTORY] -l`

### Upload a craft ###
`python kspmanager.py [-g GAME_DIRECTORY] -u CRAFT_INDEX --token API_TOKEN [-title] [--description] [--tags] [-c]`

**Game Directory**
If you installed the game in the default directory (C:\\Kerbal Space Program), you don't need to set the `-g` parameter.

**Select the craft to upload**
The CRAFT_INDEX is the index of the craft to upload in the list printed with the `-l` parameter

**Set the API token**
Your Sketchfab API token can be found in your Sketchfab profile : `Settings -> Password & API`

**Enable texture conversion**
Use the `-c`parameter to enable the texture conversion. It allows to convert .mbm texture files to png, in order to generate lighter .zip archive to upload. This option is more suitable for non PRO sketchfab users (upload files up to 50 MB), and makes the update be faster.

*TODO : building the UI*
