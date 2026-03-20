from itertools import combinations
database = [[0,2,3],[1,2,4],[0,1,2,4],[1,4]]
sup_min = 0
sup_min_freq = 0

def db_to_bin(table):
    # here, table is list of lists. e.g. database 
    return [sum(1 << i for i in sub_list) for sub_list in table]

def bin_to_db(bin_table):
    return [[i for i in range(mask.bit_length()) if mask & (1 << i)] for mask in bin_table]

def  make_candidates(l_k,k):
    # bitmask 형태로 나타나있는 l_k에서, AND 연산, 즉 set끼리의 union 된 combination들 생성
    # set으로 정의해서 중복될 수 있는 combo 제거
    possible_next_candi = {a | b for a,b in combinations(l_k,2)}
    # 그 중 진짜 candidate들은, 길이가 k+1 인 것들.
    ###### 아니 근데 .bit_count() 써도 됨? ######
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

db_size = len(database) # 4
sup_min_freq = 2
# Step 2. c_1 -> l_2까지는 직접 만들기
# 모든 원소 저장하기 -> set으로 정의해서 중복 걸러주기
all_items = set().union(*database)
# 포함관계 확인, candidate 만들 때 bitmask 형태로 하면 최적화
# if B contains A, (A & B) == A
# all_item bitmaskied form.
c_1 = [1 << item for item in all_items]
database = db_to_bin(database)
# if B contains A, (A & B) == A
c_1_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_1]
l_1 = {candi for candi, sup in zip(c_1, c_1_sup) if sup >= sup_min_freq}

l_k = l_1
k=1
freq_pat = []
freq_pat.append(l_k)
while not (len(l_k) == 1):
    c_k1 = make_candidates(l_k,k)
    k += 1
    l_k = pruning(c_k1)
    freq_pat.append(l_k)


print(freq_pat)
bin_to_db(freq_pat[1])
print([bin_to_db(fq) for fq in freq_pat])