import sys
import numpy as np

train_txt = sys.argv[1]
test_txt = sys.argv[2]
result_txt = sys.argv[3]

features = []
possible_values = []
label = []
train_db = []
test_db = []

def open_file(txt, first_line, others):
    try: 
        with open(txt, 'r') as f:
            first_line.extend([x for x in (f.readline().strip().split('\t'))])
            for line in f : others.append([x for x in line.strip().split('\t')])
    except FileNotFoundError: sys.exit()

def construct_db(train_db, features, possible_values, label):
    for i in range(len(features)-1):
        possible_values.append({row[i] for row in train_db})
    label.extend(list({row[-1] for row in train_db})) # 인덱싱을 위해 list로 감쌈

open_file(train_txt, features, train_db)
open_file(test_txt, [], test_db)
construct_db(train_db, features, possible_values, label)

class Decision_Tree:
    def __init__(self, data):
        available_attrs = list(range(len(features) - 1))
        # atrrs는 index 를 원소로 가지는 list.
        self.root = self.Node(available_attrs, data)
        self.root.build() 
    def get_root(self):
        return self.root        

    def print_tree(self, node=None, indent=""):
        if node is None: node = self.root
        
        if node.leaf_label is not None:
            print(indent + "selected label :", node.leaf_label)
            return
            
        print(indent + f"[{features[node.split_attr]}] 속성에 따라 분류:")
        for val, child in node.branch.items():
            print(indent + f"   ├── {val}:")
            self.print_tree(child, indent + "   │   ")

    class Node:
        def __init__(self, available_attrs, data):
            self.available_attrs = available_attrs
            self.data = data
            # 현재 노드에서 가지고 있는 data, 선택가능한 attr.
            self.branch = {}
            # dict 로 하위 branch 설정. e,g. {'high' : chlid1, 'low' : child2, 'medium' : child3 }
            self.split_attr = None 
            self.leaf_label = None
        
        def predict(self, query):
            # here, query is like ['<=30', 'high', 'no', 'fair']
            # 종료 조건 1 : 현재 node가 leaf_node 일때.
            if self.leaf_label is not None:
                return self.leaf_label
            # 종료 조건 2 : 관측하지 못한 패턴의 query 일때.
            # e.g. training 결과 income : {'high', 'medium'} 뿐인데, 'low'를 가진 친구가 나타나면...
            # -> 현재 노드의 voting을 따른다.
            if query[self.split_attr] in self.branch:
                return (self.branch[query[self.split_attr]]).predict(query)
            else : 
                labels_in_data = [x[-1] for x in self.data]
                return max(set(labels_in_data), key=labels_in_data.count)

        def build(self):
            labels_in_data = [x[-1] for x in self.data]
            # 종료 조건 1 : 모든 data의 class label 이 동일할 때
            if len(set(labels_in_data)) == 1:
                self.leaf_label = labels_in_data[0]
                return
            # 종료 조건 2 : 더이상 branching이 불가능할 때.
            # -> leaf 노드. majority voting
            if not self.available_attrs:
                self.leaf_label = max(set(labels_in_data), key=labels_in_data.count)
                return

            best_idx = self.branching()
            self.split_attr = best_idx
            child_attrs = [attr for attr in self.available_attrs if attr != best_idx]

            for val in possible_values[best_idx]:
                sub_data = [x for x in self.data if x[best_idx] == val]
                
                child_node = Decision_Tree.Node(child_attrs, sub_data)
                self.branch[val] = child_node
                
                # 종료 조건 3 : 쪼개졌는데 이에 해당되는 data 가 없을 때
                # -> decision 은 해야하기 때문에 현재 노드의 voting을 따르기
                if not sub_data: child_node.leaf_label = max(set(labels_in_data), key=labels_in_data.count)
                else: child_node.build()

        def branching(self):
            gains = {i: self.gainRatio(i) for i in self.available_attrs}
            return max(gains, key=gains.get)

        def info_after(self, idx):
            tmp = []
            for target in possible_values[idx]:
                d_j = [x for x in self.data if x[idx] == target]
                if len(d_j) > 0: tmp.append((len(d_j) / len(self.data)) * self.info_before(d_j))
            return sum(tmp)

        def info_before(self, data):
            if not data: return 0
            tmp = []
            for l in label:
                prob = len([x for x in data if x[-1] == l]) / len(data)
                if prob > 0: tmp.append(prob)
            return -sum(p * np.log2(p) for p in tmp)

        def splitInfo(self, idx):
            tmp = []
            for target in possible_values[idx]:
                d_j = [x for x in self.data if x[idx] == target]
                if len(d_j) > 0:
                    prob = len(d_j) / len(self.data)
                    tmp.append(prob * np.log2(prob))
            return -sum(tmp)

        def gainRatio(self, idx):
            split_info = self.splitInfo(idx)
            if split_info == 0: return 0
            return (self.info_before(self.data) - self.info_after(idx)) / split_info


dt = Decision_Tree(train_db)
with open(result_txt, 'w') as f:
    f.write('\t'.join(features) + '\n')
    for query in test_db:
        predicted_label = dt.get_root().predict(query)
        result_line = '\t'.join(query) + '\t' + predicted_label
        f.write(result_line + '\n')