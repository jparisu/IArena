"""Defines a player base class that can be loaded dynamically from source files."""

from __future__ import annotations

import json
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from iarena.playing.Player import Player
from iarena.utilizing.filing.Loader import Loader

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class LoadPlayer(Player):
    """Abstract player with file-loading support for custom external strategies.

    Purpose:
        Provides the `LoadPlayer` type within the IArena architecture.
    How it works:
        Adds default metadata/setup hooks and a classmethod that loads one
        player from a Python file or notebook.
    Used for:
        Running user-defined players distributed as standalone Python scripts
        or notebooks.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @abstractmethod
    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position.

        What it does:
            Declares the core decision method that produces one legal movement.
        How it works:
            Concrete subclasses evaluate the input position and select a movement.
        Args:
            pos (Position): Current game position where the player must act.
        Returns:
            Movement: Movement chosen by the player strategy.
        """
        raise NotImplementedError

    @abstractmethod
    def authors(self) -> list[str]:
        """Return the list of authors for this player implementation.

        What it does:
            Declares metadata used to identify who created the player.
        How it works:
            Concrete subclasses return one or more stable author names.
        Args:
            None.
        Returns:
            list[str]: Ordered list of author names.
        """
        raise NotImplementedError

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize player state when a new game begins.

        What it does:
            Provides a default setup hook that intentionally performs no work.
        How it works:
            Accepts the game context and returns immediately.
        Args:
            rules (Rules): Rules instance associated with the game to be played.
            player_index (PlayerIndex): Player identifier assigned in the arena.
        Returns:
            None: This default implementation has no side effects.
        """
        _ = (rules, player_index)

    def name(self) -> str:
        """Return the default stable name for dynamically loaded players.

        What it does:
            Provides a canonical fallback identifier.
        How it works:
            Returns a constant string unless subclasses override it.
        Args:
            None.
        Returns:
            str: Default name used for loaded players.
        """
        return "load-player"

    @classmethod
    def from_file(cls, path: str, token: str = "PLAYER =") -> LoadPlayer:
        """Load one `LoadPlayer` instance from a Python file or notebook.

        What it does:
            Executes one source artifact and returns its `PLAYER` instance.
        How it works:
            For `.py`, imports the module from disk. For `.ipynb`, executes the
            first code cell containing `token`. Then validates `PLAYER` type.
        Args:
            path (str): Path to the source file containing a `PLAYER` variable.
            token (str): Substring used to pick the notebook cell to execute.
        Returns:
            LoadPlayer: Loaded player instance exposed by the module.
        Raises:
            FileNotFoundError: If `path` does not exist.
            IsADirectoryError: If `path` points to a directory.
            ImportError: If the module cannot be loaded or executed.
            ValueError: If the module does not define `PLAYER`.
            TypeError: If `PLAYER` is not an instance of `LoadPlayer`.
        """
        source_path = Path(path)
        if source_path.suffix.lower() == ".ipynb":
            loaded_variables = cls._load_notebook_variables(filename=path, variable_names=["PLAYER"], token=token)
        else:
            loaded_variables = Loader.load_file(filename=path, variable_names=["PLAYER"])
        loaded_player = loaded_variables["PLAYER"]
        if not isinstance(loaded_player, LoadPlayer):
            raise TypeError(
                f"PLAYER must be an instance of LoadPlayer, got {type(loaded_player).__name__} from {path}",
            )
        return loaded_player

    @classmethod
    def _load_notebook_variables(
        cls,
        filename: str,
        variable_names: list[str],
        token: str,
    ) -> dict[str, Any]:
        """Load variables from one notebook cell selected by token matching.

        What it does:
            Reads one notebook file, executes one selected code cell, and
            extracts module-level variables.
        How it works:
            Finds the first code cell containing `token`, executes it in an
            isolated namespace, and validates requested variable names.
        Args:
            filename (str): Notebook path.
            variable_names (list[str]): Expected variables after execution.
            token (str): Cell-selection token.
        Returns:
            dict[str, Any]: Mapping from variable names to loaded values.
        Raises:
            FileNotFoundError: If `filename` does not exist.
            IsADirectoryError: If `filename` points to a directory.
            ValueError: If notebook content is invalid, no matching cell
                exists, or one required variable is missing.
            ImportError: If selected code cell execution fails.
        """
        source_path = Path(filename)
        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {source_path}")
        if source_path.is_dir():
            raise IsADirectoryError(f"Expected a file path, got directory: {source_path}")

        try:
            notebook = json.loads(source_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid notebook JSON: {source_path}") from exc

        cell_code = cls._find_notebook_cell_code(notebook=notebook, token=token, filename=filename)
        loaded_variables: dict[str, Any] = {}
        namespace: dict[str, Any] = {}
        try:
            compiled = compile(cell_code, f"{filename}::<token:{token}>", "exec")
            exec(compiled, namespace)  # noqa: S102  # pylint: disable=exec-used
        except Exception as exc:  # pragma: no cover - validated through integration-oriented paths
            raise ImportError(f"Failed to execute selected notebook cell from: {source_path}") from exc

        for variable_name in variable_names:
            if variable_name not in namespace:
                raise ValueError(f"Missing required variable '{variable_name}' in file: {filename}")
            loaded_variables[variable_name] = namespace[variable_name]
        return loaded_variables

    @classmethod
    def _find_notebook_cell_code(cls, notebook: object, token: str, filename: str) -> str:
        """Return the first code cell content that contains the requested token.

        Args:
            notebook (object): Parsed notebook JSON object.
            token (str): Substring that identifies the target cell.
            filename (str): Original notebook filename for error messages.
        Returns:
            str: Python code to execute.
        Raises:
            ValueError: If notebook shape is invalid or no matching cell exists.
        """
        if not isinstance(notebook, dict):
            raise ValueError(f"Notebook root content must be a mapping/object: {filename}")

        cells = notebook.get("cells")
        if not isinstance(cells, list):
            raise ValueError(f"Notebook must contain a `cells` list: {filename}")

        for cell in cells:
            if not isinstance(cell, dict):
                continue
            if cell.get("cell_type") != "code":
                continue
            raw_source = cell.get("source", "")
            if isinstance(raw_source, list):
                source = "".join(str(line) for line in raw_source)
            else:
                source = str(raw_source)
            if token in source:
                return source

        raise ValueError(f"No notebook code cell contains token '{token}' in file: {filename}")
