import sys
import numpy as np

train_txt = sys.argv[1]
test_txt = sys.argv[2]

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
    label.extend(list({row[-1] for row in train_db})) # 인덱싱을 위해 list로 감쌈

open_file(train_txt, features, train_db)
open_file(test_txt, [], test_db)
construct_db(train_db, features, possible_values, label)

class Decision_Tree:
    def __init__(self, data):
        available_attrs = list(range(len(features) - 1))
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
            self.branch = {}        # 자식 노드들을 저장할 딕셔너리
            self.split_attr = None  # 이 노드에서 분할 기준으로 선택된 속성 인덱스
            self.leaf_label = None  # 리프 노드일 경우 최종 결정된 라벨

        def build(self):
            # 현재 데이터들의 라벨(yes/no 등) 리스트
            labels_in_data = [x[-1] for x in self.data]
            
            # [Base Case 1] 노드 안의 모든 데이터가 같은 클래스일 때 -> 순수 노드(Leaf)
            if len(set(labels_in_data)) == 1:
                self.leaf_label = labels_in_data[0]
                return

            # [Base Case 2] 더 이상 분류 기준으로 쓸 속성이 없을 때 -> 다수결로 리프 노드 생성
            if not self.available_attrs:
                self.leaf_label = max(set(labels_in_data), key=labels_in_data.count)
                return

            # 최적의 분할 속성 인덱스 찾기
            best_idx = self.branching()
            self.split_attr = best_idx

            # 자식 노드들에게는 방금 사용한 속성을 제외하고 넘겨줌
            child_attrs = [attr for attr in self.available_attrs if attr != best_idx]

            # 선택된 속성의 가능한 모든 값(e.g., high, medium, low)에 대해 가지(branch) 치기
            for val in possible_values[best_idx]:
                sub_data = [x for x in self.data if x[best_idx] == val]
                
                # 자식 노드 객체 생성 후 딕셔너리에 연결
                child_node = Decision_Tree.Node(child_attrs, sub_data)
                self.branch[val] = child_node
                
                # [Base Case 3] 해당 조건에 맞는 데이터가 아예 없는 경우 -> 부모의 다수결을 따름
                if not sub_data:
                    child_node.leaf_label = max(set(labels_in_data), key=labels_in_data.count)
                else:
                    # 데이터가 있다면 자식 노드도 이어서 트리 생성 (재귀 호출)
                    child_node.build()

        def branching(self):
            # 남은 속성들에 대해서만 Gain Ratio 계산
            gains = {i: self.gainRatio(i) for i in self.available_attrs}
            # Gain 값이 가장 높은 속성의 인덱스 반환
            return max(gains, key=gains.get)

        def info_after(self, idx):
            tmp = []
            for target in possible_values[idx]:
                d_j = [x for x in self.data if x[idx] == target]
                if len(d_j) > 0:
                    # (해당 서브셋의 데이터 비율) * (서브셋의 엔트로피)
                    tmp.append((len(d_j) / len(self.data)) * self.info_before(d_j))
            return sum(tmp)

        def info_before(self, data):
            if not data: return 0
            tmp = []
            for l in label:
                # [수정됨] len(label)이 아닌 len(data)로 나누어야 확률(p)이 됨
                prob = len([x for x in data if x[-1] == l]) / len(data)
                if prob > 0: # log2(0) 방지
                    tmp.append(prob)
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
            gain = self.info_before(self.data) - self.info_after(idx)
            split_info = self.splitInfo(idx)
            # [수정됨] 분모가 0이 되는 것을 방지
            if split_info == 0:
                return 0
            return gain / split_info

# ====== [실행 및 결과 확인] ======
print("=== 트리 학습 시작 ===")
tree = Decision_Tree(train_db)
print("=== 학습 완료! 생성된 의사결정 나무 구조 ===")
tree.print_tree()