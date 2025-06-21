import argparse
import unittest
import typing
import sys
import io

def count_combinations(containers: list[int], *, total_liters: int) -> int:
  combinations = 0
  
  def dfs(i: int, curr_liters: int = 0) -> None:
    nonlocal combinations
    
    if curr_liters > total_liters:
      return
    if curr_liters == total_liters:
      combinations += 1
      return
    
    for j in range(i, len(containers)):
      dfs(j + 1, curr_liters + containers[j])
  
  dfs(0)
  return combinations

def parse_containers(stream: typing.TextIO) -> list[int]:
  containers: list[int] = []
  
  line = stream.readline()
  while line:
    containers.append(int(line))
    line = stream.readline()
  
  return containers

class Tests(unittest.TestCase):
  def test_count_combinations(self):
    self.assertEqual(count_combinations([1, 2, 3], total_liters=1), 1)
    self.assertEqual(count_combinations([1, 2, 3], total_liters=2), 1)
    self.assertEqual(count_combinations([1, 2, 3], total_liters=3), 2)
    self.assertEqual(count_combinations([1, 2, 3], total_liters=6), 1)
  
  def test_parse_containers(self):
    self.assertEqual(parse_containers(io.StringIO('1\n2\n3')), [1, 2, 3])

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      containers = parse_containers(f)
    print(count_combinations(containers, total_liters=150))