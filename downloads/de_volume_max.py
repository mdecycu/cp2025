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
# 第一段: 模組引入與常數設定
# ============================================================================

import math       # 提供數學函數，如 sqrt、log、exp 等
import random     # 用於亂數抽樣，例如選擇不同個體索引
import time       # 用於記錄與顯示執行時間
import sys        # 提供 exit() 等系統功能

# === 常數與全域參數設定 ===
MAXPOP = 5000               # 差分演化法的最大族群數
MAXDIM = 35                 # 參數向量最大維度（例如最多 35 個變數）
MAXIMAPROBLEM = 1           # 問題設定：1 表示最大化問題，0 表示最小化問題

# 適應值懲罰值：最大化問題時為負值，最小化問題為正值
PENALITY = -1000 if MAXIMAPROBLEM else 1000

# === 以下為亂數產生器相關常數（模仿 C 語言中 random 的作法） ===
IM1, IM2 = 2147483563, 2147483399
AM = 1.0 / IM1                  # 規一化乘數，將整數轉換為 [0,1)
IMM1 = IM1 - 1
IA1, IA2 = 40014, 40692         # 亂數乘數
IQ1, IQ2 = 53668, 52774         # 商數
IR1, IR2 = 12211, 3791          # 餘數
NTAB = 32                       # 表的大小
NDIV = 1 + IMM1 // NTAB         # 除數常數，用於表索引計算
EPS = 1.2e-7                    # 微小正值，用於控制上限誤差
RNMX = 1.0 - EPS                # 亂數最大值，避免產生剛好為 1 的值

# 第二段: === 全域資料結構初始化 ===
# ============================================================================

c = [[0.0] * MAXDIM for _ in range(MAXPOP)]     # 原始族群個體矩陣：c[i][j] 表示第 i 個體的第 j 維參數
d = [[0.0] * MAXDIM for _ in range(MAXPOP)]     # 新族群個體矩陣：與 c 大小相同，用於儲存新一代
best = [0.0] * MAXDIM                           # 記錄整體執行過程中最好的解（歷來最佳）
bestit = [0.0] * MAXDIM                         # 記錄目前這一世代最好的解（本代最佳）
tmp = [0.0] * MAXDIM                            # 暫存變異後的試探個體向量
cost = [0.0] * MAXPOP                           # 儲存每一個個體的適應函數值（即其成本或目標值）

# 設定參數上下限：適用於所有維度的簡化版本（全域範圍）
inibound_h = 50.0                               # 參數初始上限
inibound_l = 0.0                                # 參數初始下限

# === 隨機數狀態儲存區（模擬 C++ 中 static 變數）===
# 用於多次呼叫 rnd_uni() 時記住隨機狀態（為了產生穩定而可再現的序列）
rnd_state = {
    "idum2": 123456789,                         # 第二個隨機種子，用於雙重生成法
    "iy": 0,                                    # 儲存中間運算結果的臨時變數
    "iv": [0] * NTAB                            # NTAB 長度的表，用於 shuffle
}

# === 向量複製函數：將向量 b 複製到向量 a 中（元素總數為 D）===
def assignd(D, a, b):
    for j in range(D):
        a[j] = b[j]

# 第三段:  自製亂數產生器 rnd_uni()
# ============================================================================

def rnd_uni(seed_wrapper):
    idum = seed_wrapper[0]    # 使用列表包裝，以便模擬 by-reference 效果（原地更新種子）
    s = rnd_state             # 簡化變數名稱（指向儲存狀態的字典）

    # 初次呼叫或種子為負值時進行初始化（重設序列）
    if idum <= 0:
        idum = max(1, -idum)      # 種子最小必須是 1
        s["idum2"] = idum         # 第二個種子同步初始化

        # 初始化隨機表 iv[]
        for j in range(NTAB + 7, -1, -1):
            k = idum // IQ1
            idum = IA1 * (idum - k * IQ1) - k * IR1
            if idum < 0:
                idum += IM1
            if j < NTAB:
                s["iv"][j] = idum  # 填入前 NTAB 個表值
        s["iy"] = s["iv"][0]       # iy 初始化完成

    # 主亂數生成步驟（雙重混合法）
    k = idum // IQ1
    idum = IA1 * (idum - k * IQ1) - k * IR1
    if idum < 0:
        idum += IM1

    k = s["idum2"] // IQ2
    s["idum2"] = IA2 * (s["idum2"] - k * IQ2) - k * IR2
    if s["idum2"] < 0:
        s["idum2"] += IM2

    j = s["iy"] // NDIV             # 用 iy 決定表中哪個索引
    s["iy"] = s["iv"][j] - s["idum2"]
    s["iv"][j] = idum               # 更新表 iv[j] 為新 idum
    if s["iy"] < 1:
        s["iy"] += IMM1             # 確保非負值

    temp = AM * s["iy"]             # 將 iy 轉換為 [0,1) 區間小數

    seed_wrapper[0] = idum          # 更新原始呼叫者提供的種子值
    return RNMX if temp > RNMX else temp  # 保證不會回傳 1.0（以防極端情況）

# 第四段: evaluate 函式 — 計算體積與懲罰邏
# ============================================================================

def evaluate(D, tmp, nfeval_wrapper):
    surface = 80.0                     # 固定的總表面積值，用來限制幾何設計
    nfeval_wrapper[0] += 1             # 評估次數 +1，用列表包裝才能共享狀態

    # 計算 z 值（高度），根據給定 x 與 y（tmp[0] 與 tmp[1]）
    z = (surface - tmp[0] * tmp[1]) / (2.0 * (tmp[0] + tmp[1]))

    # 計算體積 = x * y * z
    volume = tmp[0] * tmp[1] * z

    # 若體積為負或變數不合法（太小），回傳懲罰值
    if volume <= 0 or tmp[0] <= inibound_l or tmp[1] <= inibound_l:
        return PENALITY

    return volume  # 若條件合理，回傳計算得到的體積

# 第五段: 主程式 main() — 初始設定與合法性檢
# ============================================================================

def main():
    strat = [  # 策略清單，用於印出目前所選策略的名稱
        "", "DE/best/1/exp", "DE/rand/1/exp", "DE/rand-to-best/1/exp",
        "DE/best/2/exp", "DE/rand/2/exp", "DE/best/1/bin", "DE/rand/1/bin",
        "DE/rand-to-best/1/bin", "DE/best/2/bin", "DE/rand/2/bin"
    ]

    # ===== 核心參數設定 =====
    D = 2             # 決策變數的維度（例如：tmp[0]、tmp[1] 為設計變數）
    NP = 200          # 族群規模（population size）
    seed = 3          # 隨機種子，控制亂數產生的初始值
    genmax = 2000     # 演化的最大世代數
    refresh = 100     # 每隔多少世代輸出一次狀態
    # 以下測試採用不同策略、權重以及交叉率進行比較
    #strategy = 3      # 選用的演化策略編號（這裡使用 DE/rand-to-best/1/exp）
    #F = 0.85          # 差分權重：控制變異的程度（通常介於 0.5 ~ 1.0）
    #CR = 1.0          # 交叉率（crossover rate）：基因交換的機率（0 ~ 1）
    strategy = 3      # 選用的演化策略編號（這裡使用 DE/rand-to-best/1/exp）
    F = 1.2          # 差分權重：控制變異的程度（通常介於 0.5 ~ 1.0）
    CR = 0.9        # 交叉率（crossover rate）：基因交換的機率（0 ~ 1）
    

    cmin = None                     # 儲存歷來最佳的適應值
    nfeval = [0]                    # 適應函數的呼叫次數，包裝為 list 以便在函數中更新
    seed_wrapper = [-seed]          # 包裝 seed，使 rnd_uni 可以修改它（模擬 by reference）

    # ===== 輸入參數合法性檢查 =====
    if not (0 < D <= MAXDIM and 0 < NP <= MAXPOP):
        print("維度或族群數超出範圍")
        return

    if not (0 <= CR <= 1 and seed > 0 and refresh > 0 and genmax > 0):
        print("參數設定錯誤")
        return

    if not (0 <= strategy <= 10):
        print("策略參數錯誤")
        return

    if inibound_h < inibound_l:
        print("上下限設定錯誤")
        return

    # 第六段: 產生初始族群並計算評估
    # ========================================================================

    # === 初始族群產生與適應函數評估 ===
    for i in range(NP):
        for j in range(D):
            # 每個參數在範圍內均勻亂數初始化
            c[i][j] = inibound_l + rnd_uni(seed_wrapper) * (inibound_h - inibound_l)

        # 對每一個個體呼叫目標函數進行評估
        cost[i] = evaluate(D, c[i], nfeval)

    # === 找出初始最佳個體 ===
    cmin, imin = cost[0], 0  # 假設第 0 個體為最佳
    for i in range(1, NP):
        if (MAXIMAPROBLEM and cost[i] > cmin) or (not MAXIMAPROBLEM and cost[i] < cmin):
            cmin, imin = cost[i], i  # 更新歷來最佳成本與對應索引

    # 儲存最佳成員向量
    assignd(D, best, c[imin])      # 儲存為歷來最佳
    assignd(D, bestit, c[imin])    # 儲存為本世代最佳

    pold, pnew = c, d              # 指定目前族群與新族群的指標
    start = time.time()            # 記錄演算法開始的時間（用於計算總時長）
    
    #第七段:  主演化迴圈 (包括策略交叉與選擇)
    # ========================================================================

    with open("out.dat", "w") as f:            # 將結果寫入輸出檔
        for gen in range(1, genmax + 1):       # 主演化世代迴圈
            for i in range(NP):                # 對每個個體做變異與交叉
                idxs = [x for x in range(NP) if x != i]       # 選出除 i 之外的其他個體索引
                r1, r2, r3, r4, r5 = random.sample(idxs, 5)   # 隨機選取 5 個不同索引

                assignd(D, tmp, pold[i])                    # 將個體 i 的值複製到 tmp 中
                n = int(rnd_uni(seed_wrapper) * D)          # 隨機決定變異起始索引 n

                for L in range(D):  # binomial crossover 試驗，最多 D 維度
                    if rnd_uni(seed_wrapper) < CR or L == D - 1:  # 至少確保一個參數被交叉
                        if strategy == 1:  # DE/best/1/exp
                            tmp[n] = bestit[n] + F * (pold[r2][n] - pold[r3][n])
                        elif strategy == 2:  # DE/rand/1/exp
                            tmp[n] = pold[r1][n] + F * (pold[r2][n] - pold[r3][n])
                        elif strategy == 3:  # DE/rand-to-best/1/exp
                            tmp[n] = tmp[n] + F * (bestit[n] - tmp[n]) + F * (pold[r1][n] - pold[r2][n])
                        elif strategy == 4:  # DE/best/2/exp
                            tmp[n] = bestit[n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                        elif strategy == 5:  # DE/rand/2/exp
                            tmp[n] = pold[r5][n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                        elif strategy == 6:  # DE/best/1/bin
                            tmp[n] = bestit[n] + F * (pold[r2][n] - pold[r3][n])
                        elif strategy == 7:  # DE/rand/1/bin
                            tmp[n] = pold[r1][n] + F * (pold[r2][n] - pold[r3][n])
                        elif strategy == 8:  # DE/rand-to-best/1/bin
                            tmp[n] = tmp[n] + F * (bestit[n] - tmp[n]) + F * (pold[r1][n] - pold[r2][n])
                        elif strategy == 9:  # DE/best/2/bin
                            tmp[n] = bestit[n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                        elif strategy == 10 or strategy == 0:  # DE/rand/2/bin（或預設）
                            tmp[n] = pold[r5][n] + F * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n])
                    n = (n + 1) % D  # 循環處理下一維度

                # === 評估試探解 ===
                trial_cost = evaluate(D, tmp, nfeval)       # 計算試探向量的適應值
                improved = (trial_cost >= cost[i]) if MAXIMAPROBLEM else (trial_cost <= cost[i])

                if improved:
                    cost[i] = trial_cost                    # 更新適應值
                    assignd(D, pnew[i], tmp)                # 試探向量替換舊值
                    # 檢查是否創造出歷來最佳解
                    if (MAXIMAPROBLEM and trial_cost > cmin) or (not MAXIMAPROBLEM and trial_cost < cmin):
                        cmin = trial_cost
                        imin = i
                        assignd(D, best, tmp)
                else:
                    assignd(D, pnew[i], pold[i])            # 試探失敗，保留原個體

            # === 世代結束：更新當代最佳解並切換族群 ===
            assignd(D, bestit, best)
            pold, pnew = pnew, pold                         # 交換族群角色（老變新）

            # === 統計分析：平均成本與變異數 ===
            cmean = sum(cost) / NP
            cvar = sum((ci - cmean)**2 for ci in cost) / (NP - 1)

            # === 記錄與顯示狀態 ===
            if gen % refresh == 1:                          # 控制輸出頻率
                print(f"\nGeneration {gen} | Best = {cmin:.8f} | Variance = {cvar:.6f}")
                for j in range(D):
                    print(f"  best[{j}] = {best[j]:.6f}")
                f.write(f"{nfeval[0]}   {cmin:.10g}\n")
    
        # 第八段: 最終輸出與結束統計
        # ========================================================================
        # === 所有世代結束後的最終輸出 ===
        f.write(f"\n\nBest-so-far obj. funct. value = {cmin:.10g}\n")  # 輸出最終最佳成本值

        for j in range(D):
            f.write(f"\nbest[{j}] = {best[j]:.10g}")                  # 輸出最佳向量中每一個參數值

        # 輸出演化設定與統計資料
        f.write(f"\n\nGeneration={gen}  NFEs={nfeval[0]}   Strategy: {strat[strategy]}")
        f.write(f"\nNP={NP}    F={F:.2f}    CR={CR:.2f}   cost-variance={cvar:.5g}\n")

    # 顯示總執行時間（以秒為單位）
    print(f"\nDone! Time elapsed: {time.time() - start:.4f} seconds")

# 最後一段: 啟動主程式
# ============================================================================

# === Python 標準主程式進入點（避免被其他模組誤執行）===
if __name__ == "__main__":
    main()