import argparse
import unittest
import textwrap
import typing
import enum
import sys
import io

class InvalidGridSize(Exception): pass

class CellState(enum.IntEnum): ON = 1; OFF = 0
class TempCellState(enum.IntEnum): ON_TO_OFF = 3; OFF_TO_ON = 4

ON, OFF = CellState.ON, CellState.OFF
NEIGHBOR_DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)] # lower left moving clockwise

Grid: typing.TypeAlias = list[list[int]]

def grid_step(grid: Grid) -> Grid:
  rows, cols = len(grid), len(grid[0])
  
  # Since lights must update simultaneously, we'll have to keep track of the original state until we
  # have determined the new state of all cells. To do this, we'll use temporary states (TempCellState).
  
  for r in range(rows):
    for c in range(cols):
      # corners cannot be altered / turned off
      if (
        (r == 0 and c == 0) or
        (r == 0 and c == cols - 1) or
        (r == rows - 1 and c == 0) or
        (r == rows - 1 and c == cols - 1)
      ):
        continue
      
      match grid[r][c]:
        case CellState.ON:
          nei_on = 0
          for dr, dc in NEIGHBOR_DIRECTIONS:
            row = dr + r
            col = dc + c
            if (
              0 <= row < rows and
              0 <= col < cols and
              (grid[row][col] == ON or grid[row][col] == 3) # is/was on
            ):
              nei_on += 1
              if nei_on >= 4:
                break # not a match, no need to check the rest of the neighbors 
          if nei_on != 2 and nei_on != 3:
            grid[r][c] = TempCellState.ON_TO_OFF
        case CellState.OFF:
          nei_on = 0
          for dr, dc in NEIGHBOR_DIRECTIONS:
            row = dr + r
            col = dc + c
            if (
              0 <= row < rows and
              0 <= col < cols and
              (grid[row][col] == ON or grid[row][col] == 3) # is/was on
            ):
              nei_on += 1
              if nei_on >= 4:
                break # not a match, no need to check the rest of the neighbors
          if nei_on == 3:
            grid[r][c] = TempCellState.OFF_TO_ON
        case _:
          raise RuntimeError(f'Unexpected grid state: {grid[r][c]}')
        
  # Now we can update all the lights to their final state
  for r in range(rows):
    for c in range(cols):
      match grid[r][c]:
        case CellState.ON | CellState.OFF:
          pass
        case TempCellState.ON_TO_OFF:
          grid[r][c] = CellState.OFF
        case TempCellState.OFF_TO_ON:
          grid[r][c] = CellState.ON
        case _:
          raise RuntimeError(f'Unexpected grid state: {grid[r][c]}')
  
  return grid

def parse_grid(stream: typing.TextIO, *, rows: int, cols: int) -> Grid:
  grid: Grid = [[0 for _ in range(cols)] for _ in range(rows)]
  
  for r in range(rows):
    line = stream.readline().strip()
    if len(line) != cols:
      raise InvalidGridSize(f'Unexpected number of cols found for row {r}: {len(line)} != {cols}')
    
    for c in range(cols):
      match line[c]:
        case '#':
          grid[r][c] = CellState.ON
        case '.':
          grid[r][c] = CellState.OFF
        case _:
          raise RuntimeError(f'Unexpected byte at row {r} and col {c}: {line[c]}')
  
  return grid

class Tests(unittest.TestCase):
  def test_grid_step(self):
    grid_0 = parse_grid(io.StringIO(textwrap.dedent("""\
      ##.#.#
      ...##.
      #....#
      ..#...
      #.#..#
      ####.#""")), rows=6, cols=6)
    
    grid_1 = parse_grid(io.StringIO(textwrap.dedent("""\
      #.##.#
      ####.#
      ...##.
      ......
      #...#.
      #.####""")), rows=6, cols=6)
    
    grid_2 = parse_grid(io.StringIO(textwrap.dedent("""\
      #..#.#
      #....#
      .#.##.
      ...##.
      .#..##
      ##.###""")), rows=6, cols=6)
    
    grid_3 = parse_grid(io.StringIO(textwrap.dedent("""\
      #...##
      ####.#
      ..##.#
      ......
      ##....
      ####.#""")), rows=6, cols=6)
    
    grid_4 = parse_grid(io.StringIO(textwrap.dedent("""\
      #.####
      #....#
      ...#..
      .##...
      #.....
      #.#..#""")), rows=6, cols=6)
    
    grid_5 = parse_grid(io.StringIO(textwrap.dedent("""\
      ##.###
      .##..#
      .##...
      .##...
      #.#...
      ##...#""")), rows=6, cols=6)
    
    self.assertEqual(grid_step(grid_0), grid_1)
    self.assertEqual(grid_step(grid_1), grid_2)
    self.assertEqual(grid_step(grid_2), grid_3)
    self.assertEqual(grid_step(grid_3), grid_4)
    self.assertEqual(grid_step(grid_4), grid_5)
    
  def test_parse_grid(self):
    # success
    self.assertEqual(parse_grid(io.StringIO('.#.#.#'), rows=1, cols=6), [[OFF, ON, OFF, ON, OFF, ON]])
    self.assertEqual(parse_grid(io.StringIO('.#.\n#.#'), rows=2, cols=3), [[OFF, ON, OFF], [ON, OFF, ON]])
    self.assertEqual(parse_grid(io.StringIO('.#\n.#\n.#'), rows=3, cols=2), [[OFF, ON], [OFF, ON], [OFF, ON]])
    
    # failure
    self.assertRaises(InvalidGridSize, lambda: parse_grid(io.StringIO('.#.#.#'), rows=100, cols=100))

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      grid = parse_grid(f, rows=100, cols=100)
    
    # turn all corners on
    rows, cols = len(grid), len(grid[0])
    grid[0][0] = CellState.ON
    grid[0][cols - 1] = CellState.ON
    grid[rows - 1][0] = CellState.ON
    grid[rows - 1][cols - 1] = CellState.ON
    
    for _ in range(100):
      grid = grid_step(grid)
      
    on = 0
    for r in range(len(grid)):
      for c in range(len(grid[0])):
        if grid[r][c] == ON:
          on += 1
    
    print(on)