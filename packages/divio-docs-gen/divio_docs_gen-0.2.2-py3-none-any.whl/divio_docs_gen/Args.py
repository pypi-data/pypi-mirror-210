# Native imports
from configparser import ConfigParser
from os import getcwd, path
from argparse import ArgumentParser

"""Code to handle configuration, through docs.conf or args"""

section_keys = ["tutorials", "how_to_guides", "explanation", "reference"]
class Args:
    def __init__(self) -> None:
        # store_true default is False, which means save_conf's output will be too verbose. Use None instead
        self.save_conf = None  
        self.write_to_disk = None
        self.docs_basedir = "docs/"
        self.generate_nav = None

        self.tutorials, self.how_to_guides, self.explanation, self.reference = section_keys

        self.repos = []
    
    def get_configured_section_name(self, section_id: str):
        # TODO look for a cleaner solution
        if section_id == section_keys[0]:
            return self.tutorials
        elif section_id == section_keys[1]:
            return self.how_to_guides
        elif section_id == section_keys[2]:
            return self.explanation
        elif section_id == section_keys[3]:
            return self.reference
        print(section_id)


    
    def __str__(self) -> str:
        return f"""
        Configured args:

        - save_conf: {self.save_conf} 
        - write_to_disk: {self.write_to_disk} 
        - docs_basedir: {self.docs_basedir} 
        - generate_nav: {self.generate_nav}

        - tutorials: {self.tutorials}
        - how_to_guides: {self.how_to_guides}
        - explanation: {self.explanation}
        - reference: {self.reference}

        - repos: {self.repos} 
        """

    def __repr__(self) -> str:
        return self.__str__()

args = Args()

""" Command-line args """
parser = ArgumentParser()

conf_sections = {
    "output": "Output Configuration", 
    "naming": "Naming Scheme", 
    "repos": "Repository Selection"
    }
ouptut_config = parser.add_argument_group(conf_sections["output"])
ouptut_config.add_argument("--save-conf",
                    dest="SaveConf",
                    help="When used, save the current command line options into ./docs.conf", 
                    action="store_true",
                    default=args.save_conf,  
                    )
ouptut_config.add_argument("--write-to-disk", "--write",
                           dest="WriteToDisk",
                           help="Whether to write the markdown to disk",
                           action="store_true",
                           default=args.write_to_disk,
                           )
ouptut_config.add_argument("--docs-base-dir", "--docs-dir", "--dir", "-d",
                    dest="DocsBasedir",
                    help=f"What folder to output the docs in. Defaults to `{args.docs_basedir}`", 
                    )
ouptut_config.add_argument("--generate-nav", "--nav",
                    dest="GenerateNav",
                    help="When used, add internal navigation to the top of each generated file", 
                    action="store_true",
                    default=args.generate_nav,
                    )
naming_scheme = parser.add_argument_group(conf_sections["naming"])
for section_key in section_keys:
    short_hand = section_key[0] if section_key[0] != "h" else "ht"
    naming_scheme.add_argument(f"--{section_key}", f"-{short_hand}", 
                        dest=section_key,
                        help=f"Sets the output folder name for {section_key}. Defaults to `{section_key}`"
                        )

repo_selection = parser.add_argument_group(conf_sections["repos"])
repo_selection.add_argument("--repo",
                            help="""
                            Configures if/how a repo should be parsed
                            This can be defined multiple times

                            Syntax: --repo git_url
                            Example: denperidge-redpencil/project move=docs/reference/documentation.md

                            If none are defined, all repos will be used.
                            Options:
                            - Move: Files in the repository that should be copied to a specific section. Syntax: move=file.md/sectionname///file2.md/sectionname
                            - Ignore: Files in the repository that should be ignored. Syntax: ignore=file.md//file2.md
                            """,
                            action="append",
                            dest="repos",
                            nargs="*")

cli_args = parser.parse_args()
args.save_conf = bool(getattr(cli_args, "SaveConf")) if hasattr(cli_args, "SaveConf") else False

""" Conf file """
conf_file = path.join(getcwd(), "docs.conf")
use_conf = path.exists(conf_file)
if use_conf or args.save_conf:
    conf = ConfigParser()
    if use_conf:
        conf.read("docs.conf")
    
    for section_key in conf_sections:
        section = conf_sections[section_key]
        if section not in conf:
            conf.add_section(section)


""" Get config, save if desired, apply"""
def get_conf_value(section_id, value_id):
    return conf[section_id][value_id] if value_id in conf[section_id] else None

def get_cli_arg_value(value_id):
    return getattr(cli_args, value_id) if hasattr(cli_args, value_id) else None

def get_value(section_id, value_id, default):
    """Gets the arg, whether it be from the config file or CLI"""
    # Get the value from cli if defined. Cli > conf
    value = get_cli_arg_value(value_id)
    # If it's undefined in the CLI, check if conf can be used
    if value is None and use_conf:
        value = get_conf_value(section_id, value_id)
    if value is None:
        value = default

    if args.save_conf:
        # If it should be saved, do that
        conf[section_id][value_id] = str(value)
        
    return value

args.write_to_disk = bool(get_value(conf_sections["output"], "WriteToDisk", False))
args.generate_nav = bool(get_value(conf_sections["output"], "GenerateNav", False))
args.docs_basedir = get_value(conf_sections["output"], "DocsBasedir", "docs/")

for i, section_name in enumerate(["tutorials", "how_to_guides", "explanation", "reference"]):
    # TODO cleaner solution
    value = get_value(conf_sections["naming"], value_id=section_name, default=section_name)
    if i == 0:
        args.tutorials = value
    elif i == 1:
        args.how_to_guides = value
    elif i == 2:
        args.explanation = value
    elif i == 3:
        args.reference = value


if get_cli_arg_value("repos"):
    for repo_arg in get_cli_arg_value("repos"):
        repo_config = dict()
        repo_config.url = repo_arg[0]
        for arg in repo_arg[1:]:
            key, value = arg.split("=", 1)
            key = key.lower()
            if "ignore" in key:
                repo_config["files_to_ignore"] = value.split("//")
            elif "move" in key:
                repo_config["files_to_move"] = value.split("//") 

        args.repos.append(repo_config)
        conf[repo_config["url"]] = repo_config
    
if use_conf:
    all_conf_sections = conf.sections()
    for conf_section_id in all_conf_sections:
        if conf_section_id in conf_sections.values(): continue

        conf_section = conf[conf_section_id]
        raw_data = dict(conf_section)
        repo_config = dict()
        repo_config["url"] = raw_data["url"]
        
        if "ignore" in raw_data:
            repo_config["files_to_ignore"] = raw_data["ignore"].split("//")
        if "move" in raw_data:
            repo_config["files_to_move"] = raw_data["move"].split("//")

        if repo_config not in args.repos:
            args.repos.append(repo_config)
        

if args.save_conf:
    with open("docs.conf", mode="w", encoding="UTF-8") as configfile:
        conf.write(configfile)

print(args)