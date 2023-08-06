from PIL import Image, ImageDraw, ImageFilter

class ImageProcessing:
    @staticmethod
    def ratio(component: "BaseComponent", im: Image) -> Image:
        if component.ratio:
            div = component.ratio / 100
            w, h = int(im.width * div), int(im.height * div)
            return im.resize((w, h))
        else:
            return im

    @staticmethod
    def border_radius(root, component: "BaseComponent", im: Image) -> Image:
        if component.bradius:
            blur_radius = 0
            offset = 4
            back_color = Image.new(im.mode, im.size, root._front_fill)
            offset = blur_radius * 2 + offset
            mask = Image.new("L", im.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((offset, offset, im.size[0] - offset, im.size[1] - offset), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

            ims_round = Image.composite(im, back_color, mask)
            return ims_round
        else:
            return im