from pathlib import Path
import jinja2
import pdfkit
from environment import environment
from reportmodel.template import Template
from typing import Callable

logger = environment.setup_logger()

class ReportGenerator:
    """Generates reports in PDF format."""

    def __init__(self, logo: Path = Path(), style: Path = Path(), template: Template = None) -> None:
        """
        Initialize the ReportGenerator object.

        Args:
            logo: The path to the logo file.
            style: The path to the CSS file.
            template: An optional Template object.

        """
        self._logo = logo
        self._style = style
        self._template = template
        self._formatters = []

    @property
    def formatters(self) -> list[Callable[[dict], dict]]:
        """
        Get the list of formatters.

        Returns:
            list: A list of formatter functions.

        """
        return self._formatters

    def add_formatter(self, formatter: Callable[[dict], dict]) -> None:
        """
        Add a formatter function to the list of formatters.

        Args:
            formatter: A function that takes a dictionary and returns a modified dictionary.

        """
        self._formatters.append(formatter)

    @property
    def template(self):
        """
        Get the template.

        Returns:
            Template: The template object.

        """
        return self._template

    @template.setter
    def template(self, template: Template) -> None:
        """
        Set the template.

        Args:
            template: A Template object.

        """
        self._template = template

    @template.setter
    def template(self, template_folder: Path, template_file: Path) -> None:
        """
        Set the template using the template folder and file paths.

        Args:
            template_folder: The path to the template folder.
            template_file: The path to the template file.

        """
        self._template = Template(template_folder=template_folder, template_file=template_file)

    def format(self, data: dict) -> dict:
        """
        Apply the registered formatters to the data.

        Args:
            data: The data dictionary.

        Returns:
            dict: The formatted data dictionary.

        """
        for formatter in self._formatters:
            data = formatter(data)
        return data

    def generate(self, data: dict, path: str):
        """
        Generate a PDF report for the given data.

        Args:
            data: The data dictionary.
            path: The path to save the generated PDF.

        Returns:
            str: An error message if an error occurred, otherwise None.

        """
        # Set up the Jinja2 environment
        template_loader = jinja2.FileSystemLoader(searchpath=str(self.template.template_folder.resolve()))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(str(self.template.template_file))

        # Generate the PDF
        try:
            data = self.format(data)
            output = template.render(
                **data,
                logo_path=str(self._logo.resolve()),
                style=str(self._style.resolve())
            )
            with open(f"{path}.html", "w") as html:
                html.write(output)
            # Save the HTML to a PDF
            pdfkit.from_string(
                output,
                path,
                options={"enable-local-file-access": ""},
            )
            return None
        except Exception as e:
            logger.error(e)
