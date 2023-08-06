# Native imports
from os import makedirs
from os.path import join, exists
from glob import glob
# Package imports
from git.repo import Repo as GitRepo

"""Repo utitilities for local file management"""

repos_dir = "repos/"
makedirs(repos_dir, exist_ok=True)

def clone_or_pull_repo(self) -> GitRepo:
    if not self.exists_locally:
        self.gitpython = GitRepo.clone_from(self.url, self.local_dir)
    else:
        self.gitpython = GitRepo(self.local_dir)
        self.gitpython.remotes[0].pull()
        

def _exists_locally(self) -> bool:
    """(Property)"""
    return exists(self.local_dir)
exists_locally = property(_exists_locally)

def _local_dir(self) -> str:
    """(Method) Returns path to local files for the repo"""
    # Follows GitHub zip file naming
    return f"{repos_dir}/{self.slug}"
local_dir = property(_local_dir)

def get_file(self, path) -> str:
    """(Method) Returns the path to a file, automatically prefixing the repos dir path if needed"""
    if path.startswith(self.local_dir):
        return path
    return join(self.local_dir, path)

def find_files(self, path):
    """(Method) Run a glob on the specified path within this repo"""
    return glob(self.get_file(path), recursive=True)

def _all_markdown_files(self):
    """(Property) Returns a list of all markdown files of the repo"""
    return self.find_files("**/*.md")
all_markdown_files = property(_all_markdown_files)

def get_file_contents(self, path):
    """(Method) Reads contents from specified file"""
    # If a relative path is given, append
    path = self.get_file(path)
    try:
        with open(path, "r", encoding="UTF-8") as file:
            data = file.read()
    except FileNotFoundError:
        raise FileNotFoundError
    return data
