from enum import Enum
from typing import *
from PIL import Image, ImageFont
import json
from .image_processing import ImageProcessing

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
        self.fsize: int = (
            attrs.get("fsize") or
            attrs.get("font-size") or
            configs["base_font_size"]
        )

        # ALL Flags
        self.pos: Tuple[int, int] = attrs.get("position")

        # if self.type == ComponentType.PANEL
        self.repos: Tuple[int, int] = (
            attrs.get("repos") or
            attrs.get("relative-position")
        )
        self.attached_to = attrs.get("attached-to")
        # self.focus: bool = attrs.get("focus")

        # Partial Flags (excludes Text)
        self.bradius = (
            attrs.get("bradius") or
            attrs.get("border-radius") or
            0
        )

        self.bcolor: Tuple[int, int, int] = (
            attrs.get("bcolor") or
            attrs.get("border-color") or
            (0, 0, 0)
        )

        # Panel Flags
        self.bgcolor: Tuple[int, int, int] = (
            attrs.get("bgcolor") or
            attrs.get("background-color") or
            (0, 0, 0)
        )

        self.psize: Tuple[int, int] = (
            attrs.get("psize") or
            attrs.get("panel-size")
        )

        self.children: Dict[str, self.__class__] = {}



        # Text Flags (can be applied into a panel)
        self.text: str = attrs.get("text")
        self.tcolor: Tuple[int, int, int] = (
            attrs.get("tcolor") or
            attrs.get("text-color") or
            (0, 0, 0)
        )

        self.highlight: bool = attrs.get("highlight")
        self.italicize: bool = attrs.get("italicize")
        self.bold: bool = attrs.get("bold")

        # Image Flags
        self.image = (
            attrs.get("image") or
            attrs.get("ipath")
        )

        self.ratio: int = attrs.get("ratio")

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
            bbox = self.font.getbbox(self.text)
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


        

