from .discord import *
import json

configs = {
    "base_color": (55, 57, 62, 1),
    "base_color_transparent": (55, 57, 62, 0),
    "foreground_color": (35, 39, 42),
    "base_font": "../fonts/SF-Pro-Rounded-Regular.otf",
    "base_font_size": 36
}

json.dump(configs, open("configs.json", "w"))

