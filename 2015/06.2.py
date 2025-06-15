from typing import TextIO
from enum import Enum
from io import StringIO
import sys

class Action(Enum):
  ON = 1
  OFF = 2
  TOGGLE = 3

def count_lit_cnt(actions_io: TextIO, grid: list[list[int]]) -> int:
  brightness = 0
  
  line = actions_io.readline()
  while line:
    # parse action and coords
    parts = line.split()
    match len(parts):
      case 4:
        _, c1_str, _, c2_str = line.split()
        action = Action.TOGGLE
      case 5:
        _, on_off, c1_str, _, c2_str = line.split()
        action = Action.ON if on_off == 'on' else Action.OFF
      case _:
        raise RuntimeError(f'Unexpected line parts: {parts}')
    
    # build 1st coord
    p1 = 0
    while c1_str[p1] != ',': p1 += 1
    c1x = int(c1_str[:p1])
    c1y = int(c1_str[p1+1:])
    
    # build 2nd coord
    p2 = 0
    while c2_str[p2] != ',': p2 += 1
    c2x = int(c2_str[:p2])
    c2y = int(c2_str[p2+1:])
    
    # validate input
    if c1x > c2x or c1y > c2y:
      raise RuntimeError(f'Coords given not in lower right to upper left format: ({c1x}, {c1y}), ({c2x}, {c2y})')
    
    # perform the given action
    for x in range(c1x, c2x+1):
      for y in range(c1y, c2y+1):
        match action:
          case Action.ON:
            brightness += 1
            grid[x][y] += 1
          case Action.OFF:
            if grid[x][y] > 0:
              brightness -= 1
              grid[x][y] -= 1
          case Action.TOGGLE:
            brightness += 2
            grid[x][y] += 2
          case _:
            raise RuntimeError(f'Unexpected action provided: {action}')
          
    line = actions_io.readline()
    
  return brightness
    
test = False
    
if __name__ == '__main__':
  if test:
    def make_grid(x: int, y: int) -> list[list[int]]:
      return [[0 for _ in range(x)] for _ in range(y)]
    
    actual = count_lit_cnt(StringIO(''), make_grid(3, 3))
    if actual != 0:
      raise RuntimeError(f"Expected {0} but got {actual}")
    
    actual = count_lit_cnt(StringIO('turn off 0,0 through 2,2'), make_grid(3, 3))
    if actual != 0:
      raise RuntimeError(f"Expected {0} but got {actual}")
    
    actual = count_lit_cnt(StringIO('turn on 0,0 through 2,2'), make_grid(3, 3))
    if actual != 9:
      raise RuntimeError(f"Expected {9} but got {actual}")
    
    actual = count_lit_cnt(StringIO('turn on 0,0 through 2,2\nturn on 0,0 through 2,2'), make_grid(3, 3))
    if actual != 18:
      raise RuntimeError(f"Expected {18} but got {actual}")
    
    actual = count_lit_cnt(StringIO('toggle 0,0 through 2,2'), make_grid(3, 3))
    if actual != 18:
      raise RuntimeError(f"Expected {18} but got {actual}")
    
    actual = count_lit_cnt(StringIO('turn on 0,0 through 1,1\nturn off 0,0 through 0,1'), make_grid(3, 3))
    if actual != 2:
      raise RuntimeError(f"Expected {2} but got {actual}")
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    print(count_lit_cnt(f, [[False for _ in range(1000)] for _ in range(1000)]))