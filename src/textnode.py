from htmlnode import LeafNode, HTMLNode

text_type_text = "text"
text_type_bold = "bold"
text_type_italic = "italic"
text_type_code = "code"
text_type_link = "link"
text_type_image = "image"

# Block types
block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_unordered_list = "unordered_list"
block_type_ordered_list = "ordered_list"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            self.text_type == other.text_type
            and self.text == other.text
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def text_node_to_html_node(text_node):
    if text_node.text_type == text_type_text:
        return HTMLNode(None, text_node.text)
    if text_node.text_type == text_type_bold:
        return HTMLNode("b", None, [HTMLNode(None, text_node.text)])
    if text_node.text_type == text_type_italic:
        return HTMLNode("i", None, [HTMLNode(None, text_node.text)])
    if text_node.text_type == text_type_code:
        return HTMLNode("code", None, [HTMLNode(None, text_node.text)])
    if text_node.text_type == text_type_link:
        return HTMLNode("a", None, [HTMLNode(None, text_node.text)], {"href": text_node.url})
    if text_node.text_type == text_type_image:
        return HTMLNode("img", "", props={"src": text_node.url, "alt": text_node.text})
    raise ValueError(f"Invalid text type: {text_node.text_type}")