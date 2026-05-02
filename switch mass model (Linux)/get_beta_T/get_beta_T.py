# ====================== 配置区域 ======================
# 这里只需要修改文件名，其他代码都不用动
# 输入：质量剩余数据文件
FILE_WS4 = "new_mass_excess.txt"
# 输入：beta衰变原始数据文件
FILE_BETA = "betaprimal.dat"
# 输出：最终半衰期结果（只生成这一个文件）
OUTFILE = "new_T_2.txt"
# ======================================================

# 导入Python自带的数学库（用来计算 log、指数、圆周率等）
import math

# ---------------------- 读取质量文件 new_mass_excess.txt ----------------------
# 创建空列表，用来存放所有核素的 Z, N, 质量剩余
set_data = []

# 打开质量文件，逐行读取
with open(FILE_WS4, 'r', encoding='utf-8') as f:
    # 循环处理文件里的每一行
    for line in f:
        # 去掉每行前后的空格、换行符
        line = line.strip()
        # 如果这一行是空行，直接跳过
        if not line:
            continue
        # 如果这一行以 # 开头，是注释行，直接跳过
        if line.startswith('#'):
            continue

        # 把一行内容按空格切开，分成几列
        parts = line.split()
        # 第 0 列：质子数 Z，转成整数
        z = int(parts[0])
        # 第 1 列：中子数 N，转成整数
        n = int(parts[1])
        # 第 2、3 列：质量剩余，转成小数，并且从 keV 转成 MeV（除以1000）
        if len(parts) == 3:
            mass_1 = float(parts[2]) / 1000.0
            set_data.append((z, n, mass_1))
        else:
            mass_1 = float(parts[2]) / 1000.0
            mass_2 = float(parts[3]) / 1000.0
            set_data.append((z, n, mass_1, mass_2))

# ---------------------- 读取 beta 原始数据文件 betaprimal.dat ----------------------
# 创建空列表，存放 beta 数据
beta_data = []

# 打开 beta 文件
with open(FILE_BETA, 'r', encoding='utf-8') as f:
    # 逐行读取
    for line in f:
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        # 跳过 # 开头的注释行
        if line.startswith('#'):
            continue

        # 按空格分割成列
        parts = line.split()
        # 第 0 列：质子数 Z
        z = int(parts[0])
        # 第 1 列：中子数 N
        n = int(parts[1])
        # 第2列及以后：其他参数，转成小数
        rest = [float(p) for p in parts[2:]]

        # 存入列表
        beta_data.append((z, n, rest))

# ---------------------- 物理公式固定常数 ----------------------
# 中子质量剩余常数
deta_n = 8.0713167
# 精细结构常数
alpha = 1 / 137
# 下面这些 a1~a9 都是半衰期计算公式里的固定参数
a1 = 3.016
a2 = 3.879
a3 = 1.322
a4 = 6.030
a5 = 1.669
a6 = 11.09
a7 = 1.07
a8 = -0.935
a9 = -5.398

# ---------------------- 计算中子分离能 Sn ----------------------
# Sn：中子分离能，判断原子核能不能稳定存在
Sn = []

# 从第2行开始遍历（因为要和前一行对比）
for i in range(len(set_data) - 1):
    # 当前行的 Z, N, 质量
    z_curr = set_data[i][0]
    n_curr = set_data[i][1]
    # 前一行的 Z, N, 质量
    z_prev = set_data[i + 1][0]
    n_prev = set_data[i + 1][1]
    if len(set_data[i]) == len(set_data[i + 1]):
        m_curr = set_data[i][-1]
        m_prev = set_data[i + 1][-1]
    else:
        m_curr = set_data[i][2]
        m_prev = set_data[i + 1][2]

    # 条件1：质子数必须相同（同一个元素）
    if z_curr != z_prev:
        continue
    # 条件2：中子数必须刚好比前一行多 1
    if n_prev - n_curr != 1:
        continue

    # 计算中子分离能
    sn_val = deta_n - (m_prev - m_curr)
    # 条件3：分离能必须大于 0（物理上有效）
    if sn_val > 0:
        Sn.append((z_prev, n_prev, sn_val))

# ---------------------- 筛选边缘核素（中子滴线核）SnF ----------------------
# 只保留每一条元素链最外围、最不稳定的核
SnF = []

# 如果有有效 Sn 数据才执行
if Sn:
    # 先把第一个核加进去
    SnF.append(Sn[0])
    # 记录上一个边缘核的中子数
    last_n = Sn[0][1]

    # 从第二个核开始遍历
    for i in range(1, len(Sn)):
        z, n, val = Sn[i]
        # 前一个核的质子数
        prev_z = Sn[i-1][0]

        # 满足：中子数连续 或 换了新元素 → 判定为边缘核
        if n == last_n + 1 or z != prev_z:
            SnF.append((z, n, val))
            # 更新最后一个边缘核的中子数
            last_n = n

# ---------------------- 给边缘核素匹配对应的质量剩余 ----------------------
b_list = []

# 遍历每一个边缘核
for z, n, _ in SnF:
    # 在全部质量数据里找 Z、N 完全一样的核
    for i in range(len(set_data)):
        dz = set_data[i][0]
        dn = set_data[i][1]
        if dz == z and dn == n:
            # 找到就把 Z、N、质量存起来
            b_list.append(set_data[i])
            # 找到就跳出，不再继续找
            break

# ---------------------- 计算 β 衰变能 Q ----------------------
# Q 是衰变能，Q>0 才能发生衰变
Q = []

# 遍历所有边缘核（作为母核）
for i in range(len(b_list)):
    z1 = b_list[i][0]
    n1 = b_list[i][1]
    # 再遍历所有边缘核（作为子核）
    for j in range(len(b_list)):
        z2 = b_list[j][0]
        n2 = b_list[j][1]
        if len(b_list[j]) == len(b_list[i]):
            m1 = b_list[i][-1]
            m2 = b_list[j][-1]
        else:
            m1 = b_list[i][2]
            m2 = b_list[j][2]

        # β-衰变规则：
        # 子核质子数 = 母核 + 1
        # 子核中子数 = 母核 - 1
        if z2 == z1 + 1 and n2 == n1 - 1:
            # 计算衰变能
            qval = m1 - m2
            # 衰变能 > 0 才有效
            if qval > 0:
                Q.append((z1, n1, qval))

# ---------------------- 核心：用公式计算 β 半衰期 ----------------------
result = []

# 遍历每一个有有效衰变能 Q 的核
for z, n, q in Q:
    # 原子核奇偶效应修正
    s = (-1)**z + (-1)**n
    # 修正后的有效衰变能
    w = q - a8 * s
    # 有效能量 <=0 不能衰变，跳过
    if w <= 0:
        continue

    # 质量数 A = 质子数 + 中子数
    a = z + n

    # 公式中间变量：对数能量
    k = math.log(w)

    # 5个壳效应修正项（原子核结构修正）
    term1 = a1 * math.exp(-((n-28)**2 + (z-20)**2)/12)
    term2 = a2 * math.exp(-((n-50)**2 + (z-38)**2)/43)
    term3 = a3 * math.exp(-((n-82)**2 + (z-58)**2)/13)
    term4 = a4 * math.exp(-((n-82)**2 + (z-58)**2)/24)
    term5 = a5 * math.exp(-((n-110)**2 + (z-70)**2)/244)
    # 总壳修正
    S = term1 + term2 + term3 + term4 + term5

    # ---------- 半衰期计算公式 ----------
    T = a6
    T += (alpha**2 * z**2 - 5 - a7*(n-z)/a) * k
    T += a9 * alpha**2 * z**2
    T += (1/3)*alpha**2 * z**2 * math.log(a)
    T -= alpha * z * math.pi
    T += S

    # 计算最终半衰期（取指数）
    half_life = math.exp(T)

    # 匹配原始 beta 文件里的参数（后面4列）
    cols = [1.0, 0.0, 0.0, 0.0]
    for bz, bn, rest in beta_data:
        # 找到 Z、N 相同的核
        if bz == z and bn == n:
            # 把原始数据后面4列拿过来
            cols = rest[:4]
            break

    # 把结果存入列表：Z, N, 半衰期, 其他4列参数
    result.append((z, n, half_life, *cols))

# ---------------------- 输出最终结果到 new_T_2.txt ----------------------
with open(OUTFILE, 'w') as f:
    # 把每一条结果写入文件
    for item in result:
        # 按固定格式输出：Z N 半衰期 后面4列参数
        f.write(f"{item[0]:<4d}{item[1]:<4d}{item[2]:>20.7f}{item[3]:>20.7f}{item[4]:>20.7f}{item[5]:>20.7f}{item[6]:>20.7f}\n")

# 控制台提示完成
print("完成！生成：new_T_2.txt")