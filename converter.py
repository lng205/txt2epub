"""
TXT to EPUB Converter Module

This module is designed to convert a text (.txt) file into an EPUB format eBook. It includes functionalities for processing chapters, inserting images, and setting a cover image.

Features:
- Automatically detects and uses the first .txt file in the current directory.
- Splits the text into chapters based on a specified regular expression pattern.
- Replaces specified placeholders in the text with images from a given directory, in sequential order.
- Adds a series of images as the initial pages of the EPUB, typically used for front matter images.
- Automatically finds and sets a single image file (jpg, png, or jpeg) as the EPUB cover.

Usage:
1. Ensure a single .txt file and only one cover image file (jpg, png, or jpeg) are present in the current directory.
2. Place image files for placeholders and front matter in their respective 'images' and 'front_images' directories.
3. Run the script to generate an EPUB file named after the original .txt file with additional formatting and images.

Exceptions:
- Raises FileNotFoundError if a suitable cover image is not found.

Functions:
- main(): The main function of the script, orchestrating the EPUB creation process.
- find_cover_image(): Searches for a single cover image file in the current directory.
- split_into_chapters(text, pattern): Splits the given text into chapters based on the provided regex pattern.
- replace_placeholders_with_images(content, image_files): Replaces placeholders in the content with the specified images.

Author: lng205
"""


import re
import os
from ebooklib import epub
from glob import glob

# User-configurable variables
IMAGE_DIRECTORY = './images/'  # Path to the image directory
FRONT_IMAGE_DIRECTORY = './front_images/'  # Path to the front image directory
PLACEHOLDER_REGEX = '\n(（?插圖）?)\n'  # Regular expression pattern for Placeholder in the text file
CHAPTER_REGEX = r'\n\n(.*?[章話]　.*?)\n\n'  # Regular expression pattern for chapter titles

def main():
    txt_file = glob('*.txt')[0]
    cover_file = find_cover_image()

    # Create a new EPUB book
    book = epub.EpubBook()

    add_front_image(book)

    # Read text from a .txt file
    with open(txt_file, 'r', encoding="utf-8") as file:
        text = file.read()

    image_files = sorted(os.listdir(IMAGE_DIRECTORY))
    # Replace placeholders with images
    text = replace_placeholders_with_images(text, image_files)
    # Add your images to the EPUB
    for img_filename in image_files:
        book.add_item(epub.EpubItem(file_name=f'images/{img_filename}', media_type='image/jpeg', content=open(os.path.join(IMAGE_DIRECTORY, img_filename), 'rb').read()))


    # Regular expression pattern to match chapter titles
    chapter_pattern = re.compile(CHAPTER_REGEX)
    # Split text into chapters
    chapters = split_into_chapters(text, chapter_pattern)

    with open(cover_file, 'rb') as img:
        book.set_cover(cover_file, img.read())

    # Loop through chapters and add them to the EPUB
    for i, (chapter_title, chapter_content) in enumerate(chapters, start=1):
        c = epub.EpubHtml(title=chapter_title, file_name=f'chap_{i:02}.xhtml')
        c.content = f'<html><body><h1>{chapter_title}</h1><p>{chapter_content.replace("\n", "<br/>")}</p></body></html>'
        book.add_item(c)
        book.spine.append(c)
        book.toc.append(epub.Link(f'chap_{i:02}.xhtml', chapter_title, f'chap{i}'))

    # Add default NCX and Nav (required)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Save your book
    epub.write_epub(txt_file[:-4] + ".epub", book, {})


def find_cover_image():
    for extension in ["jpg", "png", "jpeg"]:
        found_files = glob(f"*.{extension}")
        if len(found_files) == 1:
            return found_files[0]
    raise FileNotFoundError


def add_front_image(book):
    front_image_files = sorted(os.listdir(FRONT_IMAGE_DIRECTORY))
    # Add front images to the book and create pages for them
    for i, img_filename in enumerate(front_image_files, start=1):
        img_path = os.path.join(FRONT_IMAGE_DIRECTORY, img_filename)
        book.add_item(epub.EpubItem(file_name=f'front_images/{img_filename}', media_type='image/jpeg', content=open(img_path, 'rb').read()))

        img_page = epub.EpubHtml(title=f'Front Image {i}', file_name=f'front_img_{i}.xhtml')
        img_page.content = f'<html><body><img src="front_images/{img_filename}" alt="Front Image {i}" style="max-width: 100%; height: auto;"/></body></html>'
        book.add_item(img_page)
        book.spine.insert(i-1, img_page)  # Insert the image page at the beginning of the spine


def split_into_chapters(text, pattern):
    chapters = []
    first_match = pattern.search(text)

    # Include the preface section
    preface_end = first_match.start() if first_match else len(text)
    preface_content = text[:preface_end].strip()
    chapters.append(("Preface", preface_content))

    for match in pattern.finditer(text):
        chapter_title = match.group(1).strip()
        print(f"Chapter found: {chapter_title}")
        end = match.end()
        next_match = next(pattern.finditer(text, end), None)
        start_next = next_match.start() if next_match else len(text)
        chapters.append((chapter_title, text[end:start_next].strip()))

    return chapters


# Function to replace placeholders with img tags
def replace_placeholders_with_images(content, image_files):
    placeholder_pattern = re.compile(PLACEHOLDER_REGEX)

    for img_filename in image_files:
        img_tag = f'\n<img src="images/{img_filename}" alt="{img_filename}"/>\n'
        
        # Replace one placeholder at a time
        content, count = placeholder_pattern.subn(img_tag, content, 1)

        print(f"Replacing placeholder with: {img_filename}")  # Debug print

        # If no replacements were made, break out of the loop
        if count == 0:
            break

    return content


if __name__ == "__main__":
    main()