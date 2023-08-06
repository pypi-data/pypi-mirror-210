from enum import Enum
from typing import *
from PIL import Image, ImageFont
import json
from .image_processing import ImageProcessing
from ..ext.checks import enforce_type

class ComponentType(Enum):
    PANEL = 1
    TEXT = 2
    IMAGE = 3
    HTML = 4

configs = json.load(open("configs.json"))

configs["base_color"] = tuple(configs["base_color"])
configs["base_color_transparent"] = tuple(configs["base_color_transparent"])
configs["foreground_color"] = tuple(configs["foreground_color"])

class BaseComponent:
    def __init__(self, name: str, type: ComponentType, **attrs):
        self.name = name
        self.type = type
        self.font = configs["base_font"]
        self.fsize: int = enforce_type(
            "font-size",
            attrs.get("fsize") or
            attrs.get("font-size") or
            configs["base_font_size"],
            int
        )

        # ALL Flags
        self.pos: Tuple[int, int] = enforce_type(
            "position",
            attrs.get("position"),
            tuple
        )

        # if self.type == ComponentType.PANEL
        self.repos: Tuple[int, int] = enforce_type(
            "relative-position",
            attrs.get("repos") or
            attrs.get("relative-position"),
            tuple
        )
        self.attached_to: str = enforce_type(
            "attached-to",
            attrs.get("attached-to"),
            str
        )
        # self.focus: bool = attrs.get("focus")

        # Partial Flags (excludes Text)
        self.bradius = enforce_type(
            "border-radius",
            attrs.get("bradius") or
            attrs.get("border-radius") or
            0,
            int
        )

        self.bcolor: Tuple[int, int, int] = enforce_type(
            "border-color",
            attrs.get("bcolor") or
            attrs.get("border-color") or
            (0, 0, 0),
            tuple
        )

        # Panel Flags
        self.bgcolor: Tuple[int, int, int] = (
            attrs.get("bgcolor") or
            attrs.get("background-color") or
            (0, 0, 0)
        )

        self.psize: Tuple[int, int] = enforce_type(
            "panel-size",
            attrs.get("psize") or
            attrs.get("panel-size"),
            tuple
        )

        self.children: Dict[str, self.__class__] = {}



        # Text Flags (can be applied into a panel)
        self.text: str = enforce_type(
            "text",
            attrs.get("text"),
            str
        )
        self.tcolor: Tuple[int, int, int] = enforce_type(
            "text-color",
            attrs.get("tcolor") or
            attrs.get("text-color") or
            (0, 0, 0),
            tuple
        )

        self.highlight: bool = enforce_type(
            "highlight",
            attrs.get("highlight"),
            bool
        )
        self.italicize: bool = enforce_type(
            "italicize",
            attrs.get("italicize"),
            bool
        )
        self.bold: bool = enforce_type(
            "bold",
            attrs.get("bold"),
            bool
        )

        # Image Flags
        self.image = enforce_type(
            "image",
            attrs.get("image") or
            attrs.get("ipath"),
            str
        )

        self.ratio: int = enforce_type(
            "ratio",
            attrs.get("ratio"),
            int
        )

        # HTML Flags
        self.html = attrs.get("html")
        self.shtml: str = (
            attrs.get("shtml") or
            attrs.get("string-html")
        )

        self.css = attrs.get("css")
        self.scss: str = (
            attrs.get("scss") or
            attrs.get("string-css")
        )

        self.url = attrs.get("url")

    def center_with(self, component: "BaseComponent"):
        cen = list(self.center)
        if component.type == ComponentType.TEXT:
            font = ImageFont.truetype(component.font, component.fsize)
            bbox = font.getbbox(component.text)
            size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            cen[0] -= size[0] // 2
            cen[1] -= size[1] // 2
        elif component.type == ComponentType.IMAGE:
            bbox = ImageProcessing.ratio(
                component, Image.open(component.image)
            ).getbbox()
            cen[0] -= (bbox[2] - bbox[0]) // 2
            cen[1] -= (bbox[3] - bbox[1]) // 2
        elif component.type == ComponentType.PANEL:
            size = component.psize
            cen[0] -= size[0] // 2
            cen[1] -= size[1] // 2
        return cen[0] + self.pos[0], cen[1] + self.pos[1] - 10
        
    @property
    def center(self):
        if self.type == ComponentType.TEXT:
            font = ImageFont.truetype(self.font, self.fsize)
            bbox = font.getbbox(self.text)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        elif self.type == ComponentType.IMAGE:
            bbox = ImageProcessing.ratio(
                self, Image.open(self.image)
            ).getbbox()
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        elif self.type == ComponentType.PANEL:
            return self.psize[0] // 2, self.psize[1] // 2

    def __repr__(self):
        return f"BaseComponent [{self.name=}, {self.type=}, {self.pos=}, {self.repos=}, {self.attached_to=}, {self.bradius=}, {self.bcolor=}, {self.bgcolor=}, {self.psize=}, {self.text=}, {self.tcolor=}, {self.image=}, {self.ratio=}, {self.shtml=}, {self.scss=}]"


        

