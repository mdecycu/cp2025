'''
題目:
一位製造商想設計一個開口式的盒子，其底部為長方形，寬為 x、長為 y，且總表面積為 80 平方公分。 請問要使盒子的體積達到最大，應該使用哪些尺寸？

A manufacturer wants to design an open-top box with a rectangular base, where the width is x and the length is y. The total surface area of the box is 80 square centimeters. What dimensions will produce a box with the maximum volume?

差分演化（Differential Evolution, DE）是一種以族群為基礎的隨機搜尋演算法，用來解決連續空間的最佳化問題。它屬於進化計算（Evolutionary Computation）範疇，概念上與基因演算法（Genetic Algorithm, GA）類似，但操作方式更直接且參數更少。

核心流程包含以下步驟：

1. 族群初始化（Initialization）
隨機產生一組解向量（population），每個向量代表一個潛在解。

2. 變異（Mutation）
對每個個體 x_i，選擇其他幾個個體來產生一個差分向量。
例如：
v_i = x_{r1} + F \cdot (x_{r2} - x_{r3})
其中 F \in [0, 2] 是變異係數，用於放大差分。

3. 交叉（Crossover）
將原始個體與變異向量混合，以產生試驗向量 u_i。 
使用交叉率 CR \in [0,1] 控制每個維度是否從變異向量中取得。

4. 選擇（Selection）
若試驗向量的適應值優於原始個體，則保留試驗向量作為新一代；否則保留原始個體。

5. 重複步驟 2~4，直到滿足終止條件，例如達到最大世代數或收斂標準。

差分演化的策略總覽（strategy 1～10）

每種策略名稱的格式一般為：  
`DE/x/y/z`，其中：
- `x` 是基向量來源，例如 `best` 或 `rand`
- `y` 是差分向量的個數（1 或 2）
- `z` 是交叉類型：`exp`（指數型）、`bin`（二項式）

strategy 1: DE/best/1/exp

變異公式：  
  v = best + F × (x_r2 - x_r3)

特色：  
- 基於目前最佳個體進行擴張探索  
- 收斂速度快，但易陷入區域最優

strategy 2: DE/rand/1/exp

變異公式：  
  v = x_r1 + F × (x_r2 - x_r3)

特色：  
- 更具探索性（隨機選擇基向量）  
- 適用於多峰與複雜問題，但收斂較慢

strategy 3: DE/rand-to-best/1/exp

變異公式：  
  v = x_i + F × (best - x_i) + F × (x_r1 - x_r2)

特色：  
- 同時利用自己、最佳個體與差分向量  
- 平衡探索與利用，適合大多數問題  
- 本程式預設就是使用此策略

strategy 4: DE/best/2/exp

變異公式：  
  v = best + F × (x_r1 + x_r2 - x_r3 - x_r4)

特色：  
- 雙重差分向量，變異幅度大  
- 加強全域搜索能力

strategy 5: DE/rand/2/exp

變異公式：  
  v = x_r5 + F × (x_r1 + x_r2 - x_r3 - x_r4)

特色：  
- 完全隨機基準與兩組差分  
- 極具探索力，但結果不穩定

strategy 6: DE/best/1/bin

變異公式：  
  v = best + F × (x_r2 - x_r3)

交叉：  
- 二項式交叉（binomial crossover）：每一維有機率採用變異值

特色：  
- 版本與 strategy 1 類似，但採用 bin 模式  
- 通常收斂快，但侷限較大

strategy 7: DE/rand/1/bin

變異公式：  
  v = x_r1 + F × (x_r2 - x_r3)

特色：  
- 與 strategy 2 相同變異公式，但交叉為 bin  
- 較穩健、效果不錯

strategy 8: DE/rand-to-best/1/bin

變異公式：  
  v = x_i + F × (best - x_i) + F × (x_r1 - x_r2)

特色：  
- 同 strategy 3，但交叉為 bin  
- 本程式支援此策略，你有看到

strategy 9: DE/best/2/bin

變異公式：  
  v = best + F × (x_r1 + x_r2 - x_r3 - x_r4)

特色：  
- 雙差分 + binomial crossover  
- 能兼顧搜索與收斂性

strategy 10: DE/rand/2/bin

變異公式：  
  v = x_r5 + F × (x_r1 + x_r2 - x_r3 - x_r4)

特色：  
- 隨機性極強，變化多端  
- 冒險型策略，適合初期探索
'''
import random

MAXPOP = 5000
MAXDIM = 35
MAXIMAPROBLEM = 1
PENALITY = -1000
inibound_h = 50.0
inibound_l = 0.0

IM1, IM2 = 2147483563, 2147483399
AM = 1.0 / IM1
IMM1 = IM1 - 1
IA1, IA2 = 40014, 40692
IQ1, IQ2 = 53668, 52774
IR1, IR2 = 12211, 3791
NTAB = 32
NDIV = 1 + IMM1 // NTAB
EPS = 1.2e-7
RNMX = 1.0 - EPS

rnd_state = {
    "idum2": 123456789,
    "iy": 0,
    "iv": [0] * NTAB
}
def rnd_uni(seed_wrapper):
    idum = seed_wrapper[0]
    s = rnd_state
    if idum <= 0:
        idum = max(1, -idum)
        s["idum2"] = idum
        for j in range(NTAB + 7, -1, -1):
            k = idum // IQ1
            idum = IA1 * (idum - k * IQ1) - k * IR1
            if idum < 0: idum += IM1
            if j < NTAB: s["iv"][j] = idum
        s["iy"] = s["iv"][0]
    k = idum // IQ1
    idum = IA1 * (idum - k * IQ1) - k * IR1
    if idum < 0: idum += IM1
    k = s["idum2"] // IQ2
    s["idum2"] = IA2 * (s["idum2"] - k * IQ2) - k * IR2
    if s["idum2"] < 0: s["idum2"] += IM2
    j = s["iy"] // NDIV
    s["iy"] = s["iv"][j] - s["idum2"]
    s["iv"][j] = idum
    if s["iy"] < 1: s["iy"] += IMM1
    temp = AM * s["iy"]
    seed_wrapper[0] = idum
    return RNMX if temp > RNMX else temp

def assignd(D, a, b):
    for j in range(D):
        a[j] = b[j]

def evaluate(D, tmp, nfeval):
    surface = 80.0
    nfeval[0] += 1
    x, y = tmp[0], tmp[1]
    z = (surface - x * y) / (2.0 * (x + y))
    vol = x * y * z
    if vol <= 0 or x <= inibound_l or y <= inibound_l:
        return PENALITY
    return vol
def run_de(params):
    D = params.get("D", 2)
    NP = params.get("NP", 200)
    F = params.get("F", 0.85)
    CR = params.get("CR", 0.9)
    strategy = params.get("strategy", 3)
    genmax = params.get("genmax", 1000)
    seed = params.get("seed", 42)

    seed_wrapper = [-seed]
    nfeval = [0]

    c = [[0.0] * D for _ in range(NP)]
    d = [[0.0] * D for _ in range(NP)]
    best = [0.0] * D
    bestit = [0.0] * D
    tmp = [0.0] * D
    cost = [0.0] * NP
    best_history = []

    for i in range(NP):
        for j in range(D):
            c[i][j] = inibound_l + rnd_uni(seed_wrapper) * (inibound_h - inibound_l)
        cost[i] = evaluate(D, c[i], nfeval)

    cmin, imin = cost[0], 0
    for i in range(1, NP):
        if MAXIMAPROBLEM and cost[i] > cmin or (not MAXIMAPROBLEM and cost[i] < cmin):
            cmin, imin = cost[i], i

    assignd(D, best, c[imin])
    assignd(D, bestit, c[imin])
    pold, pnew = c, d

    for gen in range(1, genmax + 1):
        for i in range(NP):
            idxs = [x for x in range(NP) if x != i]
            r1, r2, r3, r4, r5 = random.sample(idxs, 5)
            assignd(D, tmp, pold[i])
            n = int(rnd_uni(seed_wrapper) * D)

            for L in range(D):
                if rnd_uni(seed_wrapper) < CR or L == D - 1:
                    if strategy == 1:
                        tmp[n] = bestit[n] + F * (pold[r2][n] - pold[r3][n])
                    elif strategy == 2:
                        tmp[n] = pold[r1][n] + F * (pold[r2][n] - pold[r3][n])
                    elif strategy == 3:
                        tmp[n] += F * (bestit[n] - tmp[n]) + F * (pold[r1][n] - pold[r2][n])
                    elif strategy == 4:
                        tmp[n] = bestit[n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                    elif strategy == 5:
                        tmp[n] = pold[r5][n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                    elif strategy == 6:
                        tmp[n] = bestit[n] + F * (pold[r2][n] - pold[r3][n])
                    elif strategy == 7:
                        tmp[n] = pold[r1][n] + F * (pold[r2][n] - pold[r3][n])
                    elif strategy == 8:
                        tmp[n] += F * (bestit[n] - tmp[n]) + F * (pold[r1][n] - pold[r2][n])
                    elif strategy == 9:
                        tmp[n] = bestit[n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                    elif strategy == 10 or strategy == 0:
                        tmp[n] = pold[r5][n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                n = (n + 1) % D

            trial_cost = evaluate(D, tmp, nfeval)
            improved = trial_cost >= cost[i] if MAXIMAPROBLEM else trial_cost <= cost[i]

            if improved:
                cost[i] = trial_cost
                assignd(D, pnew[i], tmp)
                if trial_cost > cmin:
                    cmin = trial_cost
                    assignd(D, best, tmp)
            else:
                assignd(D, pnew[i], pold[i])

        assignd(D, bestit, best)
        pold, pnew = pnew, pold
        best_history.append((gen, cmin))
            
    return {
        "best_cost": cmin,
        "best_vector": best,
        "history": best_history,
        "evaluations": nfeval[0]
    }