# Native imports
from os.path import exists, join
from shutil import rmtree
from typing import Union

# Local imports
from .utils import _join_paths_mkdir
from ..Args import args
from ..Section import Section
from .nav import generate_nav_as_needed  # Import for export

"""Functions to assist in writing docs to disk"""


def clear_docs():
    """Removes previously generated docs"""
    if exists(args.docs_basedir):
        rmtree(args.docs_basedir)

def _make_and_get_repodir(repo_name):
    """Create a directory for the repository in the docs basedir"""
    return _join_paths_mkdir(args.docs_basedir, repo_name)
   
def _make_and_get_sectiondir(repo_name, section: Union[str,Section]):
    """Create a directory for the section in the repository's folder"""
    if isinstance(section, Section):
        section = section.name
    
    return _join_paths_mkdir(_make_and_get_repodir(repo_name), section)


def write_to_docs(repo_name: str, section_id: str, content: str, filename="README.md", replaceContent=False, prepend=False) -> str:
    """Add CONTENT to the generated documentation. Optionally creates the needed directories, replaces contents..."""
    section_dirname = args.get_configured_section_name(section_id)

    dir = _make_and_get_sectiondir(repo_name, section_dirname)
    full_filename = join(dir, filename)
    mode = "a+" if (not replaceContent) and (not prepend) else "w"

    if prepend:
        with open(full_filename, "r", encoding="UTF-8") as file:
            original_data = file.read(content)

    with open(full_filename, mode, encoding="UTF-8") as file:
        file.write(content)
        if prepend:
            file.write(original_data)
    
    # Return without 
    return full_filename


