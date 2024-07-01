import unittest
from inline_markdown import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node
)
from textnode import (
    TextNode,
    text_type_text,
    text_type_bold,
    text_type_italic,
    text_type_code,
    text_type_image,
    text_type_link,
    block_type_paragraph,
    block_type_heading,
    block_type_code,
    block_type_quote,
    block_type_unordered_list,
    block_type_ordered_list
)


class TestInlineMarkdown(unittest.TestCase):
    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", text_type_text)
        new_nodes = split_nodes_delimiter([node], "**", text_type_bold)
        self.assertListEqual(
            [
                TextNode("This is text with a ", text_type_text),
                TextNode("bolded", text_type_bold),
                TextNode(" word", text_type_text),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", text_type_text
        )
        new_nodes = split_nodes_delimiter([node], "**", text_type_bold)
        self.assertListEqual(
            [
                TextNode("This is text with a ", text_type_text),
                TextNode("bolded", text_type_bold),
                TextNode(" word and ", text_type_text),
                TextNode("another", text_type_bold),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", text_type_text
        )
        new_nodes = split_nodes_delimiter([node], "**", text_type_bold)
        self.assertListEqual(
            [
                TextNode("This is text with a ", text_type_text),
                TextNode("bolded word", text_type_bold),
                TextNode(" and ", text_type_text),
                TextNode("another", text_type_bold),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an *italic* word", text_type_text)
        new_nodes = split_nodes_delimiter([node], "*", text_type_italic)
        self.assertListEqual(
            [
                TextNode("This is text with an ", text_type_text),
                TextNode("italic", text_type_italic),
                TextNode(" word", text_type_text),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and *italic*", text_type_text)
        new_nodes = split_nodes_delimiter([node], "**", text_type_bold)
        new_nodes = split_nodes_delimiter(new_nodes, "*", text_type_italic)
        self.assertListEqual(
            [
                TextNode("bold", text_type_bold),
                TextNode(" and ", text_type_text),
                TextNode("italic", text_type_italic),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", text_type_text)
        new_nodes = split_nodes_delimiter([node], "`", text_type_code)
        self.assertListEqual(
            [
                TextNode("This is text with a ", text_type_text),
                TextNode("code block", text_type_code),
                TextNode(" word", text_type_text),
            ],
            new_nodes,
        )

    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://example.com/image.png) and ![another](https://example.com/another.jpg)"
        result = extract_markdown_images(text)
        expected = [
            ("image", "https://example.com/image.png"),
            ("another", "https://example.com/another.jpg")
        ]
        self.assertEqual(result, expected)

    def test_extract_markdown_images_no_images(self):
        text = "This is text with no images"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_extract_markdown_links(self):
        text = "This is text with a [link](https://example.com) and [another](https://example.com/page)"
        result = extract_markdown_links(text)
        expected = [
            ("link", "https://example.com"),
            ("another", "https://example.com/page")
        ]
        self.assertEqual(result, expected)

    def test_extract_markdown_links_no_links(self):
        text = "This is text with no links"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an ![image](https://example.com/image.png) and another ![second image](https://example.com/image2.png)",
            text_type_text,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", text_type_text),
                TextNode("image", text_type_image, "https://example.com/image.png"),
                TextNode(" and another ", text_type_text),
                TextNode("second image", text_type_image, "https://example.com/image2.png"),
            ],
            new_nodes,
        )

    def test_split_nodes_image_no_images(self):
        node = TextNode("This is text with no images", text_type_text)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and [another link](https://example.com/page)",
            text_type_text,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", text_type_text),
                TextNode("link", text_type_link, "https://example.com"),
                TextNode(" and ", text_type_text),
                TextNode("another link", text_type_link, "https://example.com/page"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_no_links(self):
        node = TextNode("This is text with no links", text_type_text)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    
    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        expected_nodes = [
            TextNode("This is ", text_type_text),
            TextNode("text", text_type_bold),
            TextNode(" with an ", text_type_text),
            TextNode("italic", text_type_italic),
            TextNode(" word and a ", text_type_text),
            TextNode("code block", text_type_code),
            TextNode(" and an ", text_type_text),
            TextNode("image", text_type_image, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and a ", text_type_text),
            TextNode("link", text_type_link, "https://boot.dev"),
            ]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected_nodes)

    def test_markdown_to_blocks(self):
        markdown = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items

"""
        expected_blocks = [
            "This is **bolded** paragraph",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            "* This is a list\n* with items"
        ]
        result = markdown_to_blocks(markdown)
        self.assertEqual(result, expected_blocks)

    def test_block_to_block_type(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), block_type_paragraph)
        self.assertEqual(block_to_block_type("# Heading"), block_type_heading)
        self.assertEqual(block_to_block_type("## Heading 2"), block_type_heading)
        self.assertEqual(block_to_block_type("```\ncode block\n```"), block_type_code)
        self.assertEqual(block_to_block_type("> Quote\n> Multiple lines"), block_type_quote)
        self.assertEqual(block_to_block_type("* Item 1\n* Item 2"), block_type_unordered_list)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), block_type_unordered_list)
        self.assertEqual(block_to_block_type("1. First\n2. Second"), block_type_ordered_list)


    def test_markdown_to_html_node(self):
        markdown = """
# Heading

This is a paragraph with **bold** and *italic* text.

* List item 1
* List item 2

1. Ordered item 1
2. Ordered item 2

> This is a quote

`This is code`

```
This is a code block
```
"""
        html_node = markdown_to_html_node(markdown)
        self.assertEqual(html_node.tag, "div")
        self.assertEqual(len(html_node.children), 7)  # 7 blocks in total
        
        self.assertEqual(html_node.children[0].tag, "h1")
        self.assertEqual(html_node.children[1].tag, "p")
        self.assertEqual(html_node.children[2].tag, "ul")
        self.assertEqual(html_node.children[3].tag, "ol")
        self.assertEqual(html_node.children[4].tag, "blockquote")
        self.assertEqual(html_node.children[5].tag, "p")
        self.assertEqual(html_node.children[6].tag, "pre")
        
        # Check specific content
        self.assertEqual(html_node.children[0].children[0].value, "Heading")
        self.assertEqual(len(html_node.children[2].children), 2)  # 2 list items
        self.assertEqual(len(html_node.children[3].children), 2)  # 2 ordered list items
        self.assertEqual(html_node.children[6].children[0].tag, "code")

if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
