# Native imports
from os import makedirs
from os.path import join


"""Generic helpers for write_to_disk"""

def _markdown_link_from_filepath(name, link):
    """Helper to create a markdown link"""
    link = link.replace(" ", "%20")
    return f"- [{name}]({link})\n"

def _join_paths_mkdir(path1, path2):
    """Join two paths and create the resulting directory if needed"""
    path = join(path1, path2)
    makedirs(path, exist_ok=True)
    return path


def _markdown_link_to_parent():
    """Create a markdown link that navigates to the parent"""
    return _markdown_link_from_filepath("../", "../")




