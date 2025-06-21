import argparse
import unittest
import sys

DEFAULT_UPPER_BOUND = 1_000_000

def lowest_house_number(target: int, upper_bound: int = DEFAULT_UPPER_BOUND) -> int:
  presents = [0] * (upper_bound + 1)
  
  for elf in range(1, upper_bound + 1):
    for house in range(elf, upper_bound + 1, elf):
      presents[house] += elf
      
  for house, total in enumerate(presents):
    if total * 10 >= target:
      return house
    
  raise RuntimeError('No house meets target with upper bound given')

class Tests(unittest.TestCase):
  def test_lowest_house_number(self):
    # exact (from prompt)
    self.assertEqual(lowest_house_number(10, upper_bound=100), 1)
    self.assertEqual(lowest_house_number(30, upper_bound=100), 2)
    self.assertEqual(lowest_house_number(40, upper_bound=100), 3)
    self.assertEqual(lowest_house_number(70, upper_bound=100), 4)
    self.assertEqual(lowest_house_number(60, upper_bound=100), 4)
    self.assertEqual(lowest_house_number(120, upper_bound=100), 6)
    self.assertEqual(lowest_house_number(80, upper_bound=100), 6)
    self.assertEqual(lowest_house_number(150, upper_bound=100), 8)
    self.assertEqual(lowest_house_number(130, upper_bound=100), 8)
    
    # make sure we're using "at least" logic
    self.assertEqual(lowest_house_number(11, upper_bound=100), 2)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    print(lowest_house_number(33100000))