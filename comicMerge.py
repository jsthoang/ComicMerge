import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import zipfile
import re
import argparse
import sys

# Function to wrap text into multiple lines
def wrap_text(text, draw, font, max_width):
    lines = []
    words = text.split()

    current_line = words[0]

    for word in words[1:]:
        test_line = current_line + " " + word
        test_width = draw.textbbox((0, 0), test_line, font=font)[2]

        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines

# Function to create a text image for each subfolder (chapter)
def create_text_image(chapter_name, output_path=None, size=(800, 1200), font_size=50, show_preview=False):
    width, height = size
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)

    # Use Monaco font (macOS default)
    font_path = "/System/Library/Fonts/Monaco.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback
        print("Warning: Monaco.ttf not found. Using default font.")

    # Padding and border
    border_padding = 30
    text_padding = 20
    max_width = width - 2 * (border_padding + text_padding)

    # Draw border
    draw.rectangle(
        [border_padding, border_padding, width - border_padding, height - border_padding],
        outline="black",
        width=3
    )

    # Wrap text
    lines = wrap_text(chapter_name, draw, font, max_width)

    # Calculate height of text block
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
    y_offset = (height - total_text_height) // 2  # Center vertically

    # Draw each line
    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x_offset = (width - line_width) // 2  # Center horizontally
        draw.text((x_offset, y_offset), line, font=font, fill="black")
        y_offset += draw.textbbox((0, 0), line, font=font)[3]

    # Show image preview if requested
    if show_preview:
        image.show()
    else:
        image.save(output_path)

# Function to naturally sort files correctly
def natural_sort_key(filename):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', filename)]

# Custom progress bar
def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

# Function to merge all subfolders into one without modifying the original folder
def merge_folders(big_folder_path, output_folder, font_size):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    subfolders = sorted(os.listdir(big_folder_path), key=natural_sort_key)
    total_subfolders = len(subfolders)
    page_number = 1

    # Iterate through subfolders with progress tracking
    for index, subfolder in enumerate(subfolders):
        subfolder_path = os.path.join(big_folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            # Generate chapter image
            chapter_image_path = os.path.join(output_folder, f"{page_number:05}_00_{subfolder}.png")
            create_text_image(subfolder, chapter_image_path, font_size=font_size)

            page_number += 1

            # Copy images
            images = sorted(os.listdir(subfolder_path), key=natural_sort_key)
            for img in images:
                src_img_path = os.path.join(subfolder_path, img)
                dst_img_path = os.path.join(output_folder, f"{page_number:05}_{img}")
                shutil.copyfile(src_img_path, dst_img_path)
                page_number += 1

        # Update progress bar
        print_progress_bar(index + 1, total_subfolders, prefix='Merging Folders', suffix='Complete')

# Function to create a CBZ file
def create_cbz(output_folder, cbz_path):
    with zipfile.ZipFile(cbz_path, 'w') as cbz:
        for foldername, _, filenames in os.walk(output_folder):
            for filename in sorted(filenames, key=natural_sort_key):
                filepath = os.path.join(foldername, filename)
                cbz.write(filepath, os.path.relpath(filepath, output_folder))

# Main function
def main():
    parser = argparse.ArgumentParser(description="Merge images into CBZ and add chapter title images.")
    parser.add_argument("-fz", "--font_size", type=int, default=50, help="Set custom font size for chapter title image.")
    parser.add_argument("-fn", "--file_name", type=str, help="Set custom CBZ filename.")
    parser.add_argument("-timg", "--test_image", type=str, help="Preview a text image without saving. -timg <test_text>")
    args = parser.parse_args()

    if args.test_image:
        print(f"Previewing image for text: {args.test_image}")
        create_text_image(args.test_image, show_preview=True, font_size=args.font_size)
        return

    # Get the folder path from the user input
    big_folder_path = input("Please enter the path to the big folder: ")

    if not os.path.exists(big_folder_path):
        print(f"Error: Folder {big_folder_path} does not exist.")
        return

    # Determine CBZ filename from the folder name
    default_cbz_name = os.path.basename(os.path.normpath(big_folder_path))
    cbz_filename = args.file_name if args.file_name else default_cbz_name + ".cbz"

    # Output folder
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(script_dir, default_cbz_name + "_merged_comic")
    cbz_file = os.path.join(script_dir, cbz_filename)

    # Merge folders and generate CBZ
    merge_folders(big_folder_path, output_folder, font_size=args.font_size)
    create_cbz(output_folder, cbz_file)

    # Print clickable output paths
    print(f"CBZ file created at: \033]8;;file://{cbz_file}\033\\{cbz_file}\033]8;;\033\\")
    print(f"Merged folder created at: \033]8;;file://{output_folder}\033\\{output_folder}\033]8;;\033\\")

if __name__ == "__main__":
    main()
