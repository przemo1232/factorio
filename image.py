import base64
import zlib
import png
import json
from config import full_py as tile_to_color

def mse(pixel: list, ref: list) -> float:
    """error between tile and reference"""
    err = 0
    for x, y in zip(pixel, ref):
        err += (x-y)**2
    return err / 3

def choose_tile(pixel: list, width: int) -> str:
    """choosing the appropriate tile"""
    tile = ''
    err = 1e5
    for color in tile_to_color:
        bound = mse(pixel, tile_to_color[color])
        if bound < err:
            err = bound
            tile = color
    err = []
    for old_color, new_color in zip(pixel, tile_to_color[tile]):
        err.append(old_color - new_color)
    return tile, err

def multiply_list(mult: float, pixel: list):
    for x in pixel:
        x *= mult
    return pixel

def dither(i: int, jump: int, err: list, width: int, values: list):
    """Floyd–Steinberg dithering"""
    if (i // jump) % width != width - 1:
        values[i + jump: i + jump + 3] += multiply_list(7/16, err)
    try:
        values[i + (width - 1) * jump: i + (width - 1) * jump + 3] += multiply_list(3/16, err)
        values[i + width * jump: i + width * jump + 3] += multiply_list(5/16, err)
        values[i + (width + 1) * jump: i + (width + 1) * jump + 3] += multiply_list(1/16, err)
    except IndexError:
        pass

def make_string(in_filename: str, out_filename: str):
    """make string from png file"""
    image = png.Reader(in_filename)
    # hopefully handles pngs with or without alpha channels, not tested
    jump = 3
    try:
        image.asRGB()
    except png.Error:
        jump = 4
    image = image.read_flat()
    width = image[0]
    values = image[2].tolist()

    tiles = []
    for i in range(0, len(values), jump):
        tile, err = choose_tile(values[i: i + 3], width)
        tiles.append(tile)
        dither(i, jump, err, width, values)

    # actually making the json
    output = {'blueprint': {'tiles': [], 'item': 'blueprint', 'version': 281479277707264}}
    for i, tile in enumerate(tiles):
        output['blueprint']['tiles'].append({
            'position': {'x': i % width, 'y': i // width},
            'name': tile
        })

    # convert json to bp
    bstring = json.dumps(output)
    bstring = zlib.compress(bstring.encode('utf-8'))
    bstring = base64.b64encode(bstring)
    bstring = bstring.decode('utf-8')
    bstring = '0' + bstring

    file = open(out_filename, 'w', encoding='utf-8')
    file.write(bstring)
    file.close()


def read_string(in_filename: str,  out_filename: str):
    """decode string into json"""
    file = open(in_filename, 'r')
    bstring = file.read()
    file.close()
    bstring = bstring.removeprefix('0')
    bstring = base64.b64decode(bstring)
    file = open(out_filename, 'w', encoding='utf-8')
    file.write(zlib.decompress(bstring).decode('utf-8'))
    file.close()

def read_json(in_filename: str,  out_filename: str):
    """encode json into string"""
    file = open(in_filename, 'r')
    bstring = file.read()
    file.close()
    bstring = zlib.compress(bstring.encode('utf-8'))
    bstring = base64.b64encode(bstring)
    bstring = bstring.decode('utf-8')
    bstring = '0' + bstring
    file = open(out_filename, 'w', encoding='utf-8')
    file.write(bstring)
    file.close()

choice = input('choose mode (1-3):\n1. make bp string from png file\n2. decode bp string into json\n3. encode json into string\n')
input_file = input('choose input file\n')
if choice == '1':
    make_string(input_file, 'bp.txt')
elif choice == '2':
    read_string(input_file, 'bp.txt')
elif choice == '3':
    read_json(input_file, 'bp.txt')
