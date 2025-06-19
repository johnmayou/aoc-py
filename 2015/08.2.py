import argparse
import typing
import sys
import io
import re

def next_line_encode_ch_diff(stream: typing.TextIO) -> typing.Optional[int]:
  line = stream.readline().strip()
  if not line: return None
  
  newline = re.sub(r'\\', r'\\\\', line)
  newline = re.sub(r'"', '\\"', newline)
  return 2 + len(newline) - len(line)
  
  
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if actual != expected:
        raise RuntimeError(f'Expected {expected} but got {actual}')
    
    assert_equal(4, next_line_encode_ch_diff(io.StringIO('""')))
    assert_equal(4, next_line_encode_ch_diff(io.StringIO('"abc"')))
    assert_equal(6, next_line_encode_ch_diff(io.StringIO('"aaa\\"aaa"')))
    assert_equal(5, next_line_encode_ch_diff(io.StringIO('"\\x27"')))
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    diff_total = 0
    while diff := next_line_encode_ch_diff(f):
      diff_total += diff
    print(diff_total)