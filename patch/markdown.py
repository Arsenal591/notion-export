import re

from notion.markdown import FORMAT_PRECEDENCE, _NOTION_TO_MARKDOWN_MAPPER, delimiters


def patched_notion_to_markdown(notion):

    markdown_chunks = []

    use_underscores = True

    for item in notion or []:

        markdown = ""

        text = item[0]
        format = item[1] if len(item) == 2 else []

        match = re.match(
            "^(?P<leading>\s*)(?P<stripped>(\s|.)*?)(?P<trailing>\s*)$", text
        )
        if not match:
            raise Exception("Unable to extract text from: %r" % text)

        leading_whitespace = match.groupdict()["leading"]
        stripped = match.groupdict()["stripped"]
        trailing_whitespace = match.groupdict()["trailing"]

        markdown += leading_whitespace

        sorted_format = sorted(
            format,
            key=lambda x: FORMAT_PRECEDENCE.index(x[0])
            if x[0] in FORMAT_PRECEDENCE
            else -1,
        )

        is_equation = False
        for f in sorted_format:
            if f[0] in _NOTION_TO_MARKDOWN_MAPPER:
                if stripped:
                    markdown += _NOTION_TO_MARKDOWN_MAPPER[f[0]]
            if f[0] == "a":
                markdown += "["
            if f[0] == "e":
                is_equation = True
                markdown += "$$"

        if not is_equation:
            markdown += stripped

        for f in reversed(sorted_format):
            if f[0] in _NOTION_TO_MARKDOWN_MAPPER:
                if stripped:
                    markdown += _NOTION_TO_MARKDOWN_MAPPER[f[0]]
            if f[0] == "a":
                markdown += "]({})".format(f[1])
            if f[0] == "e":
                markdown += "{}$$".format(f[1])

        markdown += trailing_whitespace

        # to make it parseable, add a space after if it combines code/links and emphasis formatting
        format_types = [f[0] for f in format]
        if (
            ("c" in format_types or "a" in format_types)
            and ("b" in format_types or "i" in format_types)
            and not trailing_whitespace
        ):
            markdown += " "

        markdown_chunks.append(markdown)

    # use underscores as needed to separate adjacent chunks to avoid ambiguous runs of asterisks
    full_markdown = ""
    last_used_underscores = False
    for i in range(len(markdown_chunks)):
        prev = markdown_chunks[i - 1] if i > 0 else ""
        curr = markdown_chunks[i]
        next = markdown_chunks[i + 1] if i < len(markdown_chunks) - 1 else ""
        prev_ended_in_delimiter = not prev or prev[-1] in delimiters
        next_starts_with_delimiter = not next or next[0] in delimiters
        if (
            prev_ended_in_delimiter
            and next_starts_with_delimiter
            and not last_used_underscores
            and curr.startswith("☃")
            and curr.endswith("☃")
        ):
            if curr[1] == "☃":
                count = 2
            else:
                count = 1
            curr = "_" * count + curr[count:-count] + "_" * count
            last_used_underscores = True
        else:
            last_used_underscores = False

        final_markdown = curr.replace("☃", "*")

        # to make it parseable, convert emphasis/strong combinations to use a mix of _ and *
        if "***" in final_markdown:
            final_markdown = final_markdown.replace("***", "**_", 1)
            final_markdown = final_markdown.replace("***", "_**", 1)

        full_markdown += final_markdown

    return full_markdown
