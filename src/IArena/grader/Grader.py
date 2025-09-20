from typing import Iterator, List, Dict
from dataclasses import dataclass

from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.arena.GenericGame import ClockGame
from IArena.grader.RulesGenerator import IRulesGenerator, RulesGeneratorSuite
from IArena.grader.Report import Report, ReportCommonConfiguration, ReportResult
from IArena.utils.printing import green_tick, red_cross


@dataclass
class ReportConfiguration:
    """
    Configuration for a report, including name, value along other reports, and the required report configurations.
    """

    name: str
    common_configuration: ReportCommonConfiguration
    rules_suite: RulesGeneratorSuite
    value: float = 1



class Grader:

    """
    Class that represents a group of reports for the same game and player.
    It runs multiple reports and collects the overall results.
    """

    def __init__(
                self,
                game_rules_generator: IRulesGenerator,
                player: IPlayer,
                report_configurations: List[ReportConfiguration],
            ):
        self._game_rules_generator = game_rules_generator
        self._player = player
        self._report_configurations = report_configurations

        self._reports : List[Report] = None


    def total_value(self) -> float:
        """
        Calculate the total value of all reports.
        """
        return sum(report_configuration.value for report_configuration in self._report_configurations)


    def run(self, debug: bool = False) -> Dict[str, ReportResult]:

        self._reports = []


        for i, report_configuration in enumerate(self._report_configurations):

            if debug:
                print(f"Running report {i+1}/{len(self._report_configurations)}: {report_configuration.name} ...")

            report = Report(
                rules_generator=self._game_rules_generator,
                player=self._player,
                common_configuration=report_configuration.common_configuration,
                rules_suite=report_configuration.rules_suite,
            )

            report.run()

            self._reports.append(report)

            if debug:
                self.print_report_result(i)
                print()



    def calculate_final_grade(self) -> float:
        """
        Calculate final grade of all reports.

        Each report calculates its own score based on its configuration and results.
        Depending on each report value, the final grade is calculated as a weighted average of the individual report scores.
        """
        if self._reports is None:
            raise RuntimeError("Grader has not been run yet. Please run the grader before calculating the final grade.")

        total_value = self.total_value()
        final_grade = 0.0

        for report in self._reports:
            report_score = report.calculate_score()
            report_value = self._report_configurations[report.name].value
            final_grade += (report_score * report_value) / total_value

        return final_grade


    def print_report_result(self, report_index: int):
        if self._reports is None:
            raise RuntimeError("Grader has not been run yet. Please run the grader before printing the report result.")

        if report_index < 0 or report_index >= len(self._reports):
            raise IndexError("Report index out of range.")

        report = self._reports[report_index]
        report_configuration = self._report_configurations[report_index]

        total_value = self.total_value()
        this_report_value = report_configuration.value

        print(f"RESULT: [{report_configuration.name}] ({this_report_value}/{total_value}) -> ", end="")

        for s in report.get_result().successes:
            # Use small green check and small red cross
            if s:
                print(green_tick(), end="")  # green small check
            else:
                print(red_cross(), end="")  # red small cross

        print (f"   SCORE: {report.calculate_grade()*100}%")
