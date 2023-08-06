from dataclasses import dataclass
from pathlib import Path


@dataclass
class Template:
    template_folder: Path
    template_file: Path
