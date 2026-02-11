from itertools import combinations

x, k = map(int, input().split())
n = int(input())
c = list(map(int, input().split()))
c.sort()
min_k = []
for c_i in c:
    if c_i < k:
        min_k.append(c_i)
s = 0
br = False
for i in range(1, len(min_k)):
    for j in combinations(min_k, i):
        if s < sum(j) < k:
            s = sum(j)
        if sum(j) == k:
            s = k
            br = True
            break
    if br:
        break

if sum(c) - s <= x:
    print(x - (sum(c) - s))
else:
    print(-1)
