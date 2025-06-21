import argparse
import unittest
import typing
import sys
import io
import re

MFCSAM = {
  'children': 3,
  'cats': 7,
  'samoyeds': 2,
  'pomeranians': 3,
  'akitas': 0,
  'vizslas': 0,
  'goldfish': 5,
  'trees': 3,
  'cars': 2,
  'perfumes': 1,
}

class Sue(typing.TypedDict):
  number: int
  children: typing.NotRequired[int]
  cats: typing.NotRequired[int]
  samoyeds: typing.NotRequired[int]
  pomeranians: typing.NotRequired[int]
  akitas: typing.NotRequired[int]
  vizslas: typing.NotRequired[int]
  goldfish: typing.NotRequired[int]
  trees: typing.NotRequired[int]
  cars: typing.NotRequired[int]
  perfumes: typing.NotRequired[int]
  
def guess_sue(sues: list[Sue], gift: dict[str, int]) -> float:
  guess_num: typing.Optional[int] = None
  guess_score = -float('inf')
  
  for sue in sues:
    score = score_sue(sue, gift)
    if score > guess_score:
      guess_num = sue['number']
      guess_score = score
      
  if not guess_num:
    raise RuntimeError('No guess for sue!')
  
  return guess_num

def score_sue(sue: Sue, gift: dict[str, int]) -> float:
  score = 0
  
  for attr, val in sue.items():
    if attr == 'number':
      continue
    
    val = typing.cast(int, val)
    gift_val = gift[attr]
    match attr:
      case 'cats' | 'trees':
        # sue val must be greater than
        if val > (gift['cats'] if attr == 'cats' else gift['trees']):
          score += 1
      case 'pomeranians' | 'goldfish':
        # sue val must be less than
        if val < (gift['pomeranians'] if attr == 'pomeranians' else gift['goldfish']):
          score += 1
      case 'children' | 'samoyeds' | 'akitas' | 'vizslas' | 'cars' | 'perfumes':
        if val == gift_val:
          score += 1
        elif gift_val - 1 <= val <= gift_val + 1:
          score += 0.8
        elif gift_val - 2 <= val <= gift_val + 2:
          score += 0.6
      case _:
        raise RuntimeError(f'Unexpected attr: {attr}')
      
  return score

def parse_sues(stream: typing.TextIO) -> list[Sue]:
  sues: list[Sue] = []
  
  line = stream.readline()
  while line:
    num_capture = re.match(r'Sue (\d+):', line)
    if not num_capture: raise RuntimeError(f'Could not determine sue number: {line}')
    
    sue: Sue = {'number': int(num_capture.groups()[0])}

    attr_part = line[line.index(':') + 1:]
    if attr_part:
      for attr_str in attr_part.split(','):
        attr, val = attr_str.split(':')
        sue[attr.strip()] = int(val.strip())
        
    sues.append(sue)
    
    line = stream.readline()
    
  return sues

class Tests(unittest.TestCase):
  def test_score_sue(self):
    # same value = 1 point
    self.assertEqual(score_sue({'number': 1, 'children': 5}, {'children': 5}), 1)
    
    # within 1 = 0.8 points
    self.assertEqual(score_sue({'number': 1, 'children': 4}, {'children': 5}), 0.8)
    self.assertEqual(score_sue({'number': 1, 'children': 6}, {'children': 5}), 0.8)
    
    # within 2 = 0.6 points
    self.assertEqual(score_sue({'number': 1, 'children': 3}, {'children': 5}), 0.6)
    self.assertEqual(score_sue({'number': 1, 'children': 7}, {'children': 5}), 0.6)
    
    # default = 0 points
    self.assertEqual(score_sue({'number': 1, 'children': 9}, {'children': 5}), 0)
  
  def test_parse_sues(self):
    # no attributes
    self.assertEqual(
      parse_sues(io.StringIO('Sue 1:')),
      [{'number': 1}]
    )
    
    # all attributes
    self.assertEqual(
      parse_sues(io.StringIO('Sue 1: children: 1, cats: 2, samoyeds: 3, pomeranians: 4, akitas: 5, vizslas: 6, goldfish: 7, trees: 8, cars: 9, perfumes: 10')),
      [{'number': 1, 'children': 1, 'cats': 2, 'samoyeds': 3, 'pomeranians': 4, 'akitas': 5, 'vizslas': 6, 'goldfish': 7, 'trees': 8, 'cars': 9, 'perfumes': 10}]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      sues = parse_sues(f)
    print(guess_sue(sues, gift=MFCSAM))