from typing import List, Iterator, Dict
from itertools import product

from IArena.interfaces.IGameRules import IGameRules
from IArena.utils.decorators import pure_virtual

from IArena.utils.importing import import_class_from_module

"""Dictionary with the arguments required for the RulesGenerator to generate a rule."""
RulesGeneratorConfiguration = dict


class RulesGeneratorSuite:
    """
    Dictionary with the arguments required for the RulesGenerator to generate a rule.
    This class represents a suite of configurations for generating game rules where some arguments could have multiple values.
    Each configuration is a combination of the fixed arguments and one value from each of the multi-valued arguments.
    """

    def __init__(
                self,
                args: dict,
                multi_args: dict = None,
            ):

        self._args = args
        self._multi_args = multi_args if multi_args is not None else {}

    def get_configuration_iterator(self) -> Iterator[RulesGeneratorConfiguration]:
        if len(self._multi_args) == 0:
            yield self._args
        else:
            keys, values = zip(*self._multi_args.items())
            for v in product(*values):
                args = self._args.copy()
                args.update(dict(zip(keys, v)))
                yield args

    def count_configurations(self) -> int:
        if len(self._multi_args) == 0:
            return 1
        else:
            count = 1
            for values in self._multi_args.values():
                count *= len(values)
            return count



class IRulesGenerator:
    """
    This abstract class represents a generator of game rules.
    """

    @pure_virtual
    def generate(self, configuration: RulesGeneratorConfiguration) -> IGameRules:
        """Generates a game rules instance based on the provided configuration dictionary."""
        pass


    def _get_param(
                configuration: RulesGeneratorConfiguration,
                param_name: str = None,
                param_names: List[str] = None,
                default_value = None,
                required: bool = False,
                type_cast = None,
            ):
        """
        Returns the value of the parameter with the given name from the configuration dictionary.
        If the parameter is not found, returns the default value.
        """

        def __type_cast(value, type_cast):
            if type_cast is not None:
                try:
                    value = type_cast(value)
                except Exception as e:
                    raise ValueError(f'Error casting parameter to {type_cast}: {e}')
            return value

        if param_names is None:
            param_names = [param_name]

        elif param_name is not None:
            param_names.insert(0, param_name)

        for name in param_names:
            if name in configuration:
                value = configuration[name]
                return __type_cast(value, type_cast)

        if required:
            raise ValueError(f'One of the parameters {param_names} is required in configuration.')
        return default_value


def get_rules_generator_from_name(name: str) -> IRulesGenerator:
    """
    Given the name of a game, returns the generator corresponding class.

    The module should be located in the IArena.games package.
    The name of the package should be equal to the class name, and the class should be in CamelCase as:
        <name>RulesGenerator
    """

    class_name = f"{name}RulesGenerator"

    try:
        rules_generator_class = import_class_from_module(f"IArena.games.{name}", f"{class_name}")
        if not issubclass(rules_generator_class, IRulesGenerator):
            raise ValueError(f"Class {class_name} is not a subclass of IRulesGenerator.")
        return rules_generator_class()

    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Could not find rules generator for game {name}: {e}")
