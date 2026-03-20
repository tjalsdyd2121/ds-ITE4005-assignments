import sys
from itertools import combinations

# GOAL : find all association rules.

# predefinded values for usage in some functions.
database = []
freq_pat = []
sup_min = 0
sup_min_freq = 0




# 각 transaction은 중복된 elememt를 가지지 않는다는 점을 활용해 각 transaction을 정수로 나타내기
def db_to_bin(table):
    # here, table is list of lists. e.g. database = [[1,2,3],[0,1,3]]
    # 중복된 원소가 없으니 OR 연산이 아니라 SUM으로 퉁치기 가능.
    # 각 원소 나타내기 1 << i for i.
    return [sum(1 << i for i in sub_list) for sub_list in table]

# bitmask를 다시 set 형태로 복원.  
def bin_to_set(c_k):
    # here, c_k is the set data of all bitmasked candidates.
    # e.g. c_2 = {18, 20, 5, 6} which equals [[1, 4], [2, 4], [0, 2], [1, 2]] for ppt slide example.
    return [[i for i in range(c.bit_length()) if c & (1 << i)] for c in c_k]

# 3-1. L_k -> C_k+1 함수 구현 [self-joining + applying downward closure property.]

# L_k 에 있는 frequent pattern만 가지고 다음 C_k+1 생성.
# here, l_k is already bitmasked form.
def  make_candidates(l_k,k):
    # bitmask 형태로 나타나있는 l_k에서, AND 연산, 즉 set끼리의 union 된 combination들 생성
    # set으로 정의해서 중복될 수 있는 combo 제거
    possible_next_candi = {a | b for a,b in combinations(l_k,2)}
    # 그 중 진짜 candidate들은, 길이가 k+1 인 것들.
    next_candi =[x for x in possible_next_candi if x.bit_count() == (k+1)]
    # downward closure property로 최적화 시행.
    # 각 candidate 들에 대해서, 길이가 k인 모든 subset들이 L_k에 존재하는지 확인.
    # 하나라도 존재하지 않는다면, 그 candidate 제거.

    # next_candi의 list = x들 중에서,
    # l_k에 x^(1<<i), 즉 길이가 k-1인 모든 subset에 있는가를 검사. [if x & (1<<i)로 i번째 bit가 1임을 체크.]
    # 이 검사를 통과한 모든 itemset을 list로 return.
    return [x for x in next_candi if (all(x^(1 << i) in l_k for i in range(x.bit_length()) if x & (1 << i)))]

# C_k -> L_K 함수 구현 [pruning]
def pruning(c_k):
    # here, note that c_k and database are already bitmasked form.
    # with bitmasked values, 
    # if B contains A, (A & B) == A
    # for each candidate in c_l, find their sup's.
    c_k_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_k]
    # pruning them with database and found sup.
    return {candi for candi, sup in zip(c_k, c_k_sup) if sup >= sup_min_freq}


# Step 1. input.txt 받아오기
sup_min = int(sys.argv[1]) / 100 # support as prob.
input_txt = sys.argv[2]
output_txt = sys.argv[3]
try:
    with open(input_txt, 'r') as f:
        for line in f:
            trans = line.strip().split()
            itemset = [int(x) for x in trans]
            database.append(itemset)
except FileNotFoundError:
    sys.exit()

# some useful values.
db_size = len(database)
sup_min_freq = sup_min * db_size
# Step 2. c_1 -> l_1까지는 직접 만들기
# 모든 원소 저장하기 -> set으로 정의해서 중복 걸러주기
all_items = set().union(*database)
# 포함관계 확인, candidate 만들 때 bitmask 형태로 하면 최적화
# if B contains A, (A & B) == A
# all_item bitmaskied form.
c_1 = [1 << item for item in all_items]
# bitmasking database to calculate.
database = db_to_bin(database)
# if B contains A, (A & B) == A
c_1_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_1]
l_1 = {candi for candi, sup in zip(c_1, c_1_sup) if sup >= sup_min_freq}
# Step 3. find all frequent patterns.
l_k = l_1
freq_pat.append(l_k)
k=1
while l_k :
    c_k1 = make_candidates(l_k,k)
    k += 1
    l_k = pruning(c_k1)
    freq_pat.append(l_k)
print([bin_to_set(c_k) for c_k in freq_pat])

# With 