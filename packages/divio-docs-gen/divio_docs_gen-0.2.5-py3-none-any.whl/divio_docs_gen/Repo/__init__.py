# Native imports
from pathlib import Path
from typing import List
# Package imports
from slugify import slugify
# Local imports
from .sections import _setup_sections_dict
from ..markdown_parser import split_sections_from_markdown
from ..write_to_disk import write_to_docs

"""Repo class: utilities to clone/pull the repoa nd access the files"""


class Repo():
    def __init__(self, url: str, parse_docs_on_init=True, write_to_disk_on_init=False, files_to_move: List[str] = [], files_to_ignore: List[str] = []) -> None:
        """Constructs a Repo class instance. This applies configuration, clones/pulls the repo, and optionally parses & outputs the docs"""
        self.url = url

        self.files_to_move = files_to_move
        self.files_to_ignore = files_to_ignore

        self.gitpython = self.clone_or_pull_repo()

        self.sections = _setup_sections_dict()

        if parse_docs_on_init:
            self.parse_docs()

        if write_to_disk_on_init:
            self.divio_to_disk()

        if write_to_disk_on_init and not parse_docs_on_init:
            print("write_to_disk is True but not parse_docs_on_init; output may be empty or incomplete")


    
    """GENERAL PROPERTIES"""
    @property
    def name(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[1].rsplit(".", maxsplit=1)[0]

    @property
    def slug(self) -> str:
        return slugify(self.url)

    """CONFIGURATIONS"""
    def check_ignore_file(self, filepath: str):
        return self._file_in_exceptions(self.files_to_ignore, filepath)
    
    def check_move_file(self, filepath: str):
        return self._file_in_exceptions(self.files_to_move, filepath)

    def _file_in_exceptions(self, exceptioned_files: list, filepath: str):
        """Check if an alternative action has to be taken for a file"""
        try:
            return next(filter(lambda exceptioned_file: exceptioned_file.rsplit("/", 1)[0] in filepath, exceptioned_files))
        except StopIteration:
            return False  # the file is not part of the exception could not be found, return False


    """PARSE & OUTPUT"""
    def _import_sections_from_markdown(self, input_path_or_string: str, output_filename="README.md"):
        parsed_file = split_sections_from_markdown(input_path_or_string)
        for section_id in parsed_file:
            self.add_to_section(section_id, output_filename, parsed_file[section_id])

    def parse_docs(self, write_to_disk=False):
        for file in self.all_markdown_files:
            path = Path(file)
            self._import_sections_from_markdown(path.absolute(), path.name)
        
        if write_to_disk:
            self.divio_to_disk()

    def divio_to_disk(self):
        for section_id in self.sections:
            section = self.get_section(section_id)
            
            for filename in section:
                write_to_docs(self.name, section_id, content=section[filename], filename=filename)

    from .files import clone_or_pull_repo, exists_locally, local_dir, all_markdown_files,  get_file, find_files, get_file_contents
    from .sections import add_to_section, get_section

