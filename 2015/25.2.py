import argparse
import unittest
import sys

def calc_next_code(code: int) -> int:
  return (code * 252533) % 33554393

def calc_step(row: int, col: int) -> int:
  step = r = c = 1
  while r != row or c != col:
    if r == 1:
      r = c + 1
      c = 1
    else:
      r -= 1
      c += 1
    step += 1
  return step

class Tests(unittest.TestCase):
  def test_calc_next_code(self):
    self.assertEqual(calc_next_code(20151125), 31916031)
    self.assertEqual(calc_next_code(31916031), 18749137)
    self.assertEqual(calc_next_code(18749137), 16080970)
    self.assertEqual(calc_next_code(16080970), 21629792)
    self.assertEqual(calc_next_code(21629792), 17289845)
    
  def test_calc_step(self):
    self.assertEqual(calc_step(1, 1), 1)
    self.assertEqual(calc_step(2, 1), 2)
    self.assertEqual(calc_step(1, 2), 3)
    self.assertEqual(calc_step(3, 1), 4)
    self.assertEqual(calc_step(2, 2), 5)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]], buffer=False)
  else:
    code = 20151125 # 1,1
    for i in range(calc_step(row=2981, col=3075)-1):
      code = calc_next_code(code)
    print(code)