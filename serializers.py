from io import BytesIO
from pathlib import Path

from notion.block import *
from PIL import Image
import requests


class SerializerFactory:
    def __init__(self):
        pass

    def get_serializer(self, block: BasicBlock, **kwargs):
        serializer_class = {
            TextBlock: TextSerializer,
            HeaderBlock: HeaderBlockSerializer,
            SubheaderBlock: SubheaderBlockSerializer,
            SubsubheaderBlock: SubsubheaderBlockSerializer,
            BulletedListBlock: UnorderedListBlockSerializer,
            NumberedListBlock: NumberedListBlockSerializer,
            QuoteBlock: QuoteBlockSerializer,
            PageBlock: PageBlockSerializer,
            ImageBlock: ImageBlockSerializer,
            ToggleBlock: UnorderedListBlockSerializer,
        }[type(block)]
        return serializer_class(block, **kwargs)


class Seralizer:
    def __init__(self, block: Block, level=0):
        self.block = block
        self.level = level

    def serialize(self) -> str:
        raise NotImplementedError


class TextSerializer(Seralizer):
    def serialize(self) -> str:
        if self.block.title:
            return " " * (2 * self.level) + self.block.title + '\n'
        return ''


class HeaderBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return "# {}\n".format(self.block.title)


class SubheaderBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return "## {}\n".format(self.block.title)


class SubsubheaderBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return "### {}\n".format(self.block.title)


class AbstractListBlockSerializer(Seralizer):
    mark = None
    def serialize(self) -> str:
        texts = [" " * (2 * self.level) + self.mark + " {}\n".format(self.block.title)]
        f = SerializerFactory()
        for child in self.block.children:
            texts.append(f.get_serializer(child, level=self.level + 1).serialize())
        return ''.join(texts)

class UnorderedListBlockSerializer(AbstractListBlockSerializer):
    mark = '-'

class NumberedListBlockSerializer(AbstractListBlockSerializer):
    mark = '1.'

class QuoteBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return '> {}\n'.format(self.block.title)


# todo: add a state machine here, to add extra \n after listblock, quoteblock etc
class PageBlockSerializer(Seralizer):
    def serialize(self) -> str:
        texts = []
        f = SerializerFactory()
        for child in self.block.children:
            texts.append(f.get_serializer(child).serialize())
        return ''.join(texts)


class ImageBlockSerializer(Seralizer):
    def serialize(self) -> str:
        url_full = self.block.source
        resp = requests.get(url_full)
        if resp.status_code != 200:
            raise Exception(resp.text)
        img = Image.open(BytesIO(resp.content)) # type: Image.Image
        url_parsed = requests.utils.urlparse(url_full)
        file_name = os.path.basename(url_parsed.path)

        Path("images").mkdir(exist_ok=True)
        if os.path.exists("images/" + file_name):
            base, ext = os.path.splitext(file_name)
            file_name = "{}-{}{}".format(base, url_parsed.path.split('/')[-2], ext)
        img.save("images/" + file_name)
        return "![{}]({} \"{}\")\n".format(self.block.caption, "images/" + file_name, self.block.caption)
