# Notion-export

A program that exports your notion page as Markdown.

- Support almost all Notion blocks, including database blocks.
- Support all inline elements, especially math equations.
- Multi-threading image downloading, very useful when connecting directly in CN mainland.

This project is now work-in-progress.

# Usage

```
python3 export_to_markdown.py --token_v2={{Your notion.so's token}} --page={{URL or id of your page.}}
```

The config file is `config.py`, edit it to modify configuration.

# Related Projects
[Notion-py](https://github.com/jamalex/notion-py): We rely on this package to access Notion block data. Since more features are added to Notion after the package released, we make some patches to the it to meet with the latest API (in `patch`) folder. 

# TODO
- [ ] Ability to st the location where the markdown file will be saved.

- [ ] Fully support all markdown formats.

- [ ] Support table's formula row.
