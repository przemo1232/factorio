import base64
import zlib
import png
import json
from config import full_py as tile_to_color

class Pixel:
    values = []
    pos = 0
    x = 0
    y = 0
    tile = ''
    def __init__(self, colors):
        self.values = colors[0:3]

    def mse(self, ref: list) -> float:
        """error between tile and reference"""
        err = 0
        for x, y in zip(self.values, ref):
            err += (x-y)**2
        return err / 3

    def choose_tile(self):
        """choosing the appropriate tile"""
        err = 1e5
        for color in tile_to_color:
            bound = self.mse(tile_to_color[color])
            if bound < err:
                err = bound
                self.tile = color
        err = []
        for old_color, new_color in zip(self.values, tile_to_color[self.tile]):
            err.append((old_color - new_color) >> 4)
        return err
    
    def add_values(self, values: list):
        for i, err_value in enumerate(values):
            self.values[i] += err_value

def dither(pixel: Pixel, err: list, width: int, height: int, pixels: list[Pixel]):
    """Floyd-Steinberg dithering"""
    if pixel.x < width - 1:
        print(f"old: {pixels[pixel.pos + 1].values}")
        pixels[pixel.pos + 1].add_values([value * 7 for value in err])
        if pixel.y < height - 1:
            pixels[pixel.pos + width + 1].add_values(err)
        print(f"new: {pixels[pixel.pos + 1].values}")
    if pixel.y < height - 1:
        pixels[pixel.pos + width - 1].add_values([value * 3 for value in err])
        pixels[pixel.pos + width].add_values([value * 5 for value in err])

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
    height = image[1]
    values = image[2].tolist()
    tiles = []
    pixels: list[Pixel] = []

    for i in range(0, len(values), jump):
        pixels.append(Pixel(values[i: i + 3]))
    for i, pixel in enumerate(pixels):
        pixel.pos = i
        pixel.x = i % width
        pixel.y = i // width
        err = pixel.choose_tile()
        dither(pixel, err, width, height, pixels)
        tiles.append(pixel.tile)

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
