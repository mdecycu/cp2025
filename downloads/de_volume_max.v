import math
import rand
import time
import os

const maxpop = 5000
const maxdim = 35
const maximaproblem = 1
const penalize = if maximaproblem == 1 { -1000.0 } else { 1000.0 }

const im1 = 2147483563
const im2 = 2147483399
const am = 1.0 / im1
const imm1 = im1 - 1
const ia1 = 40014
const ia2 = 40692
const iq1 = 53668
const iq2 = 52774
const ir1 = 12211
const ir2 = 3791
const ntab = 32
const ndiv = 1 + imm1 / ntab
const eps = 1.2e-7
const rnmx = 1.0 - eps

const inibound_h = 50.0
const inibound_l = 0.0

struct RndState {
mut:
	idum2 int
	iy    int
	iv    []int
}

fn new_rnd_state() RndState {
	return RndState{
		idum2: 123456789
		iy: 0
		iv: []int{len: ntab, init: 0}
	}
}

fn assignd(d int, mut a []f64, b []f64) {
	for j in 0 .. d {
		a[j] = b[j]
	}
}

fn rnd_uni(mut seed []int, mut s RndState) f64 {
	mut idum := seed[0]
	if idum <= 0 {
		idum = if -idum < 1 { 1 } else { -idum }
		s.idum2 = idum
		for j := ntab + 7; j >= 0; j-- {
			k := idum / iq1
			idum = ia1 * (idum - k * iq1) - k * ir1
			if idum < 0 { idum += im1 }
			if j < ntab { s.iv[j] = idum }
		}
		s.iy = s.iv[0]
	}
	k := idum / iq1
	idum = ia1 * (idum - k * iq1) - k * ir1
	if idum < 0 { idum += im1 }

	k2 := s.idum2 / iq2
	s.idum2 = ia2 * (s.idum2 - k2 * iq2) - k2 * ir2
	if s.idum2 < 0 { s.idum2 += im2 }

	j := s.iy / ndiv
	s.iy = s.iv[j] - s.idum2
	s.iv[j] = idum
	if s.iy < 1 { s.iy += imm1 }

	seed[0] = idum
	temp := am * f64(s.iy)
	return if temp > rnmx { rnmx } else { temp }
}

fn evaluate(d int, x []f64, mut nfeval []int) f64 {
	surface := 80.0
	nfeval[0]++
	z := (surface - x[0] * x[1]) / (2.0 * (x[0] + x[1]))
	volume := x[0] * x[1] * z
	if volume <= 0 || x[0] <= inibound_l || x[1] <= inibound_l {
		return penalize
	}
	return volume
}

fn run_de() {
	d := 2
	np := 200
	genmax := 2000
	refresh := 100
	strategy := 3
	f := 1.2
	cr := 0.9
	mut seed := [-3]
	mut state := new_rnd_state()
	mut nfeval := [0]

	mut c := [][]f64{len: np, init: []f64{len: d, init: 0.0}}
	mut dpop := [][]f64{len: np, init: []f64{len: d, init: 0.0}}
	mut tmp := []f64{len: d, init: 0.0}
	mut best := []f64{len: d, init: 0.0}
	mut bestit := []f64{len: d, init: 0.0}
	mut cost := []f64{len: np, init: 0.0}
	mut pold := c.clone()
	mut pnew := dpop.clone()

	strat := ["", "DE/best/1/exp", "DE/rand/1/exp", "DE/rand-to-best/1/exp",
		      "DE/best/2/exp", "DE/rand/2/exp", "DE/best/1/bin", "DE/rand/1/bin",
		      "DE/rand-to-best/1/bin", "DE/best/2/bin", "DE/rand/2/bin"]

	for i in 0 .. np {
		for j in 0 .. d {
			c[i][j] = inibound_l + rnd_uni(mut seed, mut state) * (inibound_h - inibound_l)
		}
		cost[i] = evaluate(d, c[i], mut nfeval)
	}

	mut cmin := cost[0]
	mut imin := 0
	for i in 1 .. np {
		if (maximaproblem == 1 && cost[i] > cmin) || (maximaproblem == 0 && cost[i] < cmin) {
			cmin = cost[i]
			imin = i
		}
	}
	assignd(d, mut best, c[imin])
	assignd(d, mut bestit, c[imin])

	start := time.now()
	mut fout := os.create("out.dat") or {
		println("❌ 無法寫入 out.dat")
		return
	}

	for gen in 1 .. genmax + 1 {
		for i in 0 .. np {
			mut idxs := []int{}
			for k in 0 .. np {
				if k != i { idxs << k }
			}
			rand.shuffle(mut idxs) or {}
			r1, r2, r3, r4, r5 := idxs[0], idxs[1], idxs[2], idxs[3], idxs[4]

			assignd(d, mut tmp, pold[i])
			mut n := int(rnd_uni(mut seed, mut state) * f64(d))

			for j in 0 .. d {
				if rnd_uni(mut seed, mut state) < cr || j == d - 1 {
					tmp[n] = match strategy {
						1 { bestit[n] + f * (pold[r2][n] - pold[r3][n]) }
						2 { pold[r1][n] + f * (pold[r2][n] - pold[r3][n]) }
						3 { tmp[n] + f * (bestit[n] - tmp[n]) + f * (pold[r1][n] - pold[r2][n]) }
						4 { bestit[n] + f * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n]) }
						5 { pold[r5][n] + f * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n]) }
						6 { bestit[n] + f * (pold[r2][n] - pold[r3][n]) }
						7 { pold[r1][n] + f * (pold[r2][n] - pold[r3][n]) }
						8 { tmp[n] + f * (bestit[n] - tmp[n]) + f * (pold[r1][n] - pold[r2][n]) }
						9 { bestit[n] + f * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n]) }
						else { pold[r5][n] + f * (pold[r1][n] + pold[r2][n] - pold[r3][n] - pold[r4][n]) }
					}
				}
				n = (n + 1) % d
			}

			trial := evaluate(d, tmp, mut nfeval)
			improved := if maximaproblem == 1 { trial >= cost[i] } else { trial <= cost[i] }
			if improved {
				cost[i] = trial
				assignd(d, mut pnew[i], tmp)
				if (maximaproblem == 1 && trial > cmin) || (maximaproblem == 0 && trial < cmin) {
					cmin = trial
					imin = i
					assignd(d, mut best, tmp)
				}
			} else {
				assignd(d, mut pnew[i], pold[i])
			}
		}

		assignd(d, mut bestit, best)
		pold = pnew.clone()
		pnew = c.clone()

		// 統計與輸出
		mut sum := 0.0
		for val in cost { sum += val }
		mean := sum / f64(np)

		mut var := 0.0
		for val in cost { var += math.pow(val - mean, 2) }
		var /= f64(np - 1)

		if gen % refresh == 1 {
			println("\nGeneration $gen | Best = ${cmin:.8f} | Variance = ${var:.6f}")
			for j in 0 .. d {
				println("  best[$j] = ${best[j]:.6f}")
			}
			fout.writeln("${nfeval[0]}   ${cmin:.10g}") or {}
		}
	}

	// 輸出最終最佳值與設定
	fout.writeln("\n\nBest-so-far obj. funct. value = ${cmin:.10g}") or {}
	for j in 0 .. d {
		fout.writeln("best[${j}] = ${best[j]:.10g}") or {}
	}
	fout.writeln("\n\nGeneration=$genmax  NFEs=${nfeval[0]}   Strategy: ${strat[strategy]}") or {}
	fout.writeln("NP=$np    F=${f:.2f}    CR=${cr:.2f}") or {}
	fout.close()

	elapsed := time.now().unix() - start.unix()
	println("\n✅ Done! Time elapsed: ${elapsed} seconds")
}

fn main() {
	println("🚀 啟動差分演化器 DE/Volume/Maximizer")
	run_de()
}