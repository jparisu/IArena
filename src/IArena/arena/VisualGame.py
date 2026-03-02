from typing import List
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.utils.decorators import override
from IArena.arena.GenericGame import GenericGame



@dataclass
class ViewerConfig:
    interval_ms: int = 300


class VisualGame(GenericGame):

    def __init__(
                self,
                rules: IGameRules,
                players: List[IPlayer],
                max_moves: int = None,
                check_movements: bool = False,
            ):
        super().__init__(rules, players, max_moves, check_movements)
        self.__states_history: List[IPosition] = [self.rules.first_position()]
        self.__moves_history: List[IMovement] = []


    @override
    def next_movement_(self, current_position: IPosition) -> IPosition:
        next_player_index = current_position.next_player()
        movement = self.players[next_player_index].play(current_position)

        # Check if the movement is possible
        # if not self.rules.is_movement_possible(movement, current_position):
        #     raise ValueError(f'Player <{self.get_player_name(next_player_index)}> has made an invalid movement: {movement} in position:\n{current_position}')

        next_position = self.rules.next_position(
            movement,
            current_position)

        self.__states_history.append(next_position)
        self.__moves_history.append(movement)

        return next_position


    def visualize(self, conf: ViewerConfig = ViewerConfig()):
        # 1. Ensure game has run
        if not self.__moves_history:
            print("Running game simulation...")
            self.play()

        total_steps = len(self.__states_history)
        if total_steps == 0:
            print("No states to visualize.")
            return

        # 2. Setup Figure and Main Axis
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.25) # Leave space at bottom for controls

        # 3. Visualization State
        # We use a mutable dict or class attributes to handle state inside callbacks
        state = {
            'index': 0,
            'playing': False,
            'timer': None
        }

        # 4. Helper: The Draw Function
        def update_plot(val=None):
            # Clamp index
            idx = int(state['index'])
            if idx < 0: idx = 0
            if idx >= total_steps: idx = total_steps - 1
            state['index'] = idx

            # Update Slider visual without triggering callback (to avoid recursion)
            slider.eventson = False
            slider.set_val(idx)
            slider.eventson = True

            # Clear and Redraw Game
            ax.clear()
            current_pos = self.__states_history[idx]

            # Call your IGameRules.plot_step
            self.rules.plot_step(
                axis=ax,
                position=current_pos,
            )

            # ax.set_title(f"Step: {idx} / {total_steps - 1}")
            fig.canvas.draw_idle()

        # 5. Define Widgets

        # -- Slider --
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(
            ax=ax_slider,
            label='Time',
            valmin=0,
            valmax=total_steps - 1,
            valinit=0,
            valstep=1
        )

        # -- Buttons positions --
        # Dimensions: [left, bottom, width, height]
        btn_width = 0.08
        btn_height = 0.05
        btn_y = 0.025
        spacing = 0.02
        start_x = 0.15

        ax_begin = plt.axes([start_x, btn_y, btn_width, btn_height])
        ax_prev  = plt.axes([start_x + (btn_width+spacing)*1, btn_y, btn_width, btn_height])
        ax_play  = plt.axes([start_x + (btn_width+spacing)*2, btn_y, btn_width, btn_height])
        ax_pause = plt.axes([start_x + (btn_width+spacing)*3, btn_y, btn_width, btn_height])
        ax_next  = plt.axes([start_x + (btn_width+spacing)*4, btn_y, btn_width, btn_height])
        ax_end   = plt.axes([start_x + (btn_width+spacing)*5, btn_y, btn_width, btn_height])

        btn_begin = Button(ax_begin, '<<')
        btn_prev  = Button(ax_prev, '<')
        btn_play  = Button(ax_play, 'Play')
        btn_pause = Button(ax_pause, 'Pause')
        btn_next  = Button(ax_next, '>')
        btn_end   = Button(ax_end, '>>')

        # 6. Callbacks

        def on_slider_change(val):
            state['index'] = int(val)
            update_plot()

        def to_begin(event):
            state['index'] = 0
            update_plot()

        def to_end(event):
            state['index'] = total_steps - 1
            update_plot()

        def step_back(event):
            if state['index'] > 0:
                state['index'] -= 1
                update_plot()

        def step_fwd(event=None):
            if state['index'] < total_steps - 1:
                state['index'] += 1
                update_plot()
            else:
                # Stop if we reach the end while playing
                if state['playing']:
                    pause_sim(None)

        # -- Play/Pause Logic --
        # We use fig.canvas.new_timer for backend-independent timing loops
        timer = fig.canvas.new_timer(interval=conf.interval_ms)
        timer.add_callback(step_fwd)
        state['timer'] = timer

        def play_sim(event):
            if not state['playing']:
                state['playing'] = True
                # If at end, restart
                if state['index'] >= total_steps - 1:
                    state['index'] = 0
                    update_plot()
                state['timer'].start()

        def pause_sim(event):
            if state['playing']:
                state['playing'] = False
                state['timer'].stop()

        # 7. Connect Events
        slider.on_changed(on_slider_change)
        btn_begin.on_clicked(to_begin)
        btn_prev.on_clicked(step_back)
        btn_play.on_clicked(play_sim)
        btn_pause.on_clicked(pause_sim)
        btn_next.on_clicked(step_fwd)
        btn_end.on_clicked(to_end)

        # Store references to prevent garbage collection
        self._widgets_ref = [slider, btn_begin, btn_prev, btn_play,
                             btn_pause, btn_next, btn_end]

        # Initial draw
        update_plot()
        plt.show()
