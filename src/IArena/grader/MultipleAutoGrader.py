from typing import List, Dict
import copy
from __future__ import annotations

from IArena.interfaces.IPlayer import IPlayer
from IArena.grader.Grader import ReportConfiguration, Grader
from IArena.grader.Report import ReportCommonConfiguration
from IArena.grader.RulesGenerator import IRulesGenerator, RulesGeneratorSuite, get_rules_generator_from_name
from IArena.grader.AutoGrader import IndividualCompleteAutoGrader
from IArena.utils.filing import read_yaml, get_vars_from_file, read_file_or_url, download_tmp_file
from IArena.utils.ziping import unzip_get_files


class MultipleAutoGrader:
    """
    Class to read configurations files and generate Graders for multiple student's player codes.

    It uses IndividualCompleteAutoGraders to grade each player's code.
    """

    def __init__(
            self,
            configuration_filename: str,
            player_filenames: List[str]):

        self.autograders = {}  # player_filename -> IndividualCompleteAutoGrader
        self.results = {}  # player_filename -> grade (float)

        # If configuration is URL, download it once
        if configuration_filename.startswith('http'):
            configuration_filename = download_tmp_file(configuration_filename)

        for player_filename in player_filenames:
            autograder = IndividualCompleteAutoGrader(
                configuration_filename=configuration_filename,
                player_filename=player_filename
            )
            self.graders[player_filename] = autograder


    def grade_all(self, debug: bool = True) -> Dict[str, float]:

        for player_filename, autograder in self.autograders.items():
            if debug:
                print(f"Grading player file: {player_filename}")
            grade = autograder.grade(debug=debug)
            self.results[player_filename] = grade

        return self.results


    def prepare_result_table(self) -> List[List[str]]:
        """
        Prepare a table with the results.
        """

        if not self.result:
            raise ValueError("No results available. Please run grade_all() first.")

        ###
        # PREPARE TABLE STRUCTURE
        headers = ["PlayerFile", "Author1", "Author2", "Grade"]

        # Get the list of report configurations for the first autograder
        confs = self.autograders[self.autograders.keys()[0]].grader.get_report_configurations()

        for conf in confs:
            headers.append(conf.name + " (" + str(conf.value) + ")")


        ###
        # PREPARE TABLE RESULTS
        table = []

        for player_filename, autograder in self.autograders.items():
            row = [player_filename]

            # Authors
            authors = autograder.authors

            if len(authors) == 0:
                print("Warning: No authors found for player file:", player_filename)
                row.append("")
                row.append("")
            elif len(authors) == 1:
                row.append(authors[0])
                row.append("")
            elif len(authors) == 2:
                row.append(authors[0])
                row.append(authors[1])
            else:
                row.append(authors[0])
                row.append(authors[1])
                print("Warning: More than 2 authors found for player file:", player_filename)

            # Grade
            grade = self.results[player_filename]
            row.append(str(grade))

            # Report results
            for result in autograder.grader.get_report_result_values():
                row.append(str(result))

            table.append(row)

        ###
        # JOIN TABLES
        table.insert(0, headers)
        return table


    def prepare_csv(self) -> str:
        """
        Prepare a CSV string with the results.
        """

        if not self.result:
            raise ValueError("No results available. Please run grade_all() first.")

        table = self.prepare_result_table()

        # Convert table into CSV string
        csv_lines = []
        for row in table:
            csv_lines.append(",".join(row))
        csv_content = "\n".join(csv_lines)
        return csv_content

    def write_csv(
            self,
            csv_filename: str
    ):
        """
        Write the results to a CSV file.
        """
        csv_content = self.prepare_csv()
        with open(csv_filename, 'w') as file:
            file.write(csv_content)


    def from_zip(
            configuration_filename: str,
            zip_filename
    ) -> MultipleAutoGrader:
        """
        Create a MultipleAutoGrader from a zip file.
        """
        # Unzip the file
        extracted_files = unzip_get_files(zip_filename)

        # Find player files (assuming .py and .ipynb files are player files)
        player_filenames = []
        for file in extracted_files:
            if file.endswith('.py') or file.endswith('.ipynb'):
                player_filenames.append(file)

        # Create the MultipleAutoGrader
        return MultipleAutoGrader(
            configuration_filename=configuration_filename,
            player_filenames=player_filenames
        )
