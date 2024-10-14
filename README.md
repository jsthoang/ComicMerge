
# Comic Merge

  

Merge multiple chapters, add chapter name at the beginning of each, and then generate cbz file.
# Require
[Python](https://www.python.org/downloads/)

[Pillow](https://pypi.org/project/pillow/)
# Output
The output will be:
- A folder contains all images from all chapters, sorting naturally. The first image of each chapter will be the name of itself.
- A .cbz file generate from that folder.
You can use [KCC](https://github.com/ciromattia/kcc) or [Calibre](https://calibre-ebook.com/download) to convert output folder/file into MOBI and other format
<img width="1500" alt="image" src="https://github.com/user-attachments/assets/487fc0ae-2ba7-4256-af3f-7c3ca6574c7b">


# Usage
- Download your favourite comic chapters to pc, im using Suwayomi. Each folder should contain all image of the chapter. Folder name should contain chapter's name and number.
- All chapters folder has to be in the same folder, this folder should be naming as the comic's name.
- Run with default setting: `python comicMerge.py`
- Enter the path to the Big_folder.
- Run with help: `python comicMerge.py -h`
- Options:
	- `-file_name | -fn` for custom output filename/folder name
	- `-font_size | -fz` for custom chapter name text font size
