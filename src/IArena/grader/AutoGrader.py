from typing import List, Dict, Tuple
import yaml
import os
import tempfile
import requests
import nbformat
import importlib
import copy

from IArena.interfaces.IPlayer import IPlayer
from IArena.grader.Grader import ReportConfiguration, Grader
from IArena.grader.Report import ReportCommonConfiguration
from IArena.grader.RulesGenerator import IRulesGenerator, RulesGeneratorSuite
from IArena.utils.importing import import_class_from_module, get_cell_from_ipynb, execute_str_as_module, extract_marker_values

TAG_YAML_CONF_GAME = "game"
TAG_YAML_CONF_DEFAULT = "default"
TAG_YAML_CONF_REPORTS = "reports"

TAG_PLAYER_VAR = "students_player"
TAG_AUTHOR = "@AUTHOR:"



def read_yaml(filename: str) -> Dict:
    """
    Read a YAML file and return its contents as a dictionary.

    If the filename is an url, it will be downloaded first.
    """

    if filename.startswith('http://') or filename.startswith('https://'):
        response = requests.get(filename)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml') as tmp_file:
            tmp_file.write(response.content)
            tmp_filename = tmp_file.name
        filename_to_read = tmp_filename
    else:
        filename_to_read = filename

    if not os.path.exists(filename_to_read):
        raise FileNotFoundError(f"File {filename_to_read} does not exist.")

    with open(filename_to_read, 'r') as file:
        try:
            data = yaml.safe_load(file)
            if isinstance(data, dict):
                return data
            else:
                raise ValueError(f"YAML content is not a dictionary in file {filename_to_read}.")
        except yaml.YAMLError as e:
            if filename.startswith('http://') or filename.startswith('https://'):
                os.remove(tmp_filename)
            raise ValueError(f"Error parsing YAML file {filename_to_read}: {e}")

    # If not error occurs, remove the temporary file if it was created
    if filename.startswith('http://') or filename.startswith('https://'):
                os.remove(tmp_filename)



PLAYER_CODE_MARKERS = [
    "CODE SOLUTION",
    "STUDENT CODE",
    "@AUTHOR",
]


def get_player_from_file(
            filename: str,
            player_var_name: str,
            markers: List[str] = PLAYER_CODE_MARKERS
        ) -> IPlayer:
    """
    Given a local python file name, reads and execute the code.

    If it is a .py file, it will be executed directly.
    If it is a .ipynb file, find the code cell that contains any of the markers, and execute its content.
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist.")

    code_text = ""

    if filename.endswith('.py'):
        with open(filename, 'r') as file:
            code_text = file.read()

    elif filename.endswith('.ipynb'):
        code_text = get_cell_from_ipynb(filename, markers)

    else:
        raise ValueError(f"Unsupported file extension for file {filename}. Only .py and .ipynb are supported.")

    # Execute the code as a module
    module = execute_str_as_module(code_text)

    # Get the player
    if not hasattr(module, player_var_name):
        raise ValueError(f"Variable {player_var_name} not found in file {filename}.")
    player = getattr(module, player_var_name)
    if not isinstance(player, IPlayer):
        raise ValueError(f"Variable {player_var_name} is not an instance of IPlayer in file {filename}.")
    return player



def read_authors_file(filename: str) -> List[str]:
    """
    Given a text file, look for the line containing the author tag and return the author(s).
    The author tag is defined as TAG_AUTHOR = "@AUTHOR", and the name is after a space after the occurrence of the tag.
    """

    return extract_marker_values(filename, TAG_AUTHOR)




def get_rules_generator_from_name(name: str) -> IRulesGenerator:
    """
    Given the name of a game, returns the generator corresponding class.

    The module should be located in the IArena.games package.
    The name of the package should be equal to the class name, and the class should be in CamelCase as:
        <name>RulesGenerator
    """

    try:
        rules_generator_class = import_class_from_module(f"IArena.games.{name}", f"{name}RulesGenerator")
        if not issubclass(rules_generator_class, IRulesGenerator):
            raise ValueError(f"Class {name}RulesGenerator is not a subclass of IRulesGenerator.")
        return rules_generator_class()

    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Could not find rules generator for game {name}: {e}")



def read_reports(default_config: ReportCommonConfiguration, test_config: Dict) -> List[ReportConfiguration]:

    if not TAG_YAML_CONF_REPORTS in test_config:
        raise ValueError(f"<{TAG_YAML_CONF_REPORTS}> must be specified in the configuration file.")

    reports = []

    # For each report, create a ReportConfiguration
    for i, report_yaml in enumerate(test_config[TAG_YAML_CONF_REPORTS]):
        if not isinstance(report_yaml, dict):
            raise ValueError(f"Report {i} is not a dictionary.")

        # Get name
        if "name" not in report_yaml:
            raise ValueError(f"Report {i} does not have a name.")
        name = report_yaml["name"]

        # Get the common configuration as the default updated with the report specific values
        common_configuration = copy.copy(default_config)
        common_configuration.update(report_yaml)

        # Get the rules suite
        args = {}
        multi_args = {}

        if "args" in report_yaml:
            if not isinstance(report_yaml["args"], dict):
                raise ValueError(f"Report {i} args is not a dictionary.")
            args = report_yaml["args"]
        if "multi_args" in report_yaml:
            if not isinstance(report_yaml["multi_args"], dict):
                raise ValueError(f"Report {i} multi_args is not a dictionary.")
            multi_args = report_yaml["multi_args"]
        rules_suite = RulesGeneratorSuite(args=args, multi_args=multi_args)

        # Get the value
        value = 1.0
        if "value" in report_yaml:
            try:
                value = float(report_yaml["value"])
            except Exception as e:
                raise ValueError(f"Report {i} value is not a float: {e}")
        if value < 0:
            raise ValueError(f"Report {i} value must be non-negative.")
        reports.append(ReportConfiguration(
            name=name,
            common_configuration=common_configuration,
            rules_suite=rules_suite,
            value=value
        ))

    return reports


class IndividualAutoGrader:
    """
    Class to read configurations file and player and generate a Grader for a student's player code.

    It reads a YAML configuration file.
    It prepares the game rules generator, the player instance, and the tests to be run.
    It runs the tests and collects the results.
    """


    def __init__(
            self,
            configuration_filename: str,
            player: IPlayer,
            authors: List[str] = []):

        ##############################
        # Read configuration from YAML

        self.yaml_configuration = read_yaml(configuration_filename)


        ##############################
        # Read students code

        self.student_player = player
        self.authors = authors


        ##############################
        # Prepare game rules

        # Get the games name
        if TAG_YAML_CONF_GAME in self.yaml_configuration:
            game_name = self.yaml_configuration[TAG_YAML_CONF_GAME]
        else:
            raise ValueError(f"<TAG_YAML_CONF_GAME> must be specified in the configuration file.")

        # Get the rules generator
        self.rules_generator = get_rules_generator_from_name(game_name)


        ##############################
        # Get default configuration
        self.default_config = ReportCommonConfiguration(self.yaml_configuration)


        ##############################
        # Create the Grader
        report_configurations = read_reports(self.default_config, self.yaml_configuration)

        self.grader = Grader(
            game_rules_generator=self.rules_generator,
            player=self.student_player,
            report_configurations=report_configurations
        )



    def grade(self, debug: bool = True) -> float:

        if debug:
            print(f"Grading player by authors: {self.authors}")
            print()

        self.grader.run(debug=debug)
        grade = self.grader.calculate_final_grade()

        if debug:
            print(f"Final grade: {grade * 100:.2f}%")
            print()

        return grade


    def authors(self) -> List[str]:
        return self.authors



class IndividualCompleteAutoGrader(IndividualAutoGrader):
    """
    Class to read configurations files and generate a Grader for a student's player code.

    It reads a YAML configuration file and a python file containing the student's code.
    It prepares the game rules generator, the player instance, and the tests to be run.
    It runs the tests and collects the results.
    """


    def __init__(
            self,
            configuration_filename: str,
            player_filename: str):

        ##############################
        # Read students code

        authors = read_authors_file(player_filename)
        student_player = get_player_from_file(player_filename, TAG_PLAYER_VAR)


        ##############################
        # Reuse the parent to read configuration and prepare the grader
        super().__init__(configuration_filename, student_player, authors)
