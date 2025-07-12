import argparse
import textwrap
import unittest
import typing
import math
import sys
import io

N_GROUPS = 3

def balance(packages: list[int]) -> int:
  group_total_target = sum(packages) / N_GROUPS
  
  for size in range(1, len(packages)):
    valid_first_group: typing.Optional[list[int]] = None
    
    def first_group_dfs(
      *,
      start: int = 0,
      group_total: int = 0,
      group: list[int] = []
    ) -> None:
      nonlocal group_total_target, size, valid_first_group
      
      if len(group) == size:
        if group_total != group_total_target:
          return
        if not valid_first_group or math.prod(group) < math.prod(valid_first_group):
          valid_first_group = group.copy()
          
      for i in range(start, len(packages)):
        group.append(packages[i])
        first_group_dfs(
          start=i+1,
          group_total=group_total+packages[i],
          group=group
        )
        group.pop()
    
    first_group_dfs()
    
    if valid_first_group:
      return math.prod(valid_first_group)
    
  raise RuntimeError(f'Unable to balance packages: {packages}')

def parse_packages(stream: typing.TextIO) -> list[int]:
  packages: list[int] = []
  line = stream.readline().strip()
  while line:
    packages.append(int(line))
    line = stream.readline().strip()
  return packages

class Tests(unittest.TestCase):
  def test_balance(self):
    self.assertEqual(balance([1, 2, 3, 4, 5, 7, 8, 9, 10, 11]), 99)
  
  def test_parse_packages(self):
    self.assertEqual(
      parse_packages(io.StringIO(textwrap.dedent("""\
        1
        10
        100"""))),
      [1, 10, 100]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      packages = parse_packages(f)
    print(balance(packages))