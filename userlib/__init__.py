#!/usr/bin/env python3
# Global User Library

__all__ = ["utils", "verify", "game", "nbtool", "exceptions", "get_tmp"]

import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Union
from . import utils, verify, game, nbtool, exceptions
# from .tmpenv import get_tmp

try:
    unifont16 = ImageFont.truetype("fonts/unifont-13.0.06.ttf", 16)
    unifont32 = ImageFont.truetype("fonts/unifont-13.0.06.ttf", 32)
    sarasa_f32 = ImageFont.truetype("fonts/sarasa-fixed-sc-regular.ttf", 32)
    fira_xdi8_32 = ImageFont.truetype("fonts/FiraXdi8-Regular.ttf", 32)
except:
    print("[userlib] font import error, ignored.")


def draw_img_from_text(size: tuple[int, int], text: str,
                       output: tuple[str, str],
                       font: Union[ImageFont.FreeTypeFont,
                                   ImageFont.ImageFont],
                       margin: int = 8, line_space: int = 2,
                       bg_color: tuple[int, int, int] = (255, 255, 255),
                       fg_color: tuple[int, int, int] = (0, 0, 0)):
    """
    Args:
      size              (width, height)
      text              "text..."
      font              Font type from PIL.ImageFont
      margin            Margin of image
      line_space        Space between lines
      output            (file_path, format)
      bg_color          (R, G, B)
    """
    im = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(im)
    lines = list[str]()
    for para in text.split("\n"):
        trick = 0
        for char_i in range(len(para)):
            width_ = draw.textbbox((0, 0), para[trick:char_i],
                                   font=font, spacing=2,
                                   anchor="lt")
            if width_[2] - width_[0] + 5 * margin - size[0] <= 0:
                if char_i + 1 == len(para):
                    lines.append(para[trick:])
            else:
                lines.append(para[trick:char_i])
                trick = char_i
                pass
            pass
        pass
    textline = "\n".join(lines)
    # print(textline)
    _, h1, _, h2 = draw.textbbox((0, 0), textline, font=font, spacing=2)
    im.resize((size[0], h2 - h1 + 2 * margin))
    draw.text((margin, margin), textline, font=font, fill=fg_color, spacing=2)
    im.save(*output)


def gen_tmp(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    _, fp = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.chmod(fp, 0o644)
    return fp
