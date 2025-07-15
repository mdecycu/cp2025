import random
import time

MAXPOP = 5000
MAXDIM = 35
MAXIMAPROBLEM = 1
PENALITY = -1000 if MAXIMAPROBLEM else 1000

c = [[0.0] * MAXDIM for _ in range(MAXPOP)]
d = [[0.0] * MAXDIM for _ in range(MAXPOP)]
best = [0.0] * MAXDIM
bestit = [0.0] * MAXDIM
tmp = [0.0] * MAXDIM
cost = [0.0] * MAXPOP
inibound_h = 50.0
inibound_l = 0.0

def assignd(D, a, b):
    for j in range(D):
        a[j] = b[j]

def evaluate(D, tmp):
    surface = 80.0
    z = (surface - tmp[0] * tmp[1]) / (2.0 * (tmp[0] + tmp[1]))
    volume = tmp[0] * tmp[1] * z
    if volume <= 0 or tmp[0] <= inibound_l or tmp[1] <= inibound_l:
        return PENALITY
    return volume

def main():
    D = 2
    NP = 200
    genmax = 100
    refresh = 50
    strategy = 3
    F = 1.2
    CR = 0.9

    for i in range(NP):
        for j in range(D):
            c[i][j] = inibound_l + random.random() * (inibound_h - inibound_l)
        cost[i] = evaluate(D, c[i])

    cmin, imin = cost[0], 0
    for i in range(1, NP):
        if (MAXIMAPROBLEM and cost[i] > cmin) or (not MAXIMAPROBLEM and cost[i] < cmin):
            cmin, imin = cost[i], i

    assignd(D, best, c[imin])
    assignd(D, bestit, c[imin])
    pold, pnew = c, d
    start = time.time()

    for generation in range(1, genmax + 1):
        for i in range(NP):
            idxs = [x for x in range(NP) if x != i]
            r1, r2, r3, r4, r5 = random.sample(idxs, 5)
            assignd(D, tmp, pold[i])
            n = int(random.random() * D)

            for L in range(D):
                if random.random() < CR or L == D - 1:
                    if strategy == 3:
                        tmp[n] = tmp[n] + F * (bestit[n] - tmp[n]) + F * (pold[r1][n] - pold[r2][n])
                    else:
                        tmp[n] = tmp[n]  # 其他策略可補充
                n = (n + 1) % D

            trial_cost = evaluate(D, tmp)
            improved = (trial_cost >= cost[i]) if MAXIMAPROBLEM else (trial_cost <= cost[i])

            if improved:
                cost[i] = trial_cost
                assignd(D, pnew[i], tmp)
                if (MAXIMAPROBLEM and trial_cost > cmin) or (not MAXIMAPROBLEM and trial_cost < cmin):
                    cmin = trial_cost
                    imin = i
                    assignd(D, best, tmp)
            else:
                assignd(D, pnew[i], pold[i])

        assignd(D, bestit, best)
        pold, pnew = pnew, pold

        if generation % refresh == 1:
            print(f"Generation {generation} | Best = {cmin:.8f}")

    print("\nFinal Result:")
    print(f"Best-so-far obj. funct. value = {cmin:.10g}")
    for j in range(D):
        print(f"best[{j}] = {best[j]:.10g}")
    print(f"\nDone! Time elapsed: {time.time() - start:.4f} seconds")

main()
