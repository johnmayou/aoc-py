import functools
import operator
import argparse
import unittest
import typing
import sys
import io
import re

SCORE_PROPERTIES = ['capacity', 'durability', 'flavor', 'texture']

class Ingredient(typing.TypedDict):
  name: str
  capacity: int
  durability: int
  flavor: int
  texture: int
  calories: int

def find_max_score_recipe(
  ingredients: list[Ingredient],
  total_tsps: int,
  total_calories: int
) -> tuple[int, dict[str, int]]:
  ingredient_map = {i['name']: i for i in ingredients}
  
  max_recipe: dict[str, int] = {}
  max_score = -float('inf')
  
  curr_recipe: dict[str, int] = {i['name']: 0 for i in ingredients}
  
  def dfs(i: int, curr_tsps: int = 0, curr_calories: int = 0) -> None:
    nonlocal max_recipe, max_score
    
    # prune since we're going for exact calorie count
    if curr_calories > total_calories:
      return
    
    if i == len(ingredients) - 1:
      # assign remaining since we only have one ingredient left
      remaining = total_tsps - curr_tsps
      curr_recipe[ingredients[i]['name']] = remaining
      curr_calories += ingredients[i]['calories'] * remaining
      if curr_calories != total_calories:
        return
      
      # calculate score
      scores: dict[str, int] = {}
      calories = 0
      for iname, tsps in curr_recipe.items():
        ingredient = ingredient_map[iname]
        for prop in SCORE_PROPERTIES:
          scores[prop] = scores.get(prop, 0) + ingredient[prop] * tsps
        calories += ingredient['calories'] * tsps
      score: int = functools.reduce(operator.mul, [max(0, s) for s in scores.values()])
      
      # update max if needed
      if score > max_score:
        max_recipe = curr_recipe.copy()
        max_score = score
      
      return
    
    for tsps in range(total_tsps - curr_tsps + 1):
      curr_recipe[ingredients[i]['name']] = tsps
      dfs(
        i=i + 1,
        curr_tsps=curr_tsps + tsps,
        curr_calories=curr_calories + ingredients[i]['calories'] * tsps
      )
  
  dfs(0)
  return int(max_score), max_recipe

def parse_ingredients(stream: typing.TextIO) -> list[Ingredient]:
  ingredients: list[Ingredient] = []
  
  line = stream.readline()
  while line:
    capture = re.match(r'(\w+): capacity (\-?\d+), durability (\-?\d+), flavor (\-?\d+), texture (\-?\d+), calories (\-?\d+)', line)
    if not capture: raise RuntimeError(f'Invalid line format, unable to parse: "{line}"')
    
    name, capacity, durability, flavor, texture, calories = capture.groups()
    ingredients.append(Ingredient(
      name=name,
      capacity=int(capacity),
      durability=int(durability),
      flavor=int(flavor),
      texture=int(texture),
      calories=int(calories),
    ))
    
    line = stream.readline()
  
  return ingredients

class Tests(unittest.TestCase):
  def test_find_max_score_recipe(self):
    # unit cases
    self.assertEqual(
      find_max_score_recipe([
        Ingredient(name='Name', capacity=1, durability=1, flavor=1, texture=1, calories=10),
      ], total_tsps=10, total_calories=100),
      (10000, {'Name': 10}),
    )
    self.assertEqual(
      find_max_score_recipe([
        Ingredient(name='Name 1', capacity=1, durability=1, flavor=1, texture=1, calories=10),
        Ingredient(name='Name 2', capacity=2, durability=2, flavor=2, texture=2, calories=10),
      ], total_tsps=10, total_calories=100),
      (160000, {'Name 1': 0, 'Name 2': 10}),
    )
    
    # real world
    self.assertEqual(
      find_max_score_recipe([
        Ingredient(name='Butterscotch', capacity=-1, durability=-2, flavor=6, texture=3, calories=8),
        Ingredient(name='Cinnamon', capacity=2, durability=3, flavor=-2, texture=-1, calories=3),
      ], total_tsps=100, total_calories=500),
      (57600000, {'Cinnamon': 60, 'Butterscotch': 40})
    )
  
  def test_parse_ingredients(self):
    # positive
    self.assertEqual(
      parse_ingredients(io.StringIO('Name: capacity 1, durability 1, flavor 1, texture 1, calories 10')),
      [Ingredient(name='Name', capacity=1, durability=1, flavor=1, texture=1, calories=10)]
    )
    
    # negative
    self.assertEqual(
      parse_ingredients(io.StringIO('Name: capacity -1, durability -1, flavor -1, texture -1, calories -10')),
      [Ingredient(name='Name', capacity=-1, durability=-1, flavor=-1, texture=-1, calories=-10)]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]], verbosity=2)
  else:
    with open('input.txt') as f:
      ingredients = parse_ingredients(f)
    score, recipe = find_max_score_recipe(ingredients, total_tsps=100, total_calories=500)
    print(f'score: {score}')
    print(f'recipe: {recipe}')