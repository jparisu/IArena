from typing import List, Dict
import copy

from IArena.interfaces.IPlayer import IPlayer
from IArena.grader.Grader import ReportConfiguration, Grader
from IArena.grader.Report import ReportCommonConfiguration
from IArena.grader.RulesGenerator import IRulesGenerator, RulesGeneratorSuite, get_rules_generator_from_name
from IArena.utils.filing import read_yaml, get_vars_from_file, read_file_or_url

TAG_YAML_CONF_GAME = "game"
TAG_YAML_CONF_DEFAULT = "default"
TAG_YAML_CONF_REPORTS = "reports"

TAG_PLAYER_VAR = "PLAYER"
TAG_AUTHOR_VAR = "AUTHORS"

PLAYER_CODE_MARKERS = [
    "CODE SOLUTION",
    "STUDENT CODE",
    "AUTHORS",
    "PLAYER",
]


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

class AutoGrader:
    """
    Class to generate a Grader for a student's player code.

    It reads a YAML configuration file.
    It prepares the game rules generator, the player instance, and the tests to be run.
    It runs the tests and collects the results.
    """


    def __init__(
            self,
            yaml_configuration: Dict,
            player: IPlayer,
            authors: List[str] = [],
            repetitions: int = 1):

        ##############################
        # Read configuration from YAML

        self.yaml_configuration = yaml_configuration


        ##############################
        # Read students code

        self.student_player = player
        self.authors_ = authors
        self.repetitions = repetitions


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
            report_configurations=report_configurations,
            repetitions=self.repetitions
        )



    def grade(self, debug: int = 1) -> float:

        if debug:
            print(f"Grading player by authors: {self.authors_}")
            print()

        self.grader.run(debug=debug)

        grade = self.grader.calculate_final_grade()

        if debug:
            print(f"FINAL GRADE: {grade * 100:.2f}%")
            print()

        if self.grader.has_inconsistency() and debug:
            print("WARNING: Inconsistencies detected during grading due to non-deterministic player behavior.")

        return grade


    def authors(self) -> List[str]:
        return self.authors_

    def has_inconsistency(self) -> bool:
        return self.grader.has_inconsistency()


class IndividualAutoGrader(AutoGrader):
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
            authors: List[str] = [],
            repetitions: int = 1):

        ##############################
        # Read configuration from YAML
        yaml_configuration = read_yaml(read_file_or_url(configuration_filename))

        ##############################
        # Reuse the parent to read configuration and prepare the grader
        super().__init__(yaml_configuration, player, authors, repetitions)



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
            player_filename: str,
            repetitions: int = 1):

        ##############################
        # Read students code

        vars = get_vars_from_file(
            filename=player_filename,
            var_names=[TAG_AUTHOR_VAR, TAG_PLAYER_VAR],
            markers=PLAYER_CODE_MARKERS,
            types_allowed={TAG_AUTHOR_VAR: [list, str], TAG_PLAYER_VAR: [IPlayer]},
        )
        student_player = vars[TAG_PLAYER_VAR]
        authors = vars[TAG_AUTHOR_VAR]

        ##############################
        # Reuse the parent to read configuration and prepare the grader
        super().__init__(configuration_filename, student_player, authors, repetitions)
