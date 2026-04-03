import sys
from itertools import combinations
database = []
db_size = 0
sup_min = 0
sup_min_freq = 0

def db_to_bin(db):
    # here, table is list of lists. e.g. database = [[1,2,3],[0,1,3]]
    # 중복된 원소가 없으니 OR 연산이 아니라 SUM으로 퉁치기 가능.
    # 각 원소 나타내기 1 << i for i.
    return [sum(1 << i for i in sub_list) for sub_list in db]
    # e.g. return [14,13]
def bilist_to_set(c_k):
    # here, c_k is the set data of all bitmasked candidates.
    # e.g. c_2 = {18, 20, 5, 6} which equals [[1, 4], [2, 4], [0, 2], [1, 2]] for ppt slide example.
    return [{i for i in range(c.bit_length()) if c & (1 << i)} for c in c_k]

def bi_to_biset(bitmask):
    # bitmask는 int, 즉 bitmask 형태로 나타낸 set. e.g. [2,16]일 경우 18.
    # binary value 리스트로 반환. e.g. 18 -> [2,16]
    return {bitmask & (1 << i) for i in range(bitmask.bit_length()) if bitmask & (1 << i)}

def  make_candidates(l_k_with_sup,k):
    # bitmask 형태로 나타나있는 l_k에서, AND 연산, 즉 set끼리의 union 된 combination들 생성
    # set으로 정의해서 중복될 수 있는 combo 제거
    possible_next_candi = {a | b for a,b in combinations(l_k_with_sup,2)}
    # 그 중 진짜 candidate들은, 길이가 k+1 인 것들.
    ###### 아니 근데 .bit_count() 써도 됨? ######
    next_candi =[x for x in possible_next_candi if x.bit_count() == (k+1)]
    # downward closure property로 최적화 시행.
    # 각 candidate 들에 대해서, 길이가 k인 모든 subset들이 L_k에 존재하는지 확인.
    # 하나라도 존재하지 않는다면, 그 candidate 제거.

    # next_candi의 list = x들 중에서,
    # l_k에 x^(1<<i), 즉 길이가 k-1인 모든 subset에 있는가를 검사. [if x & (1<<i)로 i번째 bit가 1임을 체크.]
    # 이 검사를 통과한 모든 itemset을 list로 return.
    return [x for x in next_candi if (all(x^(1 << i) in l_k_with_sup for i in range(x.bit_length()) if x & (1 << i)))]

# C_k -> L_K 함수 구현 [pruning]
def pruning(c_k):
    # here, note that c_k and database are already bitmasked form.
    # with bitmasked values, 
    # if B contains A, (A & B) == A
    # for each candidate in c_l, find their sup's.
    c_k_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_k]
    # pruning them with database and found sup.
    return {candi : sup for candi, sup in zip(c_k, c_k_sup) if sup >= sup_min_freq}


def all_association_rules(l_k_with_sup):
    asso_rule_k = []
    for fp,fp_sup in l_k_with_sup.items():
        # bin_values 는 bitmasked value(합)를 binary values(리스트)로 분리. e.g. 18 -> [2,16]
        bin_values = bi_to_biset(fp)
        # combo_half는 하나의 frequent pattern에서 나올 수 있는 중앙을 제외한 모든 조합의 절반까지 계산.
        # e.g. 15 -> 1+2+4+8 이니 combo_half for 15 = [[1,2,4,16]]
        # set의 개념으로 봤을 때, combo_half for 15 = [[{0},{1},{2},{3}]]
        combo_half = [[sum(bin_value) for bin_value in combinations(bin_values,i)] for i in range(1,(len(bin_values)-1)//2+1)]
        if not k%2 :
            #k가 짝수면... 
            middle = [sum(bin_value) for bin_value in combinations(bin_values, k//2)]
            #e.g.set 형태의 middle = [{0,1},{0,2},{0,3},{1,2},{1,3},{2,3}]
            # combination의 symmetric한 성질을 이용하자.
            #combo_half.append(middle[:k//2])
            combo_half.append(middle[:len(middle)//2])
            #e.g.set 형태의 middle = [{0,1},{0,2},{0,3}]
        # set의 개념으로 봤을 때, combo_half for 15 = [[{0},{1},{2},{3}],[{0,1},{0,2},{0,3}]]
        # 이제 미러링만 해주면 됨!
        # set 에서 - 연산을 bitmask로 구현하려면
        # e.g. 1111 - 1110 =  0001 -> 15 - 14 = 1
        # 즉, A ^ B = A - B
        # [우리는 A가 B를 포함한다는 사실을 알고 있기에 XOR로 연산해줘도 됨.]
        # Then e.g. combo_rest = [[{1,2,3},{0,2,3},{0,1,3},{0,1,2}],[{2,3},{1,3},{1,2}]]
        combo_rest = [[itemset ^ fp for itemset in combo] for combo in combo_half]
        # bi_to_set 함수를 통해서 bitmask 형태 -> set 
        # 현재 k 길이를 가진 frequent pattern들에 대해서 각 fp 마다 모든 combo를 생성 중.
        # item을 총 t[up to k//2 -1] 개 를 가지는 combo들을 combo_half에 저장,k-t개를 가지는 combo들을 combo_rest에 저장.
        # 변환시킨 후 합쳐주기.
        # 이제 계산 끝났고, output에 넣어줘야함. bitmask 해제 -> bilist_to_set 함수 재활용.
        asso_rule_k.append([[[bilist_to_set([itemset, asso_itemset]), fp_sup / db_size * 100, conf(itemset,asso_itemset)],
                             [bilist_to_set([asso_itemset, itemset]), fp_sup / db_size * 100, conf(asso_itemset,itemset)]
                             ]
            for combos_len_t,combos_len_k_t in zip(combo_half,combo_rest)
            for itemset, asso_itemset in zip(combos_len_t,combos_len_k_t)
            ])
        # Trouble Shooting : 근데 여기서 총 원소가 4개 이상인 frequent pattern의 asso_rule 을 계산 할 때,
        # 한 itemset의 총 원소 개수가 k//2 일 때 이미 미러링이 되어있음. e.g. [[{2, 4}, {1, 5}], 2], [[{1, 5}, {2, 4}], 2]
        # 미러링 안해도 이미 있음;
        # k//2 -1까지만 구하고 미러링한 후 추가, k가 짝수 일 때는 k//2인 경우 그냥 구하고 추가.
        # 추가적으로, k=2인 경우 빈 리스트에 대해서 연산 할 것 같으니 k=3일 때부터 반복문 반복 시작.

        # p.s. 그냥 이부분은 bitwise 말고 set으로 변환해서 연산 사용할 걸 그랬다... 괜히 끝까지 bitwise고집했다
    return asso_rule_k

def conf(itemset, asso_itemset):
    def sub_db(db, itemset):
    # itemset이 포함된 trans 만 db에 남겨 반환.
    # here, db and itemset are also bitmasked values.
        return [x for x in db if (x & itemset) == itemset]
    itemset_db = sub_db(database,itemset)
    return (len(sub_db(itemset_db,asso_itemset)) / len(itemset_db) * 100)


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

db_size = len(database)
sup_min_freq = sup_min * db_size
# Step 2. c_1 -> l_2까지는 직접 만들기
# 모든 원소 저장하기 -> set으로 정의해서 중복 걸러주기
all_items = set().union(*database)
# 포함관계 확인, candidate 만들 때 bitmask 형태로 하면 최적화
# all_item bitmaskied form.
c_1 = [1 << item for item in all_items]
database = db_to_bin(database)
# if B contains A, (A & B) == A
c_1_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_1]
l_1 = {candi for candi, sup in zip(c_1, c_1_sup) if sup >= sup_min_freq}
k=1
l_k_with_sup = {candi : sup for candi, sup in zip(c_1, c_1_sup) if sup >= sup_min_freq}

output = []

c_2 = make_candidates(l_k_with_sup,k)
k+=1
l_k_with_sup = pruning(c_2)
asso_rule_2 = []
for fp,fp_sup in l_k_with_sup.items():
    bin_values = bi_to_biset(fp)
    hard = [sum(bin_value) for bin_value in combinations(bin_values,1)]
    asso_rule_2.append([[bilist_to_set([hard[0],hard[1]]), fp_sup / db_size * 100, conf(hard[0],hard[1])],
                        [bilist_to_set([hard[1],hard[0]]), fp_sup / db_size * 100, conf(hard[1],hard[0])]
                        ])  
output.append([asso_rule_2])

while l_k_with_sup :
    c_k_plus_1 = make_candidates(l_k_with_sup,k)
    k += 1
    l_k_with_sup = pruning(c_k_plus_1)
    output.append(all_association_rules(l_k_with_sup))
    if not l_k_with_sup:
        break

with open(output_txt, "w", encoding="utf-8") as f:
        for k_group in output:       
            for rule_group in k_group:     
                for rule_pair in rule_group:
                    for rule in rule_pair:    
                        (item_set, associative_item_set), support, confidence = rule
                        line = f"{item_set}\t{associative_item_set}\t{support:.2f}\t{confidence:.2f}\n"
                        f.write(line)


