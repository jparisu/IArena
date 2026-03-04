
from abc import ABC, abstractmethod

from IArena.interfaces.IGameRules import IGameRules
from IArena.utils.importing import import_class_from_module

class Solver(ABC):
    """
    Abstract class that represents a solver for a game.
    A Solver is able to determine the minimum and maximum allowed scores for a rule set, which can be used to evaluate the performance of a player.
    """

    @abstractmethod
    def min_max_allowed_score(self, rules: IGameRules) -> tuple[float, float]:
        pass



def get_solver_from_name(name: str, args: dict = None) -> Solver:
    """
    Given the name of a game, returns the generator corresponding class.

    The module should be located in the IArena.games package.
    The name of the package should be equal to the class name, and the class should be in CamelCase as:
        <name>RulesGenerator
    """

    args = args or {}

    if name is None:
        raise ValueError("Solver name cannot be None.")

    base_name = name[:-6] if name.endswith("Solver") else name
    class_name = f"{base_name}Solver"

    try:
        rules_generator_class = import_class_from_module(f"IArena.games.solvers.{class_name}", f"{class_name}")
        if not issubclass(rules_generator_class, Solver):
            raise ValueError(f"Class {class_name} is not a subclass of Solver.")
        return rules_generator_class(**args)

    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Could not find solver for game {name}: {e}")
