from itertools import combinations
def db_to_bin(table):
    # here, table is list of lists. e.g. database = [[1,2,3],[0,1,3]]
    # 중복된 원소가 없으니 OR 연산이 아니라 SUM으로 퉁치기 가능.
    # 각 원소 나타내기 1 << i for i.
    return [sum(1 << i for i in sub_list) for sub_list in table]
def bin_to_set(c_k):
    # here, c_k is the set data of all bitmasked candidates.
    # e.g. c_2 = {18, 20, 5, 6} which equals [[1, 4], [2, 4], [0, 2], [1, 2]] for ppt slide example.
    return [{i for i in range(c.bit_length()) if c & (1 << i)} for c in c_k]

def all_association_rules(l_k):
    for fp in l_k:
        # bin_values 는 bitmasked value를 binary values로 분리. e.g. 18 -> [2,16]
        bin_values = [fp & (1 << i) for i in range(fp.bit_length()) if fp & (1 << i)]
        # combo는 하나의 frequent pattern에서 나올 수 있는 모든 조합의 절반
        # e.g. 21 -> 1+4+16 이니 combo for 21 = [{1,4,16},{5,17,20}]
        # set의 개념으로 봤을 때, combo for 21 = [[{0},{2},{4}],[{0,2},{0,4},{2,4}]]
        combo_half = [[sum(bin_value) for bin_value in combinations(bin_values,i)] for i in range(1,(len(bin_values)//2)+1)]
        # set 에서 - 연산을 bitmask로 구현하려면
        # e.g. 1111 - 1110 =  0001 -> 15 - 14 = 1
        # 즉, A ^ B = A - B
        # [우리는 A가 B를 포함한다는 사실을 알고 있기에 XOR로 연산해줘도 됨.]
        combo_rest = [[itemset ^ fp for itemset in combo] for combo in combo_half]
        
        print(bin_to_set([fp]))
        print(combo_half)
        #print(bin_to_set(combo) for combo in combo_half)
        print()

        
    return 0
    #return combo
database = [[0,2,3],[1,2,4],[0,1,2,4],[1,4]]
sup_min_freq = 2

# k 는 frequent pattern의 원소의 총 개수.

# bi == 1111 in binary

#1. 만약 k가 짝수라면,,, e.g. k = 4
# k/2 e.g.2 까지만 combo를 다 구하고 {combo, eg - combo} 가 하나의 assocation rule.
# k/2에서 중복이 발생하니, combo 합칠 때 set 표현 사용. {{0,1}, {2,3}}
# 아니면 그냥 combo 절반만 생각해도 되나..?
# 근데 그냥 case 안나누고 통짜로 가려면 set으로 정의하는게 좋으려나
# 어짜피 output 형태도 {} 필요해서 set of set이 좋을지도

#2. 만약 k가 홀수라면,,, 
# (k-1)/2 까지만 combo를 다 구하고 {combo, eg - combo} 가 하나의 assocation rule.



#print([bin_to_set([bi^sum(combo) for combo in combinations(bit_values,i)]) for i in range(1,int(k/2)+1)])
#print([bin_to_set([sum(combo) for combo in combinations(bit_values,i)]) for i in range(1,int(k/2)+1)])

#11111 = 
l_2 = {18,20,21,61}
print(all_association_rules(l_2))
