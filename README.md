# pyinstaller-excluder
Exclude unused packages for PyInstaller based on a requirements.txt file to decrease PyInstaller's generated file size.

## Known Limitations:

The script will try to find all depdendicies for the top level packages, but it may not be able to find packages that are relied on by other modules (which may have multiple options). For example: if you are using `pandas` to write to an Excel file in your script, and only mention `pandas` in your `requirements.txt` then you will be missing an import (which pandas has multiple alternatives for Excel Writers such as `openpyxl`) which will have to be imported manually into your `requirements.txt` file to provide all of the appropriate modules for your program to run after bundling it with PyInstaller.


## Usage:

```python3
import excluder

excluder.main('path_to_file/requirements.txt')
```
If no path is given for the spec_file_path then the script will try to look if there is a `.spec` file in the same directory as the `requirements.txt` file and will try to modify that existing `.spec` file with the list of excludes. Otherwise the script will print out the excludes for you to add to your own `.spec` file.
