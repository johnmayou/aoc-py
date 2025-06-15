import collections
import argparse
import typing
import pprint
import sys
import io
import re

uint16max = (1 << 16) - 1

def assemble(instructions: typing.TextIO) -> dict[str, int]:
  wire_map: dict[str, int] = {}
  lines: collections.deque[str] = collections.deque()
  
  if line := instructions.readline().strip():
    lines.append(line)
  
  def get(x: str) -> typing.Optional[int]:
    return int(x) if x.isdigit() else wire_map.get(x)
  
  def parse_instruction(line: str) -> typing.Optional[tuple[str, int]]:
    if match := re.match(r'(\w+) -> (\w+)', line):
      src, dest = match.groups()
      if val := get(src):
        return dest, val
    elif match := re.match(r'NOT (\w+) -> (\w+)', line):
      src, dest = match.groups()
      if val := get(src):
        return dest, ~val & uint16max
    elif match := re.match(r'(\w+) AND (\w+) -> (\w+)', line):
      src1, src2, dest = match.groups()
      val1, val2 = get(src1), get(src2)
      if val1 and val2:
        return dest, (val1 & val2) & uint16max
    elif match := re.match(r'(\w+) OR (\w+) -> (\w+)', line):
      src1, src2, dest = match.groups()
      val1, val2 = get(src1), get(src2)
      if val1 and val2:
        return dest, (val1 | val2) & uint16max
    elif match := re.match(r'(\w+) LSHIFT (\d+) -> (\w+)', line):
      src, n, dest = match.groups()
      if val := get(src):
        return dest, (val << int(n)) & uint16max
    elif match := re.match(r'(\w+) RSHIFT (\d+) -> (\w+)', line):
      src, n, dest = match.groups()
      if val := get(src):
        return dest, (val >> int(n)) & uint16max
    else:
      return None # not calculable yet
    
  while lines:
    line = lines.popleft()
    
    result = parse_instruction(line)
    if result:
      dest, value = result
      wire_map[dest] = value
    else:
      lines.append(line) # try again later
      
    if line := instructions.readline().strip():
      lines.append(line)
  
  return wire_map

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if expected != actual:
        raise RuntimeError(f'Expected {expected} but got {actual}')
      
    # sanity
    assert_equal({'x': 1}, assemble(io.StringIO('1 -> x')))
  
    # given in order
    assert_equal({'x': 1, 'y': 2, 'z': 0}, assemble(io.StringIO('1 -> x\n2 -> y\nx AND y -> z')))
    assert_equal({'x': 1, 'y': 2, 'z': 3}, assemble(io.StringIO('1 -> x\n2 -> y\nx OR y -> z')))
    assert_equal({'x': 1, 'y': 4}, assemble(io.StringIO('1 -> x\nx LSHIFT 2 -> y')))
    assert_equal({'x': 1, 'y': 0}, assemble(io.StringIO('1 -> x\nx RSHIFT 2 -> y')))
    assert_equal({'x': 1, 'y': 65534}, assemble(io.StringIO('1 -> x\nNOT x -> y')))
    
    # give out of order
    assert_equal({'x': 1, 'y': 2, 'z': 0}, assemble(io.StringIO('x AND y -> z\n1 -> x\n2 -> y')))
    assert_equal({'x': 1, 'y': 2, 'z': 3}, assemble(io.StringIO('x OR y -> z\n1 -> x\n2 -> y')))
    assert_equal({'x': 1, 'y': 4}, assemble(io.StringIO('x LSHIFT 2 -> y\n1 -> x')))
    assert_equal({'x': 1, 'y': 0}, assemble(io.StringIO('x RSHIFT 2 -> y\n1 -> x')))
    assert_equal({'x': 1, 'y': 65534}, assemble(io.StringIO('NOT x -> y\n1 -> x')))
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    pprint.pprint(assemble(f))