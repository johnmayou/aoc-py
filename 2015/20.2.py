import argparse
import unittest
import typing
import sys

def lowest_house_number(target: int, multiplier: int, delivery_limit: typing.Optional[int], house_limit: int) -> int:  
  presents = [0] * (house_limit + 1)
  
  for elf in range(1, house_limit + 1):
    deliveries = 0
    for house in range(elf, house_limit + 1, elf):
      presents[house] += elf
      deliveries += 1
      if delivery_limit and deliveries >= delivery_limit:
        break
      
  for house, total in enumerate(presents):
    if total * multiplier >= target:
      return house
    
  raise RuntimeError('No house meets target with upper bound given')

class Tests(unittest.TestCase):
  def test_lowest_house_number(self):
    # exact (from prompt)
    self.assertEqual(lowest_house_number(10, multiplier=10, delivery_limit=None, house_limit=100), 1)
    self.assertEqual(lowest_house_number(30, multiplier=10, delivery_limit=None, house_limit=100), 2)
    self.assertEqual(lowest_house_number(40, multiplier=10, delivery_limit=None, house_limit=100), 3)
    self.assertEqual(lowest_house_number(70, multiplier=10, delivery_limit=None, house_limit=100), 4)
    self.assertEqual(lowest_house_number(60, multiplier=10, delivery_limit=None, house_limit=100), 4)
    self.assertEqual(lowest_house_number(120, multiplier=10, delivery_limit=None, house_limit=100), 6)
    self.assertEqual(lowest_house_number(80, multiplier=10, delivery_limit=None, house_limit=100), 6)
    self.assertEqual(lowest_house_number(150, multiplier=10, delivery_limit=None, house_limit=100), 8)
    self.assertEqual(lowest_house_number(130, multiplier=10, delivery_limit=None, house_limit=100), 8)
    
    # make sure we're using "at least" logic
    self.assertEqual(lowest_house_number(11, multiplier=10, delivery_limit=None, house_limit=100), 2)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    print(lowest_house_number(33100000, multiplier=11, delivery_limit=50, house_limit=1_000_000))