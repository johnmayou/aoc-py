import argparse
import unittest
import typing
import sys
import io
import re

Replacement: typing.TypeAlias = tuple[str, str]

def find_quickest_fabrication(replacements: list[Replacement], target_molecule: str) -> int:
  rev_replacements = [(to, frm) for frm, to in replacements]
  rev_replacements.sort(key=lambda x: -len(x[0])) # longest first
  
  steps = 0
  molecule = target_molecule
  
  while molecule != 'e':
    for frm, to in rev_replacements:
      if frm in molecule:
        molecule = molecule.replace(frm, to, 1)
        steps += 1
        break
    else:
      raise RuntimeError('No replacement found!')
    
  return steps

def parse_input(stream: typing.TextIO) -> tuple[list[Replacement], str]:
  replacements: list[Replacement] = []
  
  while True:
    line = stream.readline()
    
    capture = re.match(r'(\w+) => (\w+)', line)
    if not capture:
      return replacements, stream.read().strip()
    
    m1, m2 = capture.groups()
    replacements.append((m1, m2))

class Tests(unittest.TestCase):  
  def test_find_quickest_fabrication(self):
    self.assertEqual(find_quickest_fabrication([('e', 'H'), ('e', 'O'), ('H', 'HO'), ('H', 'OH'), ('O', 'HH')], 'HOH'), 3)
    self.assertEqual(find_quickest_fabrication([('e', 'H'), ('e', 'O'), ('H', 'HO'), ('H', 'OH'), ('O', 'HH')], 'HOHOHO'), 6)
    
  def test_parse_input(self):
    self.assertEqual(
      parse_input(io.StringIO('a => b\naa => cc\n\nmolecule')),
      ([('a', 'b'), ('aa', 'cc')], 'molecule')
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      replacements, molecule = parse_input(f)
    print(find_quickest_fabrication(replacements, molecule))