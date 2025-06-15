import collections
import argparse
import typing
import pprint
import sys
import io

uint16max = (1 << 16) - 1

def assemble(instructions: typing.TextIO) -> dict[str, int]:
  wire_map: dict[str, int] = {}
  lines: collections.deque[str] = collections.deque()
  lines.append(instructions.readline().strip())
  
  while lines:      
    line = lines.popleft()
    parts_str, dest_w = line.split(' -> ')
    if parts_str.isnumeric():
      wire_map[dest_w] = int(parts_str) & uint16max
    elif parts_str.startswith('NOT'):
      _, w = parts_str.split()
      if w in wire_map:
        wire_map[dest_w] = ~wire_map[w] & uint16max
      else:
        lines.append(line)
    else:
      parts = parts_str.split()
      match len(parts):
        case 1:
          w = parts[0]
          if w in wire_map:
            wire_map[dest_w] = wire_map[w]
          else:
            lines.append(line)
        case 3:
          match parts[1]:
            case 'AND':
              w1, _, w2 = parts
              if w1 in wire_map and w2 in wire_map:
                wire_map[dest_w] = (wire_map[w1] & wire_map[w2]) & uint16max
              else:
                lines.append(line)
            case 'OR':
              w1, _, w2 = parts
              if w1 in wire_map and w2 in wire_map:
                wire_map[dest_w] = (wire_map[w1] | wire_map[w2]) & uint16max
              else:
                lines.append(line)
            case 'LSHIFT':
              w, _, pos = parts
              if w in wire_map:
                wire_map[dest_w] = (wire_map[w] << int(pos)) & uint16max
              else:
                lines.append(line)
            case 'RSHIFT':
              w, _, pos = parts
              if w in wire_map:
                wire_map[dest_w] = (wire_map[w] >> int(pos)) & uint16max
              else:
                lines.append(line)
            case _:
              raise RuntimeError(f'Unexpected bitwise operator found: {parts[1]}')
        case _:
          raise RuntimeError(f'Unexpected number of parts: {parts}')
        
    if (line := instructions.readline().strip()):
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