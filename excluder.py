import os
from typing import List, Set
import pkg_resources
from importlib.metadata import requires
from pathlib import Path

# https://stackoverflow.com/questions/4138851/recursive-looping-function-in-python
def collect_requirements(start: str) -> List[str]:
    """ negative depths means unlimited recursion """
    requirement_names: List[str] = []

    def package_name(original_name: str) -> str:
        return pkg_resources.working_set.by_key[original_name]

    # recursive function that collects all the names from upper package name
    def recurse(current: str) -> None:
        requirement_names.append(current)

        _package = package_name(current)
        if required_packages := _package.requires():
            for package in required_packages:
                recurse(package.name) # recursive call for each subrequirement

    recurse(start) # starts recursion
    return requirement_names

def write_to_spec(spec_file_path: str, exclude_packages_list: List[str]) -> None:
    spec_lines: List[str] = []
    with open(spec_file_path, 'r') as file:
        for line in file.readlines():
            if 'excludes=[],' in line:
                line = line.replace('excludes=[],', f'excludes={exclude_packages_list}')
                spec_lines.append(line)
            elif 'excludes=[' in line: # where a partial list already implemented --> append
                line = line.replace('],', f', {str(exclude_packages_list)[1:]},') # 1: to remove first list bracket as a string
                spec_lines.append(line)
            else:
                spec_lines.append(line)

    with open(spec_file_path, 'w') as file:
        file.writelines(spec_lines)

def main(file_path: str, spec_file_path: str = None) -> None:
    folder_path: str = file_path
    # see if requirements.txt file is in the folder path selected
    if not os.path.isfile(file_path):
        file_path = Path.joinpath(Path(file_path), 'requirements.txt')
        if not os.path.isfile(file_path):
            raise FileNotFoundError("requirements.txt was not found in the provided directory")
    else:
        folder_path = Path(file_path).parent

    REQUIRED_PACKAGES: Set[str] = {}
    with open(file_path, 'r') as file:
        REQUIRED_PACKAGES = {item.split('==')[0].lower() for item in file.readlines()}

    # get required package dependencies
    # https://stackoverflow.com/questions/29751572/how-to-find-a-python-packages-dependencies
    all_required_packages: List[str] = []
    for package in REQUIRED_PACKAGES:
        all_required_packages.extend(collect_requirements(package))

    all_required_packages_set: Set[str] = set(all_required_packages)

    # https://www.activestate.com/resources/quick-reads/how-to-list-installed-python-packages/
    all_installed_packages = pkg_resources.working_set
    all_installed_packages_set = set(sorted([i.key for i in all_installed_packages]))

    exclude_packages_list = list(all_installed_packages_set.difference(all_required_packages_set))

    # try to find the spec file in the folder with the requirements.txt file else print output
    available_spec: List[str] = [file for file in os.listdir(folder_path) if file.endswith('.spec')]
    if spec_file_path:
        write_to_spec(spec_file_path, exclude_packages_list)
    elif len(available_spec) == 1:
        print(f'Updating excludes in {available_spec[0]}')
        spec_path: str = Path.joinpath(Path(folder_path), available_spec[0])
        write_to_spec(spec_path, exclude_packages_list)
    else:
        print('Unable to add the list of excludes to a spec file')
        print('Add the below list to excludes in your spec file for PyInstaller: \n\n')
        print(f'excludes={exclude_packages_list}')


if __name__ == '__main__':
    main('./requirements.txt')
