import argparse
import typing
import sys

def look_and_say(digits: str) -> str:
  newStr = ''
  
  lastDigit: typing.Optional[str] = None
  lastDigitCount = 0
  for digit in digits:
    if lastDigit and digit == lastDigit:
      lastDigitCount += 1
      continue
    
    if lastDigit:
      newStr += f'{lastDigitCount}{lastDigit}'
    lastDigit = digit
    lastDigitCount = 1
    
  if lastDigit:
    newStr += f'{lastDigitCount}{lastDigit}'
    
  return newStr

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if actual != expected:
        raise RuntimeError(f'Expected {expected} but got {actual}')
    
    assert_equal('11', look_and_say('1'))
    assert_equal('21', look_and_say('11'))
    assert_equal('1211', look_and_say('21'))
    assert_equal('111221', look_and_say('1211'))
    assert_equal('312211', look_and_say('111221'))
    
    print('All tests passed!')
    sys.exit()

  curr = '3113322113'
  for _ in range(50):
    curr = look_and_say(curr)
  print(len(curr))