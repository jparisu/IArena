
from IArena.arena.GenericGame import GenericGame
from IArena.games.GoldMine import GoldMineGameRules
from IArena.games.solvers.Solver import Solver
from IArena.games.GoldMine import GoldMinePosition, GoldMineGameRules, GoldMineMovement, GoldMineCoordinate, GoldMineDirection
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.utils.RandomTiePriorityQueue import RandomTiePriorityQueue



class BlindGoldMine_OptimalPlayer(IPlayer):

    def __init__(self, rng: RandomGenerator = None, name: str = None):
        super().__init__(name=name)
        if rng is None:
            rng = RandomGenerator(0)
        self.rng = rng

    """
    Optimal player for a non-hint search in GoldMine game.
    It uses UCS algorithm to find minimum path.
    """

    def starting_game(
            self,
            rules: GoldMineGameRules,
            player_index: int):

        self.current_position = GoldMineCoordinate(0, 0)
        self.visited_tiles = set([self.current_position])
        self.tiles_to_visit = RandomTiePriorityQueue(random_generator=self.rng)
        self.current_active_path = []

    def _find_move(self, target):
        """Find a path to target using visited tiles."""

        def rearrange_path(visited, target):
            # print(f"Rearranging path: {visited} from {target}")
            path = [target]
            while target is not None:
                target = visited[target]
                path.append(target)
            return path[::-1][2:]

        visited = {}
        to_visit = {}
        to_visit[self.current_position] = None

        while not len(to_visit) == 0:

            position, previous = to_visit.popitem()

            visited[position] = previous

            if position == target:
                break

            for _, neig in position.neighbors():

                if neig == target:
                    visited[target] = position
                    return rearrange_path(visited, target)

                elif neig not in visited and neig not in to_visit and neig in self.visited_tiles:

                    to_visit[neig] = position

        raise ValueError("Finished without finding new path")

    def _continue_path(self):
        if self.current_active_path:
            move = self.current_active_path.pop(0)
            for dir, neig in self.current_position.neighbors():
                if neig == move:
                    return GoldMineMovement(dir)
        else:
            raise ValueError("No current move to continue")

    def _check_surroundings(self, position):
        self.visited_tiles.add(self.current_position)
        for dir, cost in position.get_directions_with_cost():
            pos = self.current_position.from_direction(dir)

            if pos not in self.visited_tiles and pos not in self.tiles_to_visit:
                self.tiles_to_visit.push(cost, pos)

    def _define_new_path(self):

        # Get lowest unvisited tile
        cost, next_tile = self.tiles_to_visit.pop()

        # Find path to it
        self.current_active_path = self._find_move(next_tile)

    def __play(
            self,
            position: GoldMinePosition) -> GoldMineMovement:

        # If inside a path, continue
        if not self.current_active_path:

            # If not, first check surroundings
            self._check_surroundings(position)

            # Then, generate new path to the lowest unvisited tile
            self._define_new_path()

        return self._continue_path()



    def play(
            self,
            position: GoldMinePosition) -> GoldMineMovement:

        movement = self.__play(position)
        # Modify current position
        self.current_position = self.current_position.from_direction(movement.direction)
        self.visited_tiles.add(self.current_position)
        return movement



class GoldMineSolver(Solver):

    def __init__(
            self,
            min_p: float = 1.0,
            max_p: float = 1.0,
            repetitions: int = 100
    ):
        self._min_p = min_p
        self._max_p = max_p
        self._rep = repetitions

    def min_max_allowed_score(self, rules: GoldMineGameRules) -> tuple[float, float]:
        mi, ma = 0, 0
        if rules.compass_activated():
            mi, ma = self._min_max_allowed_score_with_compass()
        elif rules.proximity_activated():
            mi, ma = self._min_max_allowed_score_with_proximity()
        else:
            mi, ma = self._min_max_allowed_score_without_help()

        return (mi * self._min_p, ma * self._max_p)


    def _min_max_allowed_score_without_help(self, rules: GoldMineGameRules) -> tuple[float, float]:

        scores = []
        for i in range(self._rep):

            arena = GenericGame(
                rules=rules,
                players=[BlindGoldMine_OptimalPlayer(RandomGenerator(i))],
                max_moves=None,
                check_movements=False
            )
            score = arena.play()
            scores.append(score[0])

        return (min(scores), max(scores))


    def _min_max_allowed_score_with_compass(self, rules: GoldMineGameRules) -> tuple[float, float]:

        # TODO
        return (0, self.__map.sum())


    def _min_max_allowed_score_with_proximity(self, rules: GoldMineGameRules) -> tuple[float, float]:
        return self._min_max_allowed_score_with_compass()
