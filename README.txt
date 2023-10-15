steps to create a blueprint:
- check if the config file is ok, add or delete tiles if necessary
- check the game version by decoding a random bp string into json and reading the version at the end
- put your version number into the string on line 43
- start the program and choose a png file (remember to include the file extension), output is bp.txt

the config can have multiple presets, change them by changing the import
dithering as well as grayscale can be toggled in the config