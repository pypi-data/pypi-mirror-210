from ..Section import sections

def get_section(self, section_id: str):
    return self.sections[section_id]

def add_to_section(self, section_id: str, filename="README.md", content: str=""):
    ignore = self.check_ignore_file(filename)
    if ignore:
        print("Ignoring " + filename) 
        return
    
    move = self.check_move_file(filename)
    if move:
        move_filename, move_dest = move.rsplit("/", 1)
        #move_filename = Path(move_filename).name # The selector can be a path, but only the filename should be kept for handling
        section_id = move_dest

    try:
        self.sections[section_id][filename] += content
    except KeyError:
        self.sections[section_id][filename] = content

def _setup_sections_dict() -> dict:
    new_dict = dict()
    for section_id in sections:
        new_dict[section_id] = dict()
    
    return new_dict