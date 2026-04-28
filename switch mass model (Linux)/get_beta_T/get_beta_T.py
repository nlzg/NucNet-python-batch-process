import numpy as np

# ===================== 配置（你只改这里！）=====================
FILE_WS4 = "new_mass_excess.txt"  # 你的质量剩余文件
FILE_BETA = "betaprimal.dat"  # 你的beta原始文件
# ==============================================================

# %% 清除变量（Python无需）clc; clear;

# ===================== 1. 读取数据 =====================
set_data = np.loadtxt(FILE_WS4)  # 质量剩余数据
beta = np.loadtxt(FILE_BETA)  # 原始beta数据
deta_n = 8.0713167

# 单位转换：keV → MeV
set_data[:, 2] /= 1000.0

# ===================== 2. 计算 Sn =====================
Z = set_data[:, 0]
N = set_data[:, 1]
m = set_data[:, 2]

Sn = []
v = 0
for i in range(1, len(set_data)):
    cond1 = set_data[i, 0] == set_data[i - 1, 0]
    cond2 = set_data[i, 1] - set_data[i - 1, 1] == 1
    cond3 = (deta_n - (set_data[i, 2] - set_data[i - 1, 2])) > 0

    if cond1 and cond2 and cond3:
        Sn.append([
            set_data[i, 0],
            set_data[i, 1],
            deta_n - (set_data[i, 2] - set_data[i - 1, 2])
        ])

Sn = np.array(Sn) if Sn else np.empty((0, 3))

# ===================== 筛选边缘核素 =====================
if len(Sn) == 0:
    SnF = np.empty((0, 3))
else:
    SnF = [Sn[0]]
    F = Sn[0, 1]
    v = 1
    for i in range(1, len(Sn)):
        cond = (F + 1 == Sn[i, 1]) or (Sn[i, 0] != Sn[i - 1, 0])
        if cond:
            SnF.append(Sn[i])
            F = Sn[i, 1]
            v += 1
    SnF = np.array(SnF)

# 找边缘 Snb
Snb = []
if len(SnF) >= 2:
    for i in range(1, len(SnF)):
        if SnF[i, 0] != SnF[i - 1, 0]:
            Snb.append(SnF[i - 1])
    Snb.append(SnF[-1])
    Snb = np.array(Snb)
else:
    Snb = SnF.copy()

# ===================== Sn 对 M 筛选 =====================
M = []
for i in range(len(set_data)):
    for j in range(len(Snb)):
        if set_data[i, 0] == Snb[j, 0] and set_data[i, 1] <= Snb[j, 1]:
            M.append(set_data[i])
M = np.array(M) if M else np.empty((0, 3))

# ===================== Q_m (β衰变能) =====================
b = SnF[:, :2].copy()
b = np.column_stack([b, np.zeros(len(b))])

for i in range(len(b)):
    for j in range(i + 1, len(set_data)):
        if b[i, 0] == set_data[j, 0] and b[i, 1] == set_data[j, 1]:
            b[i, 2] = set_data[j, 2]

Q = []
for i in range(1, len(b)):
    for j in range(i + 1, len(b)):
        cond1 = b[i, 0] + 1 == b[j, 0]
        cond2 = b[i, 1] - 1 == b[j, 1]
        cond3 = (b[i, 2] - b[j, 2]) > 0
        if cond1 and cond2 and cond3:
            Q.append([b[i, 0], b[i, 1], b[i, 2] - b[j, 2]])
Q = np.array(Q) if Q else np.empty((0, 3))

# ===================== 半衰期计算 =====================
alpha = 1 / 137
a1 = 3.016
a2 = 3.879
a3 = 1.322
a4 = 6.030
a5 = 1.669
a6 = 11.09
a7 = 1.07
a8 = -0.935
a9 = -5.398

if len(Q) == 0:
    print("无有效Q值，退出")
    exit()

Z1, N1, W1 = [], [], []
D = []
for i in range(len(Q)):
    Zi, Ni, Qi = Q[i]
    s = (-1) ** Zi + (-1) ** Ni
    if (Qi - a8 * s) > 0:
        Z1.append(Zi)
        N1.append(Ni)
        W1.append(Qi)
        D.append(s)

Z1 = np.array(Z1)
N1 = np.array(N1)
W1 = np.array(W1)
D = np.array(D)
A1 = Z1 + N1

# k
k = np.log(W1 - a8 * D)

# S(Z,N)
term1 = a1 * np.exp(-((N1 - 28) ** 2 + (Z1 - 20) ** 2) / 12)
term2 = a2 * np.exp(-((N1 - 50) ** 2 + (Z1 - 38) ** 2) / 43)
term3 = a3 * np.exp(-((N1 - 82) ** 2 + (Z1 - 58) ** 2) / 13)
term4 = a4 * np.exp(-((N1 - 82) ** 2 + (Z1 - 58) ** 2) / 24)
term5 = a5 * np.exp(-((N1 - 110) ** 2 + (Z1 - 70) ** 2) / 244)
S = term1 + term2 + term3 + term4 + term5

# T
T = a6 + (alpha ** 2 * Z1 ** 2 - 5 - a7 * (N1 - Z1) / A1) * k + a9 * alpha ** 2 * Z1 ** 2
T += (1 / 3) * alpha ** 2 * Z1 ** 2 * np.log(A1) - alpha * Z1 * np.pi + S

# T1
T1 = np.column_stack([
    Z1, N1, np.exp(T),
    np.ones(len(Z1)),
    np.zeros((len(Z1), 3))
])

# 去掉 inf
mask = np.isfinite(T1[:, 2])
T1 = T1[mask]

# ===================== beta 边缘筛选 =====================
betaa = []
if len(beta) >= 2:
    for i in range(1, len(beta)):
        if beta[i, 0] != beta[i - 1, 0]:
            betaa.append(beta[i - 1])
    betaa.append(beta[-1])
    betaa = np.array(betaa)
else:
    betaa = beta.copy()

# ===================== 匹配 beta =====================
for i in range(len(T1)):
    zt, nt = T1[i, 0], T1[i, 1]
    for j in range(len(beta)):
        zb, nb = beta[j, 0], beta[j, 1]
        if zt == zb and nt == nb:
            T1[i, 3:] = beta[j, 3:]

# ===================== 最后一次筛选 =====================
T2 = []
for i in range(len(T1)):
    zt, nt = T1[i, :2]
    for j in range(len(betaa)):
        zb, nb = betaa[j, :2]
        if zt == zb and nt < nb:
            T2.append(T1[i])
T2 = np.array(T2) if T2 else T1

# ===================== 输出文件（和 MATLAB 完全一样格式）=====================

# 1. ws4_Sn.txt
with open('new_Sn.txt', 'w') as f:
    for row in SnF:
        f.write(f"{int(row[0]):<4d} {int(row[1]):<4d} {row[2]:>20.7f}\n")

# 2. ws4_T.txt
with open('new_T.txt', 'w') as f:
    for row in T1:
        f.write(f"{int(row[0]):<4d} {int(row[1]):<4d} {row[2]:>20.7f} {row[3]:>20.7f} {row[4]:>20.7f} {row[5]:>20.7f} {row[6]:>20.7f}\n")

# 3. ws4_M.txt
with open('new_M.txt', 'w') as f:
    for row in M:
        f.write(f"{int(row[0]):<4d} {int(row[1]):<4d} {row[2]:>20.7f}\n")
