import sys

train_txt = sys.argv[1]
test_txt = sys.argv[2]
# result_txt = sys.argv[3]
features = []
train_db = []
test_db = []
label = []

class Decision_Tree:
    def __init__(self,feature, db):
        self.root = self.Node(feature,db)

    def get_root(self):
        return self.root
    class Node:
        def __init__(self, attribute, data):
            # string 
            self.attribute = attribute
            self.data = data
            self.child = None

def open_file(txt,first_line,others):
    try: 
        with open(txt, 'r') as f:
            first_line.append([x for x in (f.readline().strip().split())])
            for line in f : others.append([x for x in line.strip().split()])
    except FileNotFoundError: sys.exit()

open_file(train_txt,features,train_db)
open_file(test_txt,[],test_db)

#print(Decision_Tree(feature = features, db = train_db).get_root().data)