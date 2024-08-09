from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

sample_maze="""
#####B#
##### #
####  #
#### ##
     ##
A######
"""

Stategy = Literal["bfs", "dfs"]

class MazeSymbols(Enum):
    WALL = 0
    CLEAR = 1
    START = 2
    END = 3


DEFAULT_SYMBOLS = {'#': MazeSymbols.WALL,
                        ' ': MazeSymbols.CLEAR,
                        'A': MazeSymbols.START,
                        'B': MazeSymbols.END}



class Node:
    def __init__(self, state: tuple[int, int], parent: Node | None = None):
        self.state = state
        self.parent = parent

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.state == other.state

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}({self.state!r}, {self.parent!r})"

class Frontier:
    def __init__(self, strategy: Literal["bfs", "dfs"] = "bfs"):
        self.frontier = []
        if strategy == "bfs":
            self.remover = lambda x: x.pop(0)
        elif strategy == "dfs":
            self.remover = lambda x: x.pop()

    def add(self, node: Node):
        self.frontier.append(node)

    def remove(self) -> Node:
        return self.remover(self.frontier)

    def __contains__(self, state: tuple[int, int]) -> bool:
        return any(node.state == state for node in self.frontier)

    def __iter__(self):
        return iter(self.frontier)

    def __len__(self) -> int:
        return len(self.frontier)

class Maze:
    maze: list[list[MazeSymbols]] | None
    symbols: dict
    current_position: tuple[int, int] | None
    end_position: tuple[int, int] | None
    start_position: tuple[int, int] | None
    checked: set[tuple[int, int]]
    frontier: Frontier

    def __init__(self, symbols: dict, _maze: list[list[MazeSymbols]] | None = None):
        self.maze = _maze
        self.symbols = symbols
        self.current_position = None
        self.end_position = None
        self.start_position = None
        self.checked = set()
        self.frontier = Frontier()


    def initialize(self, maze: str | Path | list[list[MazeSymbols]]):
        if isinstance(maze, Path):
            with maze.open() as f:
                self.maze = self.parse_maze(f.read())
        elif isinstance(maze, str):
            self.parse_maze(maze)
        elif isinstance(maze, list):
            self.maze = maze
        else:
            raise ValueError("Invalid maze input")

        self.start_position = self.get_position(MazeSymbols.START)
        self.end_position = self.get_position(MazeSymbols.END)
        print(self.maze)

    def __str__(self) -> str:
        if self.maze is None:
            return "Empty Maze"
        return "\n".join("".join(str(symbol.value) for symbol in row) for row in self.maze)

    def _decode_row(self, row: str) -> list[MazeSymbols]:
        return [self.symbols.get(symbol, MazeSymbols.WALL) for symbol in row]

    def get_position(self, target: MazeSymbols) -> tuple[int, int]:
        assert self.maze is not None, "Maze not initialized"
        return next((i, j) for i, row in enumerate(self.maze)
                    for j, symbol in enumerate(row) if symbol == target)

    def parse_maze(self, maze, decoder = DEFAULT_SYMBOLS):
        self.maze = [self._decode_row(row.rstrip())
            for row in maze.strip().splitlines()]

    def is_valid_move(self, position: tuple[int, int]) -> bool:
        assert self.maze is not None, "Maze not initialized"
        y, x = position
        return (0 <= y < len(self.maze)
        and 0 <= x < len(self.maze[0])
        and self.maze[y][x] != MazeSymbols.WALL
        and position not in self.checked)

    def find_viable_moves(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        y, x = position
        moves = [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]
        return [move for move in moves if self.is_valid_move(move)]

    def retrace_path(self, node: Node) -> list[tuple[int, int]]:
        path = []
        while node.parent:
            path.append(node.state)
            node = node.parent
        path.append(node.state)
        return path[::-1]

    def solve(self):
        assert self.start_position is not None, "Start position not initialized"
        assert self.end_position is not None, "End position not initialized"

        self.frontier.add(Node(self.start_position))
        print("End pos:", self.end_position)
        while self.frontier:
            current_node = self.frontier.remove()
            print(current_node.state)

            self.checked.add(current_node.state)

            if current_node.state == self.end_position:
                return self.retrace_path(current_node)

            for move in self.find_viable_moves(current_node.state):
                self.frontier.add(Node(move, current_node))

        raise ValueError("No path found")

if __name__ == "__main__":
    maze = Maze(DEFAULT_SYMBOLS)
    maze.initialize(sample_maze)
    print(maze)
    print(maze.solve())
