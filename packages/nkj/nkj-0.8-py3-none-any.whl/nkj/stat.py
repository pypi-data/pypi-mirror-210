#
# [name] nkj.stat.py
# [reference] https://qiita.com/suaaa7/items/745ac1ca0a8d6753cf60
#
# Written by Yoshikazu NAKAJIMA (Wed Apr 14 18:59:31 JST 2021)
#
_LIB_DEBUGLEVEL = 1

import numpy as np
from scipy import stats

import os
import sys
sys.path.append(os.path.abspath(".."))
from nkj.str import *

def ftest(A, B):
	A_var = np.var(A, ddof=1) # A の不偏分散
	B_var = np.var(B, ddof=1) # B の不偏分散
	A_df = len(A) - 1 # A の自由度
	B_df = len(B) - 1 # A の自由度
	f = A_var / B_var # F 比の値
	onesided_pval1 = stats.f.cdf(f, A_df, B_df) # 片側検定の p 値 1
	onesided_pval2 = stats.f.sf(f, A_df, B_df)  # 片側検定の p 値 2
	twosided_pval = min(onesided_pval1, onesided_pval2) * 2 # 両側検定の p 値
	ldprint3(["F:       {0}".format(round(f, 3))])
	ldprint3(["p-value: {0}".format(round(twosided_pval, 4))])
	return f, twosided_pval

def ftest_msg(A, B):
	f, pval = ftest(A, B)
	ldprint(["F:       {0}".format(round(f, 3))])
	ldprint(["p-value: {0}".format(round(pval, 4))])
	print("F 検定帰無仮説：「2 群は等分散である．」")
	if (pval > _PVAL):
		print("p > {0} より、帰無仮説は棄却されませんでした．2 群間は少なくとも不等分散でないと言って良い(= 等分散と言える可能せが残る)．".format(_PVAL))
		print("T-test で検定してください．")
	else:
		print("p <= {0} より、帰無仮説は棄却されました．2 群間は不等分散と言って良い．".format(_PVAL))
		print("Welch t-test で検定してください．")

def ttest(A, B, rel=False):
	if (rel):
		return stats.ttest_rel(A, B) # 対応あり t-test
	else:
		return stats.ttest_ind(A, B) # 対応なし t-test

def welchttest(A, B):
	return stats.ttest_ind(A, B, equal_var=False) # equal_var=False を指定する．

def wilcoxon(A, B, rel=True):
	if (rel):
		return stats.wilcoxon(A, B)     # Wilcoxon 符号付順位和検定．(対応あり)
	else:
		return stats.mannwhitneyu(A, B, alternative='two-sided') # Mann-Whitney u-test, Wilcoxon 順位和検定．(独立=対応なし)

def mannwhitneyu(A, B):
	return wilcoxon(A, B, False)

def pvalcheck(pval, flag=True):
	stars = 3
	for val in [0.001, 0.01, 0.05]:
		if (pval < val):
			if (flag):
				print("< {0}".format(val))
			break
		else:
			stars -= 1
	return stars

def starstr(pval, flag=True):
	if (flag):
		stars = pvalcheck(pval, False)
	else:
		stars = pval
	str = ''
	for i in range(stars):
		str += '*'
	return str

#-- main

_PVAL = 0.05

if __name__ == '__main__':
	lib_debuglevel(_LIB_DEBUGLEVEL)

	#
	# §．2 群間の有意差検定
	#
	# 正規分布が仮定できるとき，
	# 2 群が等分散のとき、t-test (対応あり/なし）
	# 2 群が不等分散のとき、welch t-test (対応あり/なし）
	#
	# 正規分布が仮定できないとき(=ノンパラメトリック分布のとき）、
	# 2 群間に対応ありのとき、Wilcoxon signed-rank test (符号付き順位検定)
	# 2 群間に対応なしのとき、Mann-Whitney U test (Wilcoxon rank sum test(順位和検定))
	#
	# §．3 群以上の間の有意差検定
	#
	# ANalysis Of VAriance (ANOVA)(分散分析): 全体的な平均値の相違を調べる方法で、どの群間に有意差があるかは把握できない．
	#
	print("-- t-test")
	A = np.array([6.3, 8.1, 9.4, 10.4, 8.6, 10.5, 10.2, 10.5, 10.0, 8.8])
	B = np.array([4.8, 2.1, 5.1, 2.0, 4.0, 1.0, 3.4, 2.7, 5.1, 1.4, 1.6])
	ftest_msg(A, B)
	test_result = ttest(A, B) # 対応なし t-test
	print("T-test:    {0}".format(test_result))
	print("statistic: {0}".format(test_result.statistic))
	print("p-value:   {0}".format(test_result.pvalue))
	stars = pvalcheck(test_result.pvalue)
	#print("stars:     {0}".format(stars))
	print("stars:     {0}".format(starstr(test_result.pvalue)))
	print("")

	print("-- Welch t-test")
	A = np.array([13.8, 10.2, 4.6, 10.0, 4.2, 16.1, 14.4, 4.9, 7.7, 11.4])
	B = np.array([3.3, 2.6, 4.0, 4.7, 1.9, 2.9, 4.7, 5.3, 4.3, 3.0, 2.0])
	ftest_msg(A, B)
	test_result = welchttest(A, B)
	print("T-test:    {0}".format(test_result))
	print("statistic: {0}".format(test_result.statistic))
	print("p-value:   {0}".format(test_result.pvalue))
	stars = pvalcheck(test_result.pvalue)
	#print("stars:     {0}".format(stars))
	print("stars:     {0}".format(starstr(test_result.pvalue)))
	print("")

	print("-- Wilcoxon test")
	A = np.array([1.83, 1.50, 1.62, 2.48, 1.68, 1.88, 1.55, 3.06, 1.30])
	B = np.array([0.88, 0.65, 0.60, 1.05, 1.06, 1.29, 1.06, 2.14, 1.29])
	test_result = wilcoxon(A, B)
	print("T-test:    {0}".format(test_result))
	print("statistic: {0}".format(test_result.statistic))
	print("p-value:   {0}".format(test_result.pvalue))
	stars = pvalcheck(test_result.pvalue)
	#print("stars:     {0}".format(stars))
	print("stars:     {0}".format(starstr(test_result.pvalue)))
	print("")

	print("-- Mann-Whitney U test")
	A = np.array([1.83, 1.50, 1.62, 2.48, 1.68, 1.88, 1.55, 3.06, 1.30, 2.01, 3.11])
	B = np.array([0.88, 0.65, 0.60, 1.05, 1.06, 1.29, 1.06, 2.14, 1.29])
	test_result = mannwhitneyu(A, B)
	print("T-test:    {0}".format(test_result))
	print("statistic: {0}".format(test_result.statistic))
	print("p-value:   {0}".format(test_result.pvalue))
	stars = pvalcheck(test_result.pvalue)
	#print("stars:     {0}".format(stars))
	print("stars:     {0}".format(starstr(test_result.pvalue)))
	print("")
