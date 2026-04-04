import sys
from itertools import combinations
database = []
db_size = 0
sup_min = 0
sup_min_freq = 0

def db_to_bin(db):

    return [sum(1 << i for i in sub_list) for sub_list in db]
def bilist_to_set(c_k):
    return [{i for i in range(c.bit_length()) if c & (1 << i)} for c in c_k]

def bi_to_biset(bitmask):
    return {bitmask & (1 << i) for i in range(bitmask.bit_length()) if bitmask & (1 << i)}

def  make_candidates(l_k_with_sup,k):
    possible_next_candi = {a | b for a,b in combinations(l_k_with_sup,2)}
    next_candi =[x for x in possible_next_candi if bin(x).count('1') == (k+1)]
    return [x for x in next_candi if (all(x^(1 << i) in l_k_with_sup for i in range(x.bit_length()) if x & (1 << i)))]

# C_k -> L_K 함수 구현 [pruning]
def pruning(c_k):
    c_k_sup = [sum(1 for trans in database if (trans & candi) == candi) for candi in c_k]
    return {candi : sup for candi, sup in zip(c_k, c_k_sup) if sup >= sup_min_freq}


def all_association_rules(l_k_with_sup):
    asso_rule_k = []
    for fp,fp_sup in l_k_with_sup.items():
        bin_values = bi_to_biset(fp)
        combo_half = [[sum(bin_value) for bin_value in combinations(bin_values,i)] for i in range(1,(len(bin_values)-1)//2+1)]
        if not k%2 :
            middle = [sum(bin_value) for bin_value in combinations(bin_values, k//2)]
            combo_half.append(middle[:len(middle)//2])
        combo_rest = [[itemset ^ fp for itemset in combo] for combo in combo_half]

        asso_rule_k.append([[[bilist_to_set([itemset, asso_itemset]), fp_sup / db_size * 100, conf(itemset,asso_itemset)],
                             [bilist_to_set([asso_itemset, itemset]), fp_sup / db_size * 100, conf(asso_itemset,itemset)]
                             ]
            for combos_len_t,combos_len_k_t in zip(combo_half,combo_rest)
            for itemset, asso_itemset in zip(combos_len_t,combos_len_k_t)
            ])
    return asso_rule_k

def conf(itemset, asso_itemset):
    def sub_db(db, itemset):

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

c_1 = [1 << item for item in all_items]
database = db_to_bin(database)
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
lines = []
for k_group in output:       
    for rule_group in k_group:     
        for rule_pair in rule_group:
            for rule in rule_pair:    
                (item_set, associative_item_set), support, confidence = rule
                line = "{}\t{}\t{:.2f}\t{:.2f}".format(item_set, associative_item_set, support, confidence)
                lines.append(line)
with open(output_txt, "w", encoding="utf-8") as f:
    f.write('\n'.join(lines))

