import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import zipfile
import re
import argparse

# Function to wrap text into multiple lines
def wrap_text(text, draw, font, max_width):
    lines = []
    words = text.split()

    # Start with the first word
    current_line = words[0]

    for word in words[1:]:
        # Add word to the current line and check the width
        test_line = current_line + " " + word
        test_width = draw.textbbox((0, 0), test_line, font=font)[2]

        # If the line is too wide, move to the next line
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word  # Start a new line with the current word

    lines.append(current_line)  # Add the last line

    return lines

# Function to create a text image for each subfolder (chapter)
def create_text_image(chapter_name, output_path, size=(800, 1200), font_size=50):
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)

    # Use Monaco font (macOS default)
    font_path = "/System/Library/Fonts/Monaco.ttf"  # Path for Monaco on macOS
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback to default if Monaco is not available
        print("Warning: Monaco.ttf not found. Using default font, which may not support Vietnamese.")

    # Maximum width for text in the image
    max_width = size[0] - 40  # Leave padding on the sides

    # Wrap text to fit within the image width
    lines = wrap_text(chapter_name, draw, font, max_width)

    # Calculate the height of the text block
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
    y_offset = (size[1] - total_text_height) // 2  # Vertically center the text

    # Draw each line
    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x_offset = (size[0] - line_width) // 2  # Horizontally center each line
        draw.text((x_offset, y_offset), line, font=font, fill="black")
        y_offset += draw.textbbox((0, 0), line, font=font)[3]  # Move down for the next line

    # Save the image
    image.save(output_path)

# Natural sorting function to sort files correctly
def natural_sort_key(filename):
    # Split the filename into parts: convert digits to integers and leave others as strings
    return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', filename)]

# Function to merge all subfolders into one without modifying the original folder
def merge_folders(big_folder_path, output_folder, font_size):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    subfolders = sorted(os.listdir(big_folder_path))
    page_number = 1

    for subfolder in subfolders:
        subfolder_path = os.path.join(big_folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            # Generate chapter image in a temporary location
            chapter_image_path = os.path.join(output_folder, f"{page_number:05}_00_{subfolder}.png")
            create_text_image(subfolder, chapter_image_path, font_size=font_size)

            page_number += 1  # Increment to account for the chapter image

            # Copy all images to the output folder in natural order without changing the original folder
            images = sorted(os.listdir(subfolder_path), key=natural_sort_key)
            for img in images:
                src_img_path = os.path.join(subfolder_path, img)
                dst_img_path = os.path.join(output_folder, f"{page_number:05}_{img}")
                shutil.copyfile(src_img_path, dst_img_path)
                page_number += 1

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
    args = parser.parse_args()

    # Display message about options
    print("Use -h to get other options.")

    # Get the folder path from the user input
    big_folder_path = input("Please enter the path to the big folder: ")

    if not os.path.exists(big_folder_path):
        print(f"Error: Folder {big_folder_path} does not exist.")
        return

    # Determine the default CBZ filename from the big folder name
    default_cbz_name = os.path.basename(os.path.normpath(big_folder_path))
    cbz_filename = args.file_name if args.file_name else default_cbz_name
    cbz_filename = cbz_filename + ".cbz"

    # Output folder and CBZ file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    default_output_folder_name = os.path.basename(os.path.normpath(big_folder_path))
    output_folder_name = args.file_name if args.file_name else default_output_folder_name
    output_folder = os.path.join(script_dir, output_folder_name +"_merged_comic")
    cbz_file = os.path.join(script_dir, cbz_filename)

    # Merge folders and generate CBZ
    merge_folders(big_folder_path, output_folder, font_size=args.font_size)
    create_cbz(output_folder, cbz_file)

    print(f"CBZ file created at {cbz_file}")
    print(f"Merged folder created at {output_folder}")

if __name__ == "__main__":
    main()
