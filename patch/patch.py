from notion.block import BLOCK_TYPES, TextBlock

from .maps import patched_property_map


class PatchedTextBlock(TextBlock):
    raw_data = patched_property_map("title")

BLOCK_TYPES['text'] = PatchedTextBlock
