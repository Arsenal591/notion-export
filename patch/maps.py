from inspect import signature

from notion.maps import field_map
from notion.markdown import markdown_to_notion

from .markdown import patched_notion_to_markdown


def patched_property_map(
    name, python_to_api=lambda x: x, api_to_python=lambda x: x, markdown=True
):
    """
    Similar to `field_map`, except it works specifically with the data under the "properties" field
    in the API's block table, and just takes a single name to specify which subkey to reference.
    Also, these properties all seem to use a special "embedded list" format that breaks the text
    up into a sequence of chunks and associated format metadata. If `markdown` is True, we convert
    this representation into commonmark-compatible markdown, and back again when saving.
    """

    def py2api(x, client=None):
        kwargs = {}
        if "client" in signature(python_to_api).parameters:
            kwargs["client"] = client
        x = python_to_api(x, **kwargs)
        if markdown:
            x = markdown_to_notion(x)
        return x

    def api2py(x, client=None):
        x = x or [[""]]
        if markdown:
            x = patched_notion_to_markdown(x, client=client)
        kwargs = {}
        if "client" in signature(api_to_python).parameters:
            kwargs["client"] = client
        return api_to_python(x, **kwargs)

    return field_map(["properties", name], python_to_api=py2api, api_to_python=api2py)
