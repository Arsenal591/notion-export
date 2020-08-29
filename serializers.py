from notion.block import *
from notion.collection import TableView, CollectionRowBlock, NotionDate
from notion.user import User as NotionUser

import requests


class Seralizer:
    def __init__(self, block: Block, **kwargs):
        self.block = block
        self.controller = kwargs['controller']  # type: Controller
        self.level = kwargs.get('level', 0)
        self.is_reference = kwargs.get('is_reference', False)

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
        for child in self.block.children:
            texts.append(self.controller.get_serializer(child, level=self.level + 1).serialize())
        return ''.join(texts)

class UnorderedListBlockSerializer(AbstractListBlockSerializer):
    mark = '-'

class NumberedListBlockSerializer(AbstractListBlockSerializer):
    mark = '1.'

class QuoteBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return '> {}\n'.format(self.block.title)

class DividerBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return '---\n'


# todo: add a state machine here, to add extra \n after listblock, quoteblock etc
class PageBlockSerializer(Seralizer):
    @staticmethod
    def is_list_block(block: Block):
        return type(block) in [BulletedListBlock, NumberedListBlock, TodoBlock]

    @staticmethod
    def is_normal_block(block: Block):
        return type(block) in [TextBlock, PageBlock]

    @staticmethod
    def should_insert_break_line(prev: Block, next: Block):
        if PageBlockSerializer.is_list_block(prev):
            return PageBlockSerializer.is_normal_block(next)
        return False

    def serialize(self) -> str:
        if self.is_reference:
            file_path = self.block.title + ".md"
            self.controller.worker.submit_job(self.block.id, self.controller._download_notion_page, self.block.id, file_path)
            return '[{}]({})\n'.format(self.block.title, file_path)
        else:
            texts = []
            for idx in range(len(self.block.children)):
                child = self.block.children[idx]
                texts.append(self.controller.get_serializer(child, is_reference=True).serialize())
                if idx < len(self.block.children) - 1:
                    if self.should_insert_break_line(child, self.block.children[idx + 1]):
                        texts.append('\n')
            return ''.join(texts)


    def write(self, path=None):
        if not path:
            path = self.block.title + ".md"
        with open(path, "w", encoding='utf-8') as f:
            f.write(self.serialize())


class ImageBlockSerializer(Seralizer):
    def serialize(self) -> str:
        url_full = self.block.source
        url_parsed = requests.utils.urlparse(url_full)
        base, ext = os.path.splitext(os.path.basename(url_parsed.path))
        if ext == '':  # when file name is '.png', ext is empty and '.png' is treated as base
            base, ext = ext, base

        file_name = "{}-{}{}".format(base, url_parsed.path.split('/')[-2], ext)
        file_path = "images/" + file_name

        self.controller.worker.submit_job(url_full, self.controller._download_s3_image, url_full, file_path)
        return "![{}]({} \"{}\")\n".format(self.block.caption, file_path, self.block.caption)


class TodoBlockSerializer(Seralizer):
    def serialize(self) -> str:
        if self.block.checked:
            return "- [x] ~~{}~~\n".format(self.block.title)
        else:
            return "- [ ] {}\n".format(self.block.title)


# todo: support inline table blocks here
class TableSerializer(Seralizer):
    def serializer_cell(self, item) -> str:
        if item is None:
            return ""
        if isinstance(item, list):
            return ",".join([self.serializer_cell(x) for x in item])
        if isinstance(item, Block):
            return item.title
        if isinstance(item, NotionUser):
            return item.full_name
        if isinstance(item, NotionDate):
            if item.end is not None:
                return "{} to {}".format(str(item.start), str(item.end))
            else:
                return str(item.start)
        if isinstance(item, bool):
            if item == True:
                return "√"
            else:
                return "×"
        return str(item)


    def serialize(self) -> str:
        block = self.block  # type: CollectionViewBlock
        schema = block.collection.get("schema")
        order = list(schema.keys())

        # If there is a table view, use that to determine columns' order
        for view in block.views:
            if isinstance(view, TableView):
                order = [x['property'] for x in view.get('format.table_properties') if x['property']  in schema]

        def format_row(row):
            return "| " + " | ".join(row) + " |\n"

        output = format_row([schema[key]['name'] for key in order])
        output += format_row(['---'] * len(order))
        for row in block.collection.get_rows():
            values = []
            for key in order:
                if schema.get(key)['type'] in ['created_by', 'last_edited_by']:  # To meet with Notion.so's API change.
                    user_id = row.get(schema.get(key)['type'] + '_id')
                    item = row._client.get_user(user_id)
                else:
                    if key == 'title':  # Use title plaintext
                        key = 'title_plaintext'
                    item = getattr(row, key)
                values.append(self.serializer_cell(item))
            output += format_row(values)
            
        return output


class CodeBlockSerializer(Seralizer):
    def serialize(self) -> str:
        return "```{}\n{}\n```\n".format(self.block.language, self.block.title)


class MediaBlockSerializer(Seralizer):
    def serialize(self) -> str:
        text = getattr(self.block, 'title', self.block._type)
        link = getattr(self.block, 'link', self.block.source)
        return "[{}]({})\n".format(text, link)
