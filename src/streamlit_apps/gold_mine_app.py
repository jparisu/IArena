import streamlit as st
import matplotlib.pyplot as plt
import sys

# Maintain your local path logic
sys.path.insert(1, '../')
sys.path.insert(1, './src')

from IArena.utils.square_map.SquareMap import Coordinate, Direction
from IArena.utils.square_map.random_map_generators import MapFactory
from IArena.games.GoldMine import GoldMineGenerator, GoldMineMovement

# --- SESSION STATE INITIALIZATION ---
if "game_rules" not in st.session_state:
    st.session_state.game_rules = None
if "current_pos" not in st.session_state:
    st.session_state.current_pos = None
if "seed" not in st.session_state:
    st.session_state.seed = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "history" not in st.session_state:
    st.session_state.history = []

def reset_game(config):
    generator = GoldMineGenerator()
    rules = generator.generate(config)
    st.session_state.game_rules = rules
    st.session_state.current_pos = rules.first_position()
    st.session_state.game_over = False
    # History stores list of strings for concise display
    st.session_state.history = []

def handle_move(direction: Direction):
    if st.session_state.game_over or st.session_state.game_rules is None:
        return

    pos = st.session_state.current_pos
    valid_dirs = list(pos.get_valid_directions())

    if direction in valid_dirs:
        move = GoldMineMovement(direction)
        new_pos = st.session_state.game_rules.next_position(move, pos)
        target_coord = new_pos._GoldMinePosition__current_position

        # Append concise move string
        st.session_state.history.append(f"({direction.name}) → [{target_coord.x}, {target_coord.y}]")

        st.session_state.current_pos = new_pos
        if st.session_state.game_rules.finished(new_pos):
            st.session_state.game_over = True

# --- LAYOUT: PARAMETER COLUMN (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Game Configuration")

    with st.expander("Map Geometry", expanded=True):
        height = st.number_input("Height (N)", min_value=3, max_value=50, value=5)
        width = st.number_input("Width (M)", min_value=3, max_value=50, value=5)

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            ui_seed = st.number_input("Seed", value=st.session_state.seed, key="seed_input")
        with col_s2:
            st.write(" ")
            if st.button("🎲"):
                import random
                st.session_state.seed = random.randint(0, 999999)
                st.rerun()

    with st.expander("Positions", expanded=False):
        st.write("**Starting Position**")
        start_x = st.number_input("Start X", min_value=0, max_value=height-1, value=0)
        start_y = st.number_input("Start Y", min_value=0, max_value=width-1, value=0)

        st.write("**Target Position**")
        enable_target = st.checkbox("Set Manual Target", value=False)
        if enable_target:
            target_x = st.number_input("Target X", min_value=0, max_value=height-1, value=height-1)
            target_y = st.number_input("Target Y", min_value=0, max_value=width-1, value=width-1)
            target_coord = Coordinate(target_x, target_y)
        else:
            target_coord = None

    with st.expander("Active Hints (New Game Only)"):
        ui_compass = st.checkbox("Compass", value=True)
        ui_proximity = st.checkbox("Proximity", value=False)
        ui_density = st.checkbox("Density", value=False)

    with st.expander("Generation Logic"):
        available_methods = MapFactory.available_generation_methods()
        map_generator = st.selectbox("Method", options=available_methods, index=0)

    if st.button("🚀 Generate Mine / Reset", use_container_width=True, type="primary"):
        config = {
            "n": height,
            "m": width,
            "seed": st.session_state.seed,
            "compass": ui_compass,
            "proximity": ui_proximity,
            "density": ui_density,
            "map_generator": map_generator,
            "starting_position": Coordinate(start_x, start_y),
            "target_position": target_coord,
            "integer": True,
            "map_configuration": {"p": 0.4, "scale": 5, "min_val": 1, "max_val": 20},
        }
        reset_game(config)

# --- MAIN GAME WINDOW ---
st.title("💰 GoldMine Explorer")

if st.session_state.game_rules:
    rules = st.session_state.game_rules
    pos = st.session_state.current_pos

    if st.session_state.game_over:
        score_obj = rules.score(pos)
        final_score = score_obj[0]
        st.balloons()
        st.success(f"### 🎉 Goal Reached! \n **Final Accumulated Cost:** {abs(final_score):.2f}")

    # --- UI: MOVEMENT CROSS ---
    st.markdown("### Controls")

    valid_dirs = {d: c for d, c in pos.get_directions_with_cost()}

    m_col1, m_col2, m_col3 = st.columns([1, 1, 1])

    with m_col2: # UP
        u_cost = valid_dirs.get(Direction.Up, None)
        if st.button("▲", disabled=(u_cost is None or st.session_state.game_over), key="btn_up", use_container_width=True):
            handle_move(Direction.Up)
            st.rerun()
        st.caption(f"Cost: {u_cost:.2f}" if u_cost is not None else "---")

    r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 1])
    with r2_col1: # LEFT
        l_cost = valid_dirs.get(Direction.Left, None)
        if st.button("◀", disabled=(l_cost is None or st.session_state.game_over), key="btn_left", use_container_width=True):
            handle_move(Direction.Left)
            st.rerun()
        st.caption(f"Cost: {l_cost:.2f}" if l_cost is not None else "---")

    # with r2_col2:
    #     k_input = st.text_input("KB", key="k_input", label_visibility="collapsed", placeholder="Click & WASD")
    #     if k_input:
    #         key_map = {"w": Direction.Up, "s": Direction.Down, "a": Direction.Left, "d": Direction.Right}
    #         char = k_input[-1].lower()
    #         if char in key_map:
    #             handle_move(key_map[char])
    #         st.rerun()

    with r2_col3: # RIGHT
        r_cost = valid_dirs.get(Direction.Right, None)
        if st.button("▶", disabled=(r_cost is None or st.session_state.game_over), key="btn_right", use_container_width=True):
            handle_move(Direction.Right)
            st.rerun()
        st.caption(f"Cost: {r_cost:.2f}" if r_cost is not None else "---")

    r3_col1, r3_col2, r3_col3 = st.columns([1, 1, 1])
    with r3_col2: # DOWN
        d_cost = valid_dirs.get(Direction.Down, None)
        if st.button("▼", disabled=(d_cost is None or st.session_state.game_over), key="btn_down", use_container_width=True):
            handle_move(Direction.Down)
            st.rerun()
        st.caption(f"Cost: {d_cost:.2f}" if d_cost is not None else "---")

    st.divider()

    # --- HINTS DISPLAY ---
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        if rules._GoldMineGameRules__compass_activated:
            st.metric("Compass", pos.get_compass().name)
    with h_col2:
        if rules._GoldMineGameRules__proximity_activated:
            st.metric("Proximity", pos.get_proximity())
    with h_col3:
        if rules._GoldMineGameRules__density_activated:
            st.metric("Density", pos.get_density())

    # --- CHEAT PANEL ---
    with st.expander("🕵️ Cheat Panel & Movement History"):
        st.write(f"**Live Cost:** {pos.get_accumulated_cost():.2f}")

        plot_col, hist_col = st.columns([2, 1])

        with plot_col:
            st.write("**Map View**")
            fig, ax = plt.subplots(figsize=(5, 5))
            # Fix: Explicitly pass the current position to the plot_step method
            rules.plot_step(ax, pos)
            st.pyplot(fig)

        with hist_col:
            st.write("**Move History**")
            if not st.session_state.history:
                st.info("No moves yet.")
            else:
                # Show Start Position
                start_c = rules._GoldMineGameRules__start
                st.write(f"Start: [{start_c.x}, {start_c.y}]")
                # Show chronological history
                for i, move_str in enumerate(st.session_state.history):
                    st.text(f"{i+1}. {move_str}")

else:
    st.info("👈 Configure parameters and click 'Generate Mine' to start the practice.")
