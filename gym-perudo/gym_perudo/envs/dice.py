import itertools

x = [1, 2, 3, 4, 5, 6]
Dict = [(0,)]
for i in range(1,6):
    Dict += [p for p in itertools.combinations_with_replacement(x, i)]

#print(Dict)


current_dice = [1,2,2,3,5]
f = tuple(current_dice)
print(f)

print(Dict.index(f))
