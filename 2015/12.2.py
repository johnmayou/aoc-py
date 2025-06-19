import argparse
import unittest
import typing
import json
import sys
import io

JSONVAL: typing.TypeAlias = int | str | list["JSONVAL"] | dict[str, "JSONVAL"]

def count_total(stream: typing.TextIO) -> int:
  def count(val: JSONVAL) -> int:
    if isinstance(val, int):
      return val
    elif isinstance(val, str):
      return 0
    elif isinstance(val, list):
      return sum(count(v) for v in val)
    elif isinstance(val, dict): # type: ignore
      total = 0
      for v in val.values():
        if v == "red": return 0
        total += count(v)
      return total
    else:
      raise RuntimeError(f'Unexpected type ({type(val)}): {val}')
  
  return count(json.load(stream))

class Tests(unittest.TestCase):
  def test_base_cases(self):
    # empty
    self.assertEqual(0, count_total(io.StringIO('[]')))
    self.assertEqual(0, count_total(io.StringIO('[[]]')))
    self.assertEqual(0, count_total(io.StringIO('[{}]')))
    
    # str
    self.assertEqual(0, count_total(io.StringIO('["string"]')))
    self.assertEqual(0, count_total(io.StringIO('[{"string":"string"}]')))
    self.assertEqual(1, count_total(io.StringIO('["string",1]')))
    
    # array
    self.assertEqual(6, count_total(io.StringIO('[1,2,3]')))
    self.assertEqual(6, count_total(io.StringIO('[[1,2,3]]')))
    self.assertEqual(6, count_total(io.StringIO('[1,[2,3]]')))
    
    # object
    self.assertEqual(3, count_total(io.StringIO('[{"a":1,"b":2}]')))
    self.assertEqual(3, count_total(io.StringIO('[{"a":{"b":4},"c":-1}]')))
    self.assertEqual(3, count_total(io.StringIO('[1,{"a":[1,{"a":1}]}]')))
    
  def test_red_cases(self):
    self.assertEqual(6, count_total(io.StringIO('[3,"red",3]')))
    self.assertEqual(6, count_total(io.StringIO('[3,{"k1":"red","k2":1},3]')))
    self.assertEqual(8, count_total(io.StringIO('[3,{"red":1,"k":1},3]')))

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      print(count_total(f))