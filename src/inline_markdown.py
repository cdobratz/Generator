import re
from htmlnode import HTMLNode
from textnode import (
    TextNode,
    text_node_to_html_node,
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


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], text_type_text))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes



def extract_markdown_images(text):
    pattern = r"!\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue
        
        images = extract_markdown_images(old_node.text)
        if not images:
            new_nodes.append(old_node)
            continue
        
        remaining_text = old_node.text
        for alt_text, url in images:
            parts = remaining_text.split(f"![{alt_text}]({url})", 1)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], text_type_text))
            new_nodes.append(TextNode(alt_text, text_type_image, url))
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, text_type_text))
    
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue
        
        links = extract_markdown_links(old_node.text)
        if not links:
            new_nodes.append(old_node)
            continue
        
        remaining_text = old_node.text
        for text, url in links:
            parts = remaining_text.split(f"[{text}]({url})", 1)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], text_type_text))
            new_nodes.append(TextNode(text, text_type_link, url))
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, text_type_text))
    
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, text_type_text)]
    nodes = split_nodes_delimiter(nodes, "**", text_type_bold)
    nodes = split_nodes_delimiter(nodes, "*", text_type_italic)
    nodes = split_nodes_delimiter(nodes, "`", text_type_code)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return [text_node_to_html_node(node) for node in nodes]

def paragraph_to_html_node(block):
    html_nodes = text_to_textnodes(block)
    return HTMLNode("p", None, html_nodes)

def heading_to_html_node(block):
    level = len(block.split()[0])  # Count the number of '#' characters
    text = block.lstrip('#').strip()
    html_nodes = text_to_textnodes(text)
    return HTMLNode(f"h{level}", None, html_nodes)

def code_to_html_node(block):
    code_content = block.strip('`').strip()
    return HTMLNode("pre", None, [HTMLNode("code", None, [code_content])])

def quote_to_html_node(block):
    lines = [line.lstrip('>').strip() for line in block.split('\n')]
    inner_block = '\n'.join(lines)
    inner_html = paragraph_to_html_node(inner_block)
    return HTMLNode("blockquote", None, [inner_html])

def unordered_list_to_html_node(block):
    items = [line.lstrip('*-').strip() for line in block.split('\n')]
    html_items = [
        HTMLNode("li", None, text_to_textnodes(item))
        for item in items
    ]
    return HTMLNode("ul", None, html_items)

def ordered_list_to_html_node(block):
    items = [line.split('.', 1)[1].strip() for line in block.split('\n')]
    html_items = [
        HTMLNode("li", None, text_to_textnodes(item))
        for item in items
    ]
    return HTMLNode("ol", None, html_items)

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == block_type_paragraph:
            html_nodes.append(paragraph_to_html_node(block))
        elif block_type == block_type_heading:
            html_nodes.append(heading_to_html_node(block))
        elif block_type == block_type_code:
            html_nodes.append(code_to_html_node(block))
        elif block_type == block_type_quote:
            html_nodes.append(quote_to_html_node(block))
        elif block_type == block_type_unordered_list:
            html_nodes.append(unordered_list_to_html_node(block))
        elif block_type == block_type_ordered_list:
            html_nodes.append(ordered_list_to_html_node(block))
    return HTMLNode("div", None, html_nodes)

def markdown_to_blocks(markdown):
    # Split the markdown into blocks based on one or more blank lines
    blocks = re.split(r'\n\s*\n', markdown)
    
    # Strip leading and trailing whitespace from each block and filter out empty blocks
    blocks = [block.strip() for block in blocks if block.strip()]
    
    return blocks

def block_to_block_type(block):
    # Check for heading
    if re.match(r'^#{1,6}\s', block):
        return block_type_heading
    
    # Check for code block
    if block.startswith('```') and block.endswith('```'):
        return block_type_code
    
    # Check for quote block
    if all(line.strip().startswith('>') for line in block.split('\n')):
        return block_type_quote
    
    # Check for unordered list
    if all(line.strip().startswith(('*', '-')) for line in block.split('\n')):
        return block_type_unordered_list
    
    # Check for ordered list
    lines = block.split('\n')
    if all(re.match(r'^\d+\.\s', line.strip()) for line in lines):
        numbers = [int(line.split('.')[0]) for line in lines]
        if numbers == list(range(1, len(numbers) + 1)):
            return block_type_ordered_list
    
    # If none of the above conditions are met, it's a paragraph
    return block_type_paragraph