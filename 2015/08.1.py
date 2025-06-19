import argparse
import typing
import sys
import io

def next_line_raw_to_memory_ch_diff(stream: typing.TextIO) -> typing.Optional[int]:
  line = stream.readline().strip()
  return len(line) - len(eval(line)) if line else None
  
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    assert next_line_raw_to_memory_ch_diff(io.StringIO('""')) == 2
    assert next_line_raw_to_memory_ch_diff(io.StringIO('"abc"')) == 2
    assert next_line_raw_to_memory_ch_diff(io.StringIO('"aaa\\"aaa"')) == 3
    assert next_line_raw_to_memory_ch_diff(io.StringIO('"\\x27"')) == 5
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    diff_total = 0
    while diff := next_line_raw_to_memory_ch_diff(f):
      diff_total += diff
    print(diff_total)