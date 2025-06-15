nice = 0
with open('input.txt') as f:
  s = f.readline().strip()
  while s:
    vowels = 0
    rtwice = False
    passed = True
    for i in range(len(s)):
      if s[i] == 'a' or s[i] == 'e' or s[i] == 'i' or s[i] == 'o' or s[i] == 'u':
        vowels += 1
      if i > 0 and s[i] == s[i-1]:
        rtwice = True
      if i + 1 < len(s) and (
        (s[i] == 'a' and s[i+1] == 'b') or
        (s[i] == 'c' and s[i+1] == 'd') or
        (s[i] == 'p' and s[i+1] == 'q') or
        (s[i] == 'x' and s[i+1] == 'y')
      ):
        passed = False
        break
    if passed and vowels >= 3 and rtwice:
      nice += 1
    s = f.readline().strip()
print(nice)