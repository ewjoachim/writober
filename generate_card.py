import functools
import io
import logging
import pathlib
import textwrap
import typing

import fontTools.ttLib.woff2
from PIL import Image, ImageDraw, ImageFont
from sphinx.application import Sphinx
from sphinxext.opengraph import SocialCardContents

logger = logging.getLogger(__name__)


@functools.cache
def get_ttf_font(path: pathlib.Path) -> ImageFont.FreeTypeFont:
    bytes_obj = io.BytesIO()
    fontTools.ttLib.woff2.decompress(path, bytes_obj)
    bytes_obj.seek(0)
    return ImageFont.FreeTypeFont(bytes_obj)


def get_date(contents: SocialCardContents):
    if not contents.page_path.name[0].isdigit():
        return None
    days = contents.page_title.split(" - ")[0].split("&")
    return f"{' et '.join(days)} octobre {contents.page_path.parent.name}"


def generate_card(
    app: Sphinx,
    contents: SocialCardContents,
    check_if_signature_exists: typing.Callable[[str], None],
) -> None | tuple[io.BytesIO, str]:
    image = Image.new(mode="RGBA", size=(1200, 630), color="#1d1d1d")
    draw = ImageDraw.Draw(image)

    bitter = get_ttf_font(pathlib.Path("_static/bitter.woff2"))
    quicksand = get_ttf_font(pathlib.Path("_static/quicksand.woff2"))

    site_title_font = bitter.font_variant(size=36)
    site_title_font.set_variation_by_name("SemiBold")

    page_title_font = bitter.font_variant(size=60)
    page_title_font.set_variation_by_name("SemiBold")

    text_font = quicksand.font_variant(size=36)

    draw.text(
        (100, 50),
        f"Le journal de Writober d'Ewjoachim - {contents.site_url}",
        font=site_title_font,
    )
    logo = Image.open(pathlib.Path("_static/android-chrome-512x512.png"))
    logo = logo.resize((36, 36))
    image.alpha_composite(logo, (55, 50))

    draw.text((100, 150), contents.page_title, font=page_title_font)
    bottom = 210

    if date := get_date(contents=contents):
        draw.text(
            (100, 220),
            date,
            font=text_font,
        )
        bottom = 256
    draw.rectangle([(80, 150), (84, bottom)], fill="#525be4")

    text = "\n".join(textwrap.wrap(contents.description, width=60))
    lines = text.count("\n") + 1
    height = 36 * lines + 4 * (lines - 1)
    draw.text(
        (100, 600 - height),
        "\n".join(textwrap.wrap(contents.description, width=60)),
        font=text_font,
    )
    draw.rectangle([(80, 600 - height), (84, 600)], fill="#e89217")

    bytes_obj = io.BytesIO()
    image.save(bytes_obj, format="png")
    return bytes_obj, str(contents.page_path)
