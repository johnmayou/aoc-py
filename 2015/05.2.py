nice_ctn = 0
with open('input.txt') as f:
  s = f.readline().strip()
  while s:
    pair_repeat = False
    pairs_seen: list[str] = []
    repeat_around_1_letter = False
    for i in range(len(s)):
      if i > 0 and not pair_repeat:
        pair = s[i-1] + s[i]
        pair_repeat = any([pairs_seen[p_i] == pair for p_i in range(0, len(pairs_seen)-1)])
        pairs_seen.append(pair)
      if i + 2 < len(s) and s[i] == s[i+2]:
        repeat_around_1_letter = True
      if pair_repeat and repeat_around_1_letter:
        nice_ctn += 1
        break
    s = f.readline().strip()
print(nice_ctn)