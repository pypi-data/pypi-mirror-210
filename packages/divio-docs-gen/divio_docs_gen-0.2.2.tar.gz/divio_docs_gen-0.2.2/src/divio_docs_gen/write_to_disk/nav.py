
# Native imports
from glob import glob
from os.path import join
from pathlib import Path

# Local imports
from ..Args import args
from .utils import _markdown_link_from_filepath, _markdown_link_to_parent

"""Functions to generate navigation headers"""


def _create_nav_file(subdirectory: str, max_level: int, include_parent_nav = True, filename="README.md"):
    """Create a file purely for navigation in the passed subdirectory
    
    max_level: defines how many subdirectories the navigation will account for
    
    If include_parent_nav is True, adds a ../ link
    """
    base_path = args.docs_basedir + subdirectory
    files_to_link = glob(base_path + "/*" * max_level)
    with open(join(base_path, filename), "w", encoding="UTF-8") as file:
        if include_parent_nav:
            file.write(_markdown_link_from_filepath("../", "../"))
        for file_to_link in files_to_link:
            file_to_link = file_to_link.replace(base_path, "").lstrip("/")
            file.write(_markdown_link_from_filepath(file_to_link, file_to_link))

def _add_nav_header_to_file(filename: str, include_parent_nav = True):
    """Add a navigation header to the specified file. If include_parent_nav is True, adds a ../ link"""
    # Save previous content
    with open(filename, "r", encoding="UTF-8") as file:
        prev_content = file.read()
    # Replace content
    with open(filename, "w", encoding="UTF-8") as file:
        # Whether to add a navigation to the parent dir
        if include_parent_nav:
            file.write(_markdown_link_to_parent())

        filepath = Path(filename)
        siblings = list(filepath.parent.glob("*"))
        for sibling in siblings:
            if sibling.name == filepath.name:
                continue
            file.write(_markdown_link_from_filepath(sibling.name, sibling.name))

        file.write("\n")
        file.write(prev_content)


def _add_nav_header_to_files(filenames: list, include_parent_nav = True):
    """Iterative wrapper of _add_nav_header_to_file. If include_parent_nav is True, adds a ../ link"""
    for filename in filenames:
        _add_nav_header_to_file(filename, include_parent_nav)


def _generate_basedir_nav_file():
    """Creates a navigation file to the top/entrypoint of your documentation"""
    _create_nav_file("", 1, include_parent_nav=False)

def _generate_repo_nav_file(repo_name, include_parent_nav = True):
    """Create a navigation file for the specified repo. If include_parent_nav is True, adds a ../ link"""
    _create_nav_file(repo_name, 1, include_parent_nav)

def add_nav_to_all_repo_docs(include_parent_nav = True):
    """Adds nav headers to every generated .md file, generates repo nav files and a basedir file. If include_parent_nav is True, adds ../ links"""
    doc_files = glob(args.docs_basedir + "/**/*.md", recursive=True)
    _add_nav_header_to_files(doc_files, include_parent_nav)

    repos = glob(args.docs_basedir + "/*", recursive=False)
    for repo_name in [repo.replace(args.docs_basedir, "") for repo in repos]:
        _generate_repo_nav_file(repo_name, include_parent_nav)
    
    _generate_basedir_nav_file()

def generate_nav_as_needed():
    """Will generate nav if generate_nav is configured, otherwise does nothing"""
    if args.generate_nav:
        add_nav_to_all_repo_docs()