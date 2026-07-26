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
            first_line.extend([x for x in (f.readline().strip().split())])
            for line in f : others.append([x for x in line.strip().split()])
    except FileNotFoundError: sys.exit()

def construct_db(train_db, features, possible_values, label):
    for i in range(len(features)-1):
        possible_values.append({row[i] for row in train_db})
    label.extend(sorted(list({row[-1] for row in train_db})))

open_file(train_txt, features, train_db)
open_file(test_txt, [], test_db)
construct_db(train_db, features, possible_values, label)

train_labels = [row[-1] for row in train_db]
global_majority = max(sorted(list(set(train_labels))), key=train_labels.count)

class Decision_Tree:
    def __init__(self, data):
        available_attrs = list(range(len(features) - 1))
        self.root = self.Node(available_attrs, data, global_majority)
        self.root.build() 
    def get_root(self):
        return self.root        

    class Node:
        def __init__(self, available_attrs, data, parent_majority):
            self.available_attrs = available_attrs
            self.data = data
            self.parent_majority = parent_majority
            self.branch = {}
            self.split_attr = None 
            self.leaf_label = None
            
            if not data:
                self.majority = parent_majority
            else:
                labels = [x[-1] for x in data]
                unique_l = sorted(list(set(labels)))
                counts = [labels.count(l) for l in unique_l]
                max_c = max(counts)
                winners = [unique_l[i] for i, v in enumerate(counts) if v == max_c]
                
                if len(winners) > 1 and parent_majority in winners:
                    self.majority = parent_majority
                else:
                    self.majority = winners[0]

        def predict(self, query):
            if self.leaf_label is not None:
                return self.leaf_label
            if query[self.split_attr] in self.branch:
                return (self.branch[query[self.split_attr]]).predict(query)
            else : 
                return self.majority

        def build(self):
            labels_in_data = [x[-1] for x in self.data]
            if len(set(labels_in_data)) == 1:
                self.leaf_label = labels_in_data[0]
                return
            if not self.available_attrs:
                self.leaf_label = self.majority
                return

            best_idx = self.branching()
            if self.gainRatio(best_idx) <= 0:
                self.leaf_label = self.majority
                return

            self.split_attr = best_idx
            child_attrs = [attr for attr in self.available_attrs if attr != best_idx]

            for val in possible_values[best_idx]:
                sub_data = [x for x in self.data if x[best_idx] == val]
                child_node = Decision_Tree.Node(child_attrs, sub_data, self.majority)
                self.branch[val] = child_node
                if not sub_data: 
                    child_node.leaf_label = self.majority
                else: 
                    child_node.build()

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
        f.write('\t'.join(query) + '\t' + predicted_label + '\n')