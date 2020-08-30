from io import BytesIO
import os
from pathlib import Path

from notion.client import NotionClient
from notion.block import *
from PIL import Image
import requests

from patch import PatchedTextBlock
from serializers import *
from worker import JobWorker

class Controller:
    def __init__(self, token_v2: str):
        self.worker = JobWorker()
        self.notion_cli = NotionClient(token_v2=token_v2)
        self.token_v2 = token_v2

    def _download_s3_image(self, url, path):
        resp = requests.get(url, cookies={'token_v2': self.token_v2})
        if resp.status_code != 200:
            raise Exception(resp.text)
        img = Image.open(BytesIO(resp.content))  # type: Image.Image
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        img.save(path)

    def _download_notion_page(self, id, path):
        page = self.notion_cli.get_block(id)
        self.get_serializer(page).write(path=path)

    def get_serializer(self, block: BasicBlock, **kwargs):
        serializer_class = {
            PatchedTextBlock: TextSerializer,
            HeaderBlock: HeaderBlockSerializer,
            SubheaderBlock: SubheaderBlockSerializer,
            SubsubheaderBlock: SubsubheaderBlockSerializer,
            BulletedListBlock: UnorderedListBlockSerializer,
            NumberedListBlock: NumberedListBlockSerializer,
            QuoteBlock: QuoteBlockSerializer,
            CalloutBlock: QuoteBlockSerializer,
            DividerBlock: DividerBlockSerializer,
            PageBlock: PageBlockSerializer,
            ImageBlock: ImageBlockSerializer,
            ToggleBlock: UnorderedListBlockSerializer,
            TodoBlock: TodoBlockSerializer,
            CollectionViewBlock: TableSerializer,
            CodeBlock: CodeBlockSerializer,
            BookmarkBlock: MediaBlockSerializer,
            EmbedOrUploadBlock: MediaBlockSerializer,
            VideoBlock: MediaBlockSerializer,
            FileBlock: MediaBlockSerializer,
            AudioBlock: MediaBlockSerializer,
            PDFBlock: MediaBlockSerializer,
        }[type(block)]
        return serializer_class(block, controller=self, **kwargs)
