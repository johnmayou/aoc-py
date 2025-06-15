import argparse
import typing
import pprint
import sys
import io

def assemble(instructions: typing.TextIO) -> dict[str, int]:
  wire_map: dict[str, int] = {}
  
  line = instructions.readline().strip()
  while line:
    parts_str, dest_w = line.split(' -> ')
    if parts_str.isnumeric():
      wire_map[dest_w] = int(parts_str)
    elif parts_str.startswith('NOT'):
      _, w = parts_str.split()
      wire_map[dest_w] = ~int(wire_map[w])
    else:
      parts = parts_str.split()
      if len(parts) != 3:
        raise RuntimeError(f'Unexpected number of parts, expected 3: {parts}')
      match parts[1]:
        case 'AND':
          w1, _, w2 = parts
          wire_map[dest_w] = wire_map[w1] & wire_map[w2]
        case 'OR':
          w1, _, w2 = parts
          wire_map[dest_w] = wire_map[w1] | wire_map[w2]
        case 'LSHIFT':
          w, _, pos = parts
          wire_map[dest_w] = wire_map[w] << int(pos)
        case 'RSHIFT':
          w, _, pos = parts
          wire_map[dest_w] = wire_map[w] >> int(pos)
        case _:
          raise RuntimeError(f'Unexpected bitwise operator found: {parts[1]}')
      
    line = instructions.readline().strip()
    
  return wire_map

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if expected != actual:
        raise RuntimeError(f'Expected {expected} but got {actual}')
  
    assert_equal({'x': 1}, assemble(io.StringIO('1 -> x')))
    assert_equal({'x': 1, 'y': 2, 'z': 0}, assemble(io.StringIO('1 -> x\n2 -> y\nx AND y -> z')))
    assert_equal({'x': 1, 'y': 2, 'z': 3}, assemble(io.StringIO('1 -> x\n2 -> y\nx OR y -> z')))
    assert_equal({'x': 1, 'y': 4}, assemble(io.StringIO('1 -> x\nx LSHIFT 2 -> y')))
    assert_equal({'x': 1, 'y': 0}, assemble(io.StringIO('1 -> x\nx RSHIFT 2 -> y')))
    assert_equal({'x': 1, 'y': -2}, assemble(io.StringIO('1 -> x\nNOT x -> y')))
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    pprint.pprint(assemble(f))