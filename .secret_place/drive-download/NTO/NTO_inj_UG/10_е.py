n, k = [int(i) for i in input().split()]
if k == 0:
    print(1)
else:
    pow_nums = {
        0: [0],
        1: [1],
        2: [2, 4, 8, 6],
        3: [1, 3, 9, 7],
        4: [4, 6],
        5: [5],
        6: [6],
        7: [1, 7, 9, 3],
        8: [8, 4, 2, 6],
        9: [1, 9]
    }
    n = n % 10
    if n == 0 or n == 2 or n == 4 or n == 5 or n == 6 or n == 8:
        k -= 1
    possible_nums = pow_nums[n % 10]
    pow_ind = k % len(possible_nums)
    print(possible_nums[pow_ind])

