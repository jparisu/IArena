"""GoldMine Streamlit page built on top of generic apping components."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.apping.AppingModels import OptimizationGamePage, OptimizationViewState
from iarena.gaming.GoldMine.GoldMine import GoldMineDirection
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.gaming.GoldMine.GoldMinePlayablePlayer import GoldMinePlayablePlayer
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.VisualGame import VisualGameState
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap
from iarena.utilizing.square_map.draw_square_map import plot_square_map
from iarena.utilizing.square_map.generators.MapFactory import MapFactory


def build_goldmine_streamlit_page() -> OptimizationGamePage:
    """Build GoldMine page definition for the generic Streamlit app index.

    Args:
        None.

    Returns:
        Fully configured GoldMine page definition.
    """
    generation_methods = tuple(MapFactory.available_generation_methods())
    hint_options = tuple(mode.value for mode in GoldMineHintMode)

    def render_configuration(container: Any) -> Mapping[str, object]:
        """Render GoldMine-specific configuration controls.

        Args:
            container: Streamlit-like container where controls are rendered.

        Returns:
            Dictionary with validated configuration values.
        """
        container.markdown("### GoldMine configuration")
        rows = int(container.number_input("Rows", min_value=2, max_value=60, value=8, step=1))
        cols = int(container.number_input("Columns", min_value=2, max_value=60, value=8, step=1))
        seed = int(container.number_input("Seed", min_value=0, max_value=99999999, value=0, step=1))
        map_method = str(container.selectbox("Map generator", options=generation_methods))
        hint_mode = str(container.selectbox("Hint mode", options=hint_options))
        return {
            "rows": rows,
            "cols": cols,
            "seed": seed,
            "map_method": map_method,
            "hint_mode": hint_mode,
        }

    def build_rules(values: Mapping[str, object]) -> GoldMineGameRules:
        """Build GoldMine rules from UI configuration.

        Args:
            values: Values produced by ``render_configuration``.

        Returns:
            Configured ``GoldMineGameRules``.
        """
        rows_raw = values["rows"]
        cols_raw = values["cols"]
        seed_raw = values["seed"]
        rows = rows_raw if isinstance(rows_raw, int) else int(str(rows_raw))
        cols = cols_raw if isinstance(cols_raw, int) else int(str(cols_raw))
        seed = seed_raw if isinstance(seed_raw, int) else int(str(seed_raw))
        map_method = str(values["map_method"])
        hint_mode = GoldMineHintMode.from_value(str(values["hint_mode"]))

        start = Coordinate(0, 0)
        target = Coordinate(rows - 1, cols - 1)
        generated_map = MapFactory.generate(
            name=map_method,
            n=rows,
            m=cols,
            start=start,
            target=target,
            rng=RandomGenerator(seed=seed),
            integer=False,
        )
        cost_map = SquareMap([[float(cell) for cell in row] for row in generated_map.tolist()])
        return GoldMineGameRules(
            cost_map=cost_map,
            target=target,
            start=start,
            hint_mode=hint_mode,
        )

    def render_position(container: Any, view_state: OptimizationViewState) -> None:
        """Render central GoldMine game information for one frame.

        Args:
            container: Streamlit-like container where frame information is rendered.
            view_state: Frame and replay details.

        Returns:
            None.
        """
        position = view_state.frame.position
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")

        container.subheader("Current state")
        container.write(
            f"Coordinate: ({position.current_position.x}, {position.current_position.y})"
        )
        container.write(f"Accumulated cost: {position.accumulated_cost():.2f}")
        options = position.directions_with_cost()
        if not options:
            container.write("Possible movements: <none>")
        else:
            container.write("Possible movements:")
            for direction, movement_cost in options:
                container.write(f"- {direction.name} (cost: {movement_cost:.2f})")

        if position.rules.is_hint_enabled(GoldMineHintMode.COMPASS) and not position.rules.finished(position):
            container.write(f"Compass hint: {position.compass_hint().name}")
        if position.rules.is_hint_enabled(GoldMineHintMode.PROXIMITY):
            container.write(f"Proximity hint: {position.proximity_hint()}")
        if position.rules.is_hint_enabled(GoldMineHintMode.DENSITY):
            container.write(f"Density hint: {position.density_hint():.2f}")

        secret_panel = container.expander("Secret map (debug)", expanded=False)
        if hasattr(secret_panel, "pyplot"):
            import matplotlib.pyplot as plt

            figure, axis = plt.subplots(figsize=(4.8, 4.8))
            plot_square_map(
                axis=axis,
                square_map=position.rules.cost_map(),
                start=position.rules.start_coordinate(),
                target=position.rules.target_coordinate(),
                cost=position.accumulated_cost(),
                empty_tiles=set(position.dug_tiles),
            )
            axis.scatter(
                [position.current_position.y],
                [position.current_position.x],
                s=180,
                marker="*",
                c="blue",
                zorder=11,
            )
            axis.set_title("Secret map")
            secret_panel.pyplot(figure)
            plt.close(figure)
        else:
            secret_panel.code(position.rules.cost_map().to_text())

    def render_description(container: Any, configuration: Mapping[str, object]) -> None:
        """Render GoldMine game description during configuration mode.

        Args:
            container: Streamlit-like container where description is rendered.
            configuration: Current game configuration.

        Returns:
            None.
        """
        rows = int(configuration.get("rows", 8))
        cols = int(configuration.get("cols", 8))
        hint_mode = str(configuration.get("hint_mode", "none"))
        container.markdown("### GoldMine")
        container.write("Reach the gold tile while minimizing digging cost.")
        container.write(f"Map size: {rows} x {cols}")
        container.write(f"Hint mode: {hint_mode}")
        container.write("Choose a human visual player for turn-by-turn gameplay.")

    def render_movements(container: Any, view_state: OptimizationViewState, state: VisualGameState) -> None:
        """Render movement panel content for GoldMine.

        Args:
            container: Streamlit-like container for movement information.
            view_state: Frame and replay details.
            state: Current visual game state.

        Returns:
            None.
        """
        position = view_state.frame.position
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")

        if state is VisualGameState.REVIEWING:
            if view_state.frame.movement_to_next is None:
                container.write("Movement taken: <none>")
            else:
                container.write(f"Movement taken: {view_state.frame.movement_to_next}")
            return

        container.write("Available directions:")
        cost_by_direction = {direction: cost for direction, cost in position.directions_with_cost()}
        for direction in (
            GoldMineDirection.Up,
            GoldMineDirection.Down,
            GoldMineDirection.Left,
            GoldMineDirection.Right,
        ):
            cost = cost_by_direction.get(direction)
            if cost is None:
                container.write(f"- {direction.name}: blocked")
            else:
                container.write(f"- {direction.name}: cost {cost:.2f}")
        container.write("Use the buttons below to choose the next movement.")

    def render_scoreboard(container: Any, view_state: OptimizationViewState) -> None:
        """Render GoldMine scoreboard details.

        Args:
            container: Streamlit-like container for score details.
            view_state: Frame and replay details.

        Returns:
            None.
        """
        position = view_state.frame.position
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")
        container.write(f"Current score: {view_state.frame.score.get_score(0):.2f}")
        container.write(f"Current cost: {-view_state.frame.score.get_score(0):.2f}")
        container.write(f"Dug tiles: {len(position.dug_tiles)}")
        if view_state.frame.movement_to_next is None:
            container.write(f"Final score: {view_state.replay.final_score.get_score(0):.2f}")

    def render_secret_information(container: Any, view_state: OptimizationViewState) -> None:
        """Render raw map information for compatibility with legacy views.

        Args:
            container: Streamlit-like container for secret details.
            view_state: Frame and replay details.

        Returns:
            None.
        """
        position = view_state.frame.position
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")
        container.code(position.rules.cost_map().to_text())

    return OptimizationGamePage(
        key="goldmine",
        title="GoldMine",
        render_configuration=render_configuration,
        build_rules=build_rules,
        render_position=render_position,
        render_description=render_description,
        render_movements=render_movements,
        render_scoreboard=render_scoreboard,
        render_secret_information=render_secret_information,
        default_player_factory=GoldMinePlayer,
        extra_player_factories={"Playable": GoldMinePlayablePlayer},
        turn_limit=10_000,
        autoplay_delay_seconds=0.1,
    )
