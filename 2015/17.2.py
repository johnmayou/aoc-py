import argparse
import unittest
import typing
import sys
import io

class CountMinContainerCombinationsResult(typing.TypedDict):
  count: int
  combinations: int

def count_min_container_combinations(containers: list[int], *, total_liters: int) -> CountMinContainerCombinationsResult:
  min_container_count = float('inf')
  min_container_combinations = 0
  
  def dfs(i: int, curr_container_count: int = 0, curr_liters: int = 0) -> None:
    nonlocal min_container_count, min_container_combinations
    
    if curr_liters > total_liters:
      return
    if curr_liters == total_liters:
      if curr_container_count < min_container_count:
        min_container_count = curr_container_count
        min_container_combinations = 1
      elif curr_container_count == min_container_count:
        min_container_combinations += 1
      return
    
    for j in range(i, len(containers)):
      dfs(
        j + 1,
        curr_container_count=curr_container_count + 1,
        curr_liters=curr_liters + containers[j]
      )
  
  dfs(0)
  return {
    'count': int(min_container_count),
    'combinations': min_container_combinations
  }

def parse_containers(stream: typing.TextIO) -> list[int]:
  containers: list[int] = []
  
  line = stream.readline()
  while line:
    containers.append(int(line))
    line = stream.readline()
  
  return containers

class Tests(unittest.TestCase):
  def test_count_min_container_combinations(self):
    self.assertEqual(count_min_container_combinations([1, 2, 3], total_liters=1), {'count': 1, 'combinations': 1})
    self.assertEqual(count_min_container_combinations([1, 2, 3], total_liters=2), {'count': 1, 'combinations': 1})
    self.assertEqual(count_min_container_combinations([1, 2, 3], total_liters=3), {'count': 1, 'combinations': 1})
    self.assertEqual(count_min_container_combinations([1, 2, 3], total_liters=6), {'count': 3, 'combinations': 1})
  
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
    result = count_min_container_combinations(containers, total_liters=150)
    print(f'count: {result['count']}')
    print(f'combinations: {result['combinations']}')