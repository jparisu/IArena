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
                repetitions: int = 1,
            ):
        self._game_rules_generator = game_rules_generator
        self._player = player
        self._report_configurations = report_configurations

        self._reports : List[Report] = None
        self._inconsistent = False
        self._repetitions = repetitions


    def get_report_configurations(self) -> Iterator[ReportConfiguration]:
        """
        Get an iterator over the report configurations.
        """
        return iter(self._report_configurations)


    def get_reports_results(self) -> Iterator[ReportResult]:
        """
        Get an iterator over the report results.
        """
        if self._reports is None:
            raise RuntimeError("Grader has not been run yet. Please run the grader before getting the reports results.")

        for report in self._reports:
            yield report.get_result()


    def get_report_result_values(self) -> Iterator[float]:
        """
        Get an iterator over the report result values.
        """
        if self._reports is None:
            raise RuntimeError("Grader has not been run yet. Please run the grader before getting the reports result values.")

        for report in self._reports:
            yield report.calculate_grade()


    def total_value(self) -> float:
        """
        Calculate the total value of all reports.
        """
        return sum(report_configuration.value for report_configuration in self._report_configurations)


    def run(self, debug: int = 1) -> Dict[str, ReportResult]:

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

            if debug:
                print(f"  RUNNING: ", end="", flush=True)

            for _ in range(self._repetitions):
                report.run(debug)
                if debug:
                    print()

            self._reports.append(report)

            if debug:
                self.print_report_result(i, debug)
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

        for report, report_conf in zip(self._reports, self._report_configurations):
            report_score = report.calculate_grade()
            report_value = report_conf.value
            final_grade += (report_score * report_value) / total_value

        return final_grade


    def print_report_result(self, report_index: int, error_level: int = 1):
        if self._reports is None:
            raise RuntimeError("Grader has not been run yet. Please run the grader before printing the report result.")

        if report_index < 0 or report_index >= len(self._reports):
            raise IndexError("Report index out of range.")

        report = self._reports[report_index]
        report_configuration = self._report_configurations[report_index]

        total_value = self.total_value()
        this_report_value = report_configuration.value

        g = report.calculate_grade()
        print (f"  TEST VALUE: {(this_report_value/total_value)*100:.2f}% of total")
        print (f"  SCORE: {g*100}%  ->  + {g*this_report_value*100/total_value:.2f}% to total score")


        if error_level >= 0:
            print (f"  RUN DETAILS:")
            for e in report.get_result().errors:
                print(f"   ERROR: {e}")

        if error_level >= 1:
            for w in report.get_result().warnings:
                print(f"   WARNING: {w}")

        if error_level >= 2:
            for m in report.get_result().messages:
                print(f"   MESSAGE: {m}")

    def has_inconsistency(self) -> bool:
        return any(r.has_inconsistency() for r in self._reports)
