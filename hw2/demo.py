import sys
import numpy as np

train_txt = sys.argv[1]
test_txt = sys.argv[2]
# result_txt = sys.argv[3]
features = []
# features[-1] is set for class label.
possible_values = []
# possible_values[0] is set for possible values of features[0]
label = []
# label is set for possible values of class label.
train_db = []
test_db = []

class Decision_Tree:
    def __init__(self,feature, db):
        self.root = self.Node(feature,db)

    def get_root(self):
        return self.root
    class Node:
        def __init__(self, attributes, pos_val, data):
            self.attributes = attributes
            # e.g. ['age', 'income', 'student', 'credit_rating']
            self.pos_val = pos_val
            # e.g. {'31...40', '>40', '<=30'}, {'high', 'low', 'medium'}, {'yes', 'no'}, {'excellent', 'fair'}
            chosen_idx, stop = self.branching() 
            self.a = attributes[chosen_idx]
            # selected attribute : a

            self.branch = None
            # dict 형태로 저장. e.g. {'high' : chlid1, 'low' : child2, 'medium' : child3 }

            self.data = data
            # data in this node.
            # e.g. ['>40', 'medium', 'no', 'fair', 'yes']

        def branching(self):
            gains = {i: self.gainRatio(i) for i in range(len(self.attributes))}
            return (max(gains, key=gains.get))
        def info_after(self, idx):
            # idx is index w.r.t attributes list, as candidate for selected attribute.
            tmp = []
            for target in self.pos_val[idx]:
                d_j = [x for x in self.data if x[idx] == target]
                tmp.append(len(d_j) * self.info_before(d_j))
            return sum(tmp) / len(self.data)
        def info_before(self, data):
            tmp = []
            for i in range(len(label)):
                tmp.append(len([x for x in data if (x[-1] == label[i])]) / len(label))
            return - (sum( p * np.log2(p) for p in tmp))
        def splitInfo(self, idx):
            tmp = []
            for target in self.pos_val[idx]:
                d_j = [x for x in self.data if x[idx] == target]
                if len(d_j) > 0:
                    tmp.append(len(d_j) * np.log2(len(d_j)/len(self.data)))
            return -sum(tmp)/len(self.data)
        def gainRatio(self,idx):
            # return gainRation with features[idx]
            gain = self.info_before(self.data) - self.info_after(idx)
            return (gain / self.splitInfo(idx))

    def build(self):
        pass

def open_file(txt,first_line,others):#
    try: 
        with open(txt, 'r') as f:
            first_line.extend([x for x in (f.readline().strip().split())])
            for line in f : others.append([x for x in line.strip().split()])
    except FileNotFoundError: sys.exit()

def construct_db(train_db, features, possible_values, label):
    for i in range(len(features)-1):
        possible_values.append({row[i] for row in train_db})
    label.extend({row[-1] for row in train_db})

open_file(train_txt,features,train_db)
open_file(test_txt,[],test_db)
construct_db(train_db, features, possible_values, label)

print(train_db)
print(features)
print(possible_values)
print(label)