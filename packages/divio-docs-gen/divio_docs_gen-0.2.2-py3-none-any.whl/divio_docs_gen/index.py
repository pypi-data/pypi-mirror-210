# Native imports
from typing import List
# Local imports
from .Repo import Repo
from .write_to_disk import clear_docs, generate_nav_as_needed
from .Args import args

"""Entrypoint for the application"""

def _docs_from_configured_repos():
    """Generate docs from repos configured in Args"""
    for repoconfig in args.repos:
         files_to_move = repoconfig["files_to_move"] if "files_to_move" in repoconfig else []
         files_to_ignore = repoconfig["files_to_ignore"] if "files_to_ignore" in repoconfig else []
         Repo(repoconfig["url"], parse_docs_on_init=True, write_to_disk_on_init=args.write_to_disk, files_to_move=files_to_move, files_to_ignore=files_to_ignore)
    
    generate_nav_as_needed()


def docs_from_repo(git_url: str) -> Repo:
    """
    Generate documentation from the passed git url, optionally writing to disk.

    Returns a Repo object
    
    NOTE: This function does NOT automatically create nav files; make sure to run generate_nav_if_needed if desired
    """
    repo = Repo(git_url, parse_docs_on_init=True)
    return repo


def docs_from_repos(git_urls: List[str], write_to_disk=args.write_to_disk) -> List[Repo]:
    """
    Generate documentation from passed git urls, optionally writing to disk.
    Iterative wrapper for docs_from_repo

    Returns a Repo object
    
    NOTE: This function DOES automatically create nav files, if enabled in docs.conf or the passed args
    """
    repos = []
    for url in git_urls:
        repos.append(docs_from_repo(url, write_to_disk))

    generate_nav_as_needed()
    
def main():
    """When this package is run directly, clear any existing docs and generate new ones based on args"""
    clear_docs()
    _docs_from_configured_repos()

if __name__ == "__main__":
    main()
