import argparse
import unittest
import textwrap
import typing
import sys
import io
import re

def find_max_happiness(stream: typing.TextIO) -> int:
  happiness: dict[tuple[str, str], int] = {}
  for line in stream:
    match = re.match(r'(\w+) would (\w+) (\d+) happiness units by sitting next to (\w+).', line)
    if not match:
      raise RuntimeError(f'Invalid format for line: "{line}"')
    
    person, gain_lose, units, nei = match.groups()
    happiness[(person, nei)] = int(units) if gain_lose == 'gain' else -int(units)
    
  people = list(set(p for p, _ in happiness))
  
  # add self
  for p in people:
    happiness[(p, 'you')] = 0
    happiness[('you', p)] = 0
  people.append('you')
  
  seated: set[str] = set()
  seating: list[typing.Optional[str]] = [None] * len(people)
  max_happiness = -float('inf')
  
  def dfs(i: int) -> None:
    nonlocal max_happiness
    if i >= len(seating):
      happ = 0
      
      # find current happiness iteratively two people at a time (person -> right neighbor and person <- right neighbor)
      for p in range(len(seating)):
        person = seating[p]
        if not person:
          raise RuntimeError(f'No person sitting at {p}: {seating}')
        
        nei_right = seating[(p + 1) % len(seating)]
        if not nei_right:
          raise RuntimeError(f'No person sitting to the right of {p}: {seating}')
        
        happ += happiness[(person, nei_right)] + happiness[(nei_right, person)]
        
        # if there are only two people, we have already calculated the total happiness after the first iteration
        if len(seating) == 2:
          break
        
      max_happiness = max(max_happiness, happ)
      return
      
    for p in people:
      if p in seated:
        continue
      
      seating[i] = p
      seated.add(p)
      dfs(i + 1)
      seated.remove(p)
    
  dfs(0)
  return int(max_happiness)

class Tests(unittest.TestCase):
  def test_find_max_happiness(self):
    # gain / loss
    self.assertEqual(2, find_max_happiness(io.StringIO(textwrap.dedent("""\
      a would gain 1 happiness units by sitting next to b.
      b would gain 1 happiness units by sitting next to a."""))))
    self.assertEqual(-2, find_max_happiness(io.StringIO(textwrap.dedent("""\
      a would lose 1 happiness units by sitting next to b.
      b would lose 1 happiness units by sitting next to a."""))))
    self.assertEqual(0, find_max_happiness(io.StringIO(textwrap.dedent("""\
      a would gain 1 happiness units by sitting next to b.
      b would lose 1 happiness units by sitting next to a."""))))
    
    # finding max
    self.assertEqual(6, find_max_happiness(io.StringIO(textwrap.dedent("""\
      a would gain 1 happiness units by sitting next to b.
      a would lose 1 happiness units by sitting next to c.
      a would gain 1 happiness units by sitting next to d.
      b would gain 1 happiness units by sitting next to a.
      b would gain 1 happiness units by sitting next to c.
      b would lose 1 happiness units by sitting next to d.
      c would lose 1 happiness units by sitting next to a.
      c would gain 1 happiness units by sitting next to b.
      c would gain 1 happiness units by sitting next to d.
      d would gain 1 happiness units by sitting next to a.
      d would lose 1 happiness units by sitting next to b.
      d would gain 1 happiness units by sitting next to c."""))))

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      print(find_max_happiness(f))