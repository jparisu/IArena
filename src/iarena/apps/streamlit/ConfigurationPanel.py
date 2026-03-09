"""Declares the streamlit configuration panel used by the streamlit application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iarena.gaming.Configuration import Configuration
    from iarena.playing.Player import Player


class ConfigurationPanel:
    """Streamlit panel responsible for player and configuration selection.

    Purpose:
        Encapsulate sidebar widgets used to select players and configurations.
    How it works:
        Keeps a small `controls` dictionary with values selected through
        streamlit widgets.
    Used for:
        Shared sidebar interactions inside `StreamlitApplication`.
    Public Attributes:
        controls (dict[str, Any]): Snapshot of values selected in this panel.
    """

    controls: dict[str, Any]

    def __init__(self) -> None:
        """Initialize one empty configuration panel state container.

        Returns:
            None.
        """
        self.controls = {}

    def ask_for_player(
        self,
        player_classes: list[type[Player]],
        slot_index: int,
        *,
        default_index: int = 0,
        key_prefix: str = "streamlit_player",
    ) -> type[Player]:
        """Return one player class selected in streamlit widgets.

        Args:
            player_classes: Available player classes for this slot.
            slot_index: Player slot index currently being configured.
            default_index: Fallback option index when no prior selection exists.
            key_prefix: Session-state key prefix used by the selection widget.

        Returns:
            type[Player]: Selected player class.
        """
        import streamlit as st

        if not player_classes:
            raise ValueError("Cannot ask for a player from an empty class list.")

        labels = [self._player_label(player_cls) for player_cls in player_classes]
        default_choice = min(max(default_index, 0), len(labels) - 1)

        selected_label = st.selectbox(
            label=f"Player slot {slot_index}",
            options=labels,
            index=default_choice,
            key=f"{key_prefix}_{slot_index}",
        )
        selected_index = labels.index(selected_label)
        selected_class = player_classes[selected_index]
        self.controls[f"player_class_{slot_index}"] = selected_class
        return selected_class

    def set_configuration(self, configuration: Configuration) -> None:
        """Persist one selected configuration object in panel controls.

        Args:
            configuration: Configuration object selected through panel widgets.

        Returns:
            None.
        """
        self.controls["configuration"] = configuration

    def ask_for_configuration(self) -> Configuration:
        """Return the configuration object currently stored in panel controls.

        Returns:
            Configuration: Stored configuration object.

        Raises:
            RuntimeError: If configuration has not been set yet.
        """
        configuration = self.controls.get("configuration")
        if configuration is None:
            raise RuntimeError("Configuration is not available in panel controls.")
        return configuration

    def _player_label(self, player_cls: type[Player]) -> str:
        """Build a readable label for one player class option.

        Args:
            player_cls: Player class to format for UI display.

        Returns:
            str: Human-readable label for the option list.
        """
        from iarena.playing.HumanPlayer import HumanPlayer

        category = "human" if issubclass(player_cls, HumanPlayer) else "automatic"
        try:
            display_name = player_cls().name()
        except Exception:
            display_name = player_cls.__name__
        return f"{display_name} ({category})"
