from itertools import combinations
def db_to_bin(table):
    # here, table is list of lists. e.g. database = [[1,2,3],[0,1,3]]
    # 중복된 원소가 없으니 OR 연산이 아니라 SUM으로 퉁치기 가능.
    # 각 원소 나타내기 1 << i for i.
    return [sum(1 << i for i in sub_list) for sub_list in table]
def bin_to_set(c_k):
    # here, c_k is the set data of all bitmasked candidates.
    # e.g. c_2 = {18, 20, 5, 6} which equals [[1, 4], [2, 4], [0, 2], [1, 2]] for ppt slide example.
    return [[i for i in range(c.bit_length()) if c & (1 << i)] for c in c_k]

database = [[0,2,3],[1,2,4],[0,1,2,4],[1,4]]
sup_min_freq = 2

# k 는 frequent pattern의 원소의 총 개수.
k = 5
eg = [0,1,2,3]
bi = 15
bit_values = [bi & (1 << i) for i in range(bi.bit_length()) if bi & (1 << i)]

# bi == 1111 in binary

#1. 만약 k가 짝수라면,,, e.g. k = 4
# k/2 e.g.2 까지만 combo를 다 구하고 {combo, eg - combo} 가 하나의 assocation rule.
# k/2에서 중복이 발생하니, combo 합칠 때 set 표현 사용. {{0,1}, {2,3}}
# 아니면 그냥 combo 절반만 생각해도 되나..?

#2. 만약 k가 홀수라면,,, 
# (k-1)/2 까지만 combo를 다 구하고 {combo, eg - combo} 가 하나의 assocation rule.

# set 에서 - 연산을 bitmask로 구현하려면
# e.g. 1111 - 1110 =  0001 -> 15 - 14 = 1
# 즉, A XOR B = A - B
# 우리는 A가 B를 포함한다는 사실을 알고 있기에 XOR로 연산해줘도 됨.

print([bin_to_set([bi^  sum(combo) for combo in combinations(bit_values,i)]) for i in range(1,int(k/2)+1)])
print([bin_to_set([sum(combo) for combo in combinations(bit_values,i)]) for i in range(1,int(k/2)+1)])

possible_subset_k = []
