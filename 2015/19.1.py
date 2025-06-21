import collections
import argparse
import unittest
import typing
import sys
import io
import re

Replacement: typing.TypeAlias = tuple[str, str]

class TrieNode:
  def __init__(self):
    self.children: dict[str, TrieNode] = {}
    self.is_word = False

class Trie:
  def __init__(self):
    self.root = TrieNode()
  
  def add(self, string: str) -> None:
    curr = self.root
    for ch in string:
      if ch not in curr.children:
        curr.children[ch] = TrieNode()
      curr = curr.children[ch]
    curr.is_word = True
  
  def contains(self, string: str) -> bool:
    curr = self.root
    for ch in string:
      if ch not in curr.children:
        return False
      curr = curr.children[ch]
    return curr.is_word
  
  def starts_with(self, string: str) -> bool:
    curr = self.root
    for ch in string:
      if ch not in curr.children:
        return False
      curr = curr.children[ch]
    return True

def count_generated(replacements: list[Replacement], molecule: str) -> int:
  generated: set[str] = set()
  
  replacement_map: collections.defaultdict[str, list[str]] = collections.defaultdict(list)
  for repl_from, repl_to in replacements:
    replacement_map[repl_from].append(repl_to)
  
  repl_trie = Trie()
  for repl_from, _ in replacements:
    repl_trie.add(repl_from)
  
  for i in range(len(molecule)):
    substr = molecule[i]
    substr_next_i = i + 1
    while substr_next_i <= len(molecule) and repl_trie.starts_with(substr):      
      if repl_trie.contains(substr):
        for repl in replacement_map[substr]:
          generated.add(molecule[:i] + repl + molecule[i + len(substr):])
      
      if substr_next_i < len(molecule):
        # keep building substring in case there are more replacements with this substr prefix
        substr += molecule[substr_next_i]
        substr_next_i += 1
      else:
        break
    
  return len(generated)

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
  def test_trie(self):
    trie = Trie()
    trie.add('word')
    
    # contains
    self.assertFalse(trie.contains('w'))
    self.assertFalse(trie.contains('wo'))
    self.assertFalse(trie.contains('wor'))
    self.assertTrue(trie.contains('word'))
    self.assertFalse(trie.contains('abc'))
    
    # starts_with
    self.assertTrue(trie.starts_with('w'))
    self.assertTrue(trie.starts_with('wo'))
    self.assertTrue(trie.starts_with('wor'))
    self.assertTrue(trie.starts_with('word'))
    self.assertFalse(trie.starts_with('abc'))
  
  def test_count_generated(self):
    self.assertEqual(count_generated([('H', 'HO'), ('H', 'OH'), ('O', 'HH')], 'HOH'), 4)
    self.assertEqual(count_generated([('H', 'HO'), ('H', 'OH'), ('O', 'HH')], 'HOHOHO'), 7)
    
  def test_parse_input(self):
    self.assertEqual(
      parse_input(io.StringIO('a => b\na => c\n\nmolecule')),
      ([('a', 'b'), ('a', 'c')], 'molecule')
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
    print(count_generated(replacements, molecule))