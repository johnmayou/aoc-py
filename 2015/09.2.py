import argparse
import textwrap
import typing
import sys
import io
import re

def shortest_route_dist(stream: typing.TextIO) -> int:
  distances: dict[tuple[str, str], int] = {}
  for line in stream:
    match = re.match(r'(\w+) to (\w+) = (\d+)', line)
    if not match: raise RuntimeError(f'Expected to find match in "{line}"')
    
    place1, place2, dist = match.groups()
    distances[(place1, place2)] = int(dist)
    distances[(place2, place1)] = int(dist)
    
  cities = list(set(c for c, _ in distances.keys()))
  
  currRoute: set[str] = set()
  longest = -float('inf')
  
  def dfs(dist: int, last: typing.Optional[str] = None) -> None:
    nonlocal longest
    if len(currRoute) == len(cities):
      longest = max(longest, dist)
      return
    
    for c in cities:
      if c in currRoute: continue
      
      currRoute.add(c)
      if last:
        dfs(dist + distances[(last, c)], last=c)
      else:
        dfs(dist, last=c)
      currRoute.remove(c)
  
  dfs(0)
  return int(longest)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if actual != expected:
        raise RuntimeError(f'Expected {expected} but got {actual}')
      
    assert_equal(7, shortest_route_dist(io.StringIO(textwrap.dedent("""\
      a to b = 2
      a to c = 5
      b to c = 1"""))))
    assert_equal(7, shortest_route_dist(io.StringIO(textwrap.dedent("""\
      a to b = 5
      a to c = 2
      b to c = 1"""))))
    
    print('All tests passed!')
    sys.exit()
    
  with open('input.txt') as f:
    print(shortest_route_dist(f))