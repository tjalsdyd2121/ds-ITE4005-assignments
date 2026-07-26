import sys
import math
import os
from collections import deque

# undefined -> -1
# noise -> -2 

eps_sq = 0


def range_query(points, idx):
    # idx 에 해당되는 data point의 neighbor들 return.
    x, y = points[idx][1], points[idx][2]
    neighbors = []
    for i in range(len(points)) :
        px = points[i][1]
        py = points[i][2]
        if ((x - px) ** 2 + (y - py) ** 2) <= eps_sq : neighbors.append(i)
    return neighbors

def dbscan(points, eps, min_pts):
    n = len(points)
    # 일단 undefined...
    label = [-1] * n 
    # c setting
    current_cluster = 0 

    for p in range(n):
        if label[p] != -1 : continue
        N = range_query(points, p)

        if len(N) < min_pts :
            label[p] = -2
            # label(p) <- Noise
            continue

        c = current_cluster
        current_cluster += 1
        # c <- next cluster label

        label[p] = c
        S = deque(q for q in N if q != p)
        # S <- N \ {p}
        # 굳이굳이 set을 쓸필요는 없겠다

        while S:
            q = S.popleft()
            # noise면 lable(q) <- c
            if label[q] == -2 : label[q] = c
            if label[q] != -1 : continue

            N_q = range_query(points, q)
            label[q] = c 

            if len(N_q) < min_pts : continue
            S.extend(N_q)

    clusters = {}
    for i in range(len(points)):
        c = label[i]
        if c < 0 : continue # noise들
        if c not in clusters : clusters[c] = []
        clusters[c].append(points[i][0])

    return list(clusters.values())

def main():
    global eps_sq
    input_file = sys.argv[1]
    n = int(sys.argv[2])
    eps = float(sys.argv[3])
    min_pts = int(sys.argv[4])

    eps_sq = eps * eps
    points = []
    # input.txt 받아오기
    with open(input_file, 'r') as f:
        for line in f :
            line = line.strip()
            if not line : continue
            parts = line.split('\t')
            points.append((int(parts[0]), float(parts[1]), float(parts[2])))

    clusters = dbscan(points, eps, min_pts)

    # m > n이면...
    clusters.sort(key=lambda c: len(c), reverse=True)
    clusters = clusters[:n]

    base = os.path.splitext(os.path.basename(input_file))[0]
    out_dir = os.path.dirname(input_file) or '.'

    for i in range(len(clusters)):
        with open(os.path.join(out_dir, f"{base}_cluster_{i}.txt"), 'w') as f:
            for obj_id in clusters[i]:
                f.write(f"{obj_id}\n")


if __name__ == '__main__':
    main()
