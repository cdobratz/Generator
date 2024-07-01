import os
import shutil
import logging
from pathlib import Path
from inline_markdown import markdown_to_html_node

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def copy_directory(src, dest):
    if not os.path.exists(src):
        logging.warning(f"Source directory does not exist: {src}")
        return

    if not os.path.exists(dest):
        os.mkdir(dest)
        logging.info(f"Created directory: {dest}")
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
            logging.info(f"Copied file: {s} to {d}")
        elif os.path.isdir(s):
            copy_directory(s, d)

def extract_title(markdown):
    """
    Extract the title (h1) from a markdown string.
    Raises an exception if no h1 is found.
    """
    lines = markdown.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    raise ValueError("No h1 header found in the markdown file")

def generate_page(from_path, template_path, dest_path):
    """
    Generate an HTML page from a markdown file and a template.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r') as file:
        markdown_content = file.read()
    
    # Read the template file
    with open(template_path, 'r') as file:
        template_content = file.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)
    
    # Replace placeholders in the template
    final_html = template_content.replace('{{ Title }}', title).replace('{{ Content }}', html_content)
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write the final HTML to the destination file
    with open(dest_path, 'w') as file:
        file.write(final_html)
    
    logging.info(f"Generated page: {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for entry in os.listdir(dir_path_content):
        entry_path = os.path.join(dir_path_content, entry)
        if os.path.isfile(entry_path) and entry.endswith('.md'):
            # Generate HTML file name
            rel_path = os.path.relpath(entry_path, dir_path_content)
            dest_file = os.path.join(dest_dir_path, Path(rel_path).with_suffix('.html'))
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            
            # Generate the page
            generate_page(entry_path, template_path, dest_file)
            logging.info(f"Generated page: {dest_file}")
        elif os.path.isdir(entry_path):
            # Recursively process subdirectories
            sub_dest_dir = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(entry_path, template_path, sub_dest_dir)

def main():
    src_dir = "src/static"
    dest_dir = "src/public"
    template_path = "template.html"
    content_dir = "content"

    # Remove existing public directory if it exists
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
        logging.info(f"Removed existing directory: {dest_dir}")

    # Ensure public directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Copy static files to public directory if static directory exists
    if os.path.exists(src_dir):
        copy_directory(src_dir, dest_dir)
        logging.info("Static files copied.")
    else:
        logging.warning(f"Static directory not found: {src_dir}")

    # Generate pages recursively
    generate_pages_recursive(content_dir, template_path, dest_dir)

    logging.info("Static site generation complete.")

if __name__ == "__main__":
    main()
