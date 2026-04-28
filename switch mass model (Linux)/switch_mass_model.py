import math
import os
import shutil
import subprocess
import threading

from tqdm import tqdm


#质量模型的名字
model = 'AME+WS4'
# 最大并发数
MAX_THREADS = 50

# 元素符号列表：索引=原子序数-1
element = [
    # 1-10
    "h", "he", "li", "be", "b", "c", "n", "o", "f", "ne",
    # 11-20
    "na", "mg", "al", "si", "p", "s", "cl", "ar", "k", "ca",
    # 21-30（fe26、cu29）
    "sc", "ti", "v", "cr", "mn", "fe", "co", "ni", "cu", "zn",
    # 31-40
    "ga", "ge", "as", "se", "br", "kr", "rb", "sr", "y", "zr",
    # 41-50（pd46）
    "nb", "mo", "tc", "ru", "rh", "pd", "ag", "cd", "in", "sn",
    # 51-60
    "sb", "te", "i", "xe", "cs", "ba", "la", "ce", "pr", "nd",
    # 61-70
    "pm", "sm", "eu", "gd", "tb", "dy", "ho", "er", "tm", "yb",
    # 71-80
    "lu", "hf", "ta", "w", "re", "os", "ir", "pt", "au", "hg",
    # 81-90
    "tl", "pb", "bi", "po", "at", "rn", "fr", "ra", "ac", "th",
    # 91-100
    "pa", "u", "np", "pu", "am", "cm", "bk", "cf", "es", "fm",
    # 101-110（lr103、rf104）
    "md", "no", "lr", "rf", "db", "sg", "bh", "hs", "mt", "ds",
    # 111-118（目前元素上限）
    "rg", "cn", "nh", "fl", "mc", "lv", "ts", "og"
]
# 新的质量模型：
path_new_mass_excess = os.path.join('.', f'{model}', f'mass_excess_{model}.txt')
try:
    with open(path_new_mass_excess,'r') as f:
        pass
    print('已找到新的质量剩余文件，请检查数据结构为【Z, N, MASS_EXCESS(KeV)】')
except:
    print('未找到新的质量剩余文件')
# 临时数据：
dir_temporary_data = os.path.join('.', f'{model}', 'temporary_data')
os.makedirs(dir_temporary_data, exist_ok=True)

# %% 第一部分: 生成质量剩余修改文件
print('开始计算质量剩余')
## 获取 NucNet 中的质量模型
path_old_mass_excess = os.path.join(dir_temporary_data, 'old_mass_excess.txt')
dir_libnucnet = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'libnucnet')
path_old_net = os.path.join('.', 'old', 'net_old.xml')
abs_path_old_net = os.path.abspath(path_old_net)
abs_path_old_mass_excess = os.path.abspath(path_old_mass_excess)
cmd = (f'cd {dir_libnucnet} && '
       f'./print_nuclides {abs_path_old_net} > {abs_path_old_mass_excess}')
subprocess.run(cmd, shell=True)
## 查找相同核素,生成用于修改质量剩余的文件
path_switch_mass_excess = os.path.join('.', f'{model}','switch_mass_excess.txt')
with open(path_new_mass_excess,'r') as f:
    lines = f.readlines()
    list_all = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        list_all.append([int(parts[0]), int(parts[0])+int(parts[1]), (parts[2])])
with open(path_old_mass_excess,'r') as f:
    lines = f.readlines()
    list_jina = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if line[0].isdigit() == False:
            continue
        parts = line.split()
        list_jina.append([int(parts[1]), int(parts[2])])
list_update = []
count = 0
for nuc_jina in list_jina:
    tag = 0
    for nuc_all in list_all:
        if nuc_all[0] == nuc_jina[0] and nuc_all[1] == nuc_jina[1]:
            count += 1
            tag = 1
            z = nuc_jina[0]
            a = nuc_jina[1]
            mass_excess = float(nuc_all[2])/1000
    if tag == 0 :
        continue
    list_update.append(f'{z}  {a}  {mass_excess}\n')
with open(path_switch_mass_excess,'w') as f:
    f.writelines(list_update)
print(f'已生成用于修改质量剩余的文件，匹配了 {count} 个核素')

# %% 第二部分: 生成用于修改 β 反应率的文件
## 计算半衰期
print('开始计算 β 半衰期')
shutil.copy(path_new_mass_excess, os.path.join('.', 'get_beta_T', 'new_mass_excess.txt'))
cmd = (f"cd {os.path.join('.', 'get_beta_T')} && "
       f'python3 get_beta_T.py')
subprocess.run(cmd, shell=True)
## 获取 NucNet 中的 β 反应
print('开始获取 NucNet 中的 β 反应')
path_old_beta_react = os.path.join(dir_temporary_data, 'old_beta_react.txt')
abs_path_old_beta_react = os.path.abspath(path_old_beta_react)
cmd = (f'cd {dir_libnucnet} && '
       f'./print_reactions {abs_path_old_net} '
       f'"[count(reactant) = 1 and product = \'electron\' and product = \'anti-neutrino_e\' and count(product) = 3]" '
       f'> {abs_path_old_beta_react}')
subprocess.run(cmd, shell=True)
## 定义了一个函数：通过一个核素，输出 Z A β衰变后产生的核素，如 o19 -> f19
def next_element(the_element:str):
    name = ''
    a = ''
    for item in the_element:
        if item.isdigit():
            a += item
        else:
            name += item
    next_index = element.index(name) + 1
    if next_index >= len(element):
        return [0, 0, 0]
    else:
        next_name = element[next_index]
        next_ele = next_name + a
        return [element.index(name) + 1, a, next_ele]
## 计算 β 反应率
print('开始计算 β 反应率')
path_new_beta_T = os.path.join('.', 'get_beta_T', 'new_T.txt')
path_new_beta_rate = os.path.join(dir_temporary_data, 'new_beta_rate.txt')
with open(path_new_beta_T, 'r') as f:
    lines = f.readlines()
    list1 = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        rate = math.log(2) / float(parts[2])
        rates = f'{parts[0]}\t{parts[1]}\t{rate}\n'
        list1.append(rates)
with open(path_new_beta_rate, 'w') as f:
    f.writelines(list1)
## 筛选新旧模型共有的 β 反应
path_same_beta_react = os.path.join(dir_temporary_data,'same_deta_react.txt')
list1 = []
with open(path_new_mass_excess,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        if int(parts[0]) > 118:
            continue
        a = int(parts[0]) + int(parts[1])
        list1.append(element[int(parts[0]) - 1] + str(a))
list2 = []
for item in list1:
    with open(path_old_beta_react,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            if parts[0] == 'Number':
                continue
            if parts[0] == item:
                list2.append(line + '\n')
with open(path_same_beta_react,'w') as f:
    f.writelines(list2)
## 生成用于修改 β 反应率的文件
path_dir = os.getcwd()
path_rate = os.path.join(path_dir,'ws4_beta_rate.txt')
path_new_beta = os.path.join(path_dir,'beta_reaction_jina_choice.txt')
path_switch_beta_rate = os.path.join('.', f'{model}','switch_beta_reta.txt')
with open(path_new_beta_rate,'r') as f:
    lines = f.readlines()
    rates = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        rates.append(line)
with open(path_same_beta_react,'r') as f:
    lines = f.readlines()
    reactions = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        reactions.append(parts[0])
update_txt = []
count = 0
for reaction in reactions:
    for rate in rates:
        parts = rate.split()
        tag = 0
        z1 = int(next_element(reaction)[0])
        z2 = int(parts[0])
        a1 = int(next_element(reaction)[1])
        a2 = int(parts[1]) + int(parts[0])
        if z2 > z1:
            break
        elif z1 > z2:
            continue
        elif a1 == a2:
            tag = 1
            count += 1
            the_rate = parts[2]
            break
    if tag == 0 :
        continue
    the_txt = (f'single_rate\n'
                f'my_ws4\n'
                f'1\n'
                f'{reaction}\n'
                f'3\n'
                f'{next_element(reaction)[2]}\n'
                f'electron\n'
                f'anti-neutrino_e\n'
                f'{the_rate}\n\n')
    update_txt.append(the_txt)
with open(path_switch_beta_rate,'w') as f:
    f.writelines(update_txt)
print(f'已生成用于修改 β 反应率的文件，匹配了 {count} 个 β 衰变反应')

# %% 第三部分: 生成用于修改 (n,γ) 反应率的文件
## 获取 NucNet 中的 (n,γ) 反应
print('开始获取 NucNet 中的 (n,γ) 反应')
path_old_gamma_react = os.path.join(dir_temporary_data, 'old_gamma_react.txt')
abs_path_old_gamma_react = os.path.abspath(path_old_gamma_react)
cmd = (f'cd {dir_libnucnet} && '
       f'./print_reactions {abs_path_old_net} '
       f'"[count(reactant) = 2 and product = \'gamma\' and reactant = \'n\' and count(product) = 2]"'
       f'> {abs_path_old_gamma_react}')
subprocess.run(cmd, shell=True)
## 定义了一个函数：通过一个核素，输出 Z A (n,γ)反应后产生的核素，如 o19 -> o20
def after_element(the_element:str):
    name = ''
    a = ''
    for item in the_element:
        if item.isdigit():
            a += item
        else:
            name += item
    after_ele = name + str( int(a) + 1 )
    return [element.index(name) + 1, int(a), after_ele]
## 筛选新旧模型共有的 (n,γ) 反应
path_same_gamma_react = os.path.join(dir_temporary_data,'same_gamma_react.txt')
list_all = []
with open(path_new_mass_excess,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        list_all.append([int(parts[0]), int(parts[0])+int(parts[1])])
list_gamma = []
with open(path_old_gamma_react,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        if parts[0] == 'Number':
            continue
        list_gamma.append(line)
reactions = []
for nuc_all in list_all:
    for reaction in list_gamma:
        reaction = reaction.strip()
        parts = reaction.split()
        nuc_gamma_1 = after_element(parts[2])
        nuc_gamma_2 = after_element(parts[4])
        if nuc_all[0] == nuc_gamma_1[0] and nuc_all[1] == nuc_gamma_1[1] and nuc_all[1]+1 == nuc_gamma_2[1]:
            reactions.append(reaction + '\n')
with open(path_same_gamma_react,'w') as f:
    f.writelines(reactions)
print(f'匹配了 {len(reactions)} 个 （n，γ）反应')

# %% 第四部分：批量计算 (n,γ) 反应率，并生成用于修改 (n,γ) 反应率的文件
print('开始批量计算 (n,γ) 反应率')
semaphore = threading.Semaphore(MAX_THREADS)
path_switch_gamma_rate = os.path.join('.', f'{model}', 'switch_gamma_rate.txt')
file_lock = threading.Lock()
## 定义一个单次计算函数
def run(cp:int,max_threads:int,model:str):
    semaphore.acquire()
    ### 创建运行目录
    dir_run = os.path.join('/', 'home', 'xsli', 'projects', 'talys', f'{model}', f'run_{cp}')
    os.makedirs(dir_run, exist_ok=True)
    ### 读取反应
    react = ''
    with open(path_same_gamma_react, 'r') as f:
        lines_in = f.readlines()
        count_in = 0
        for line_in in lines_in:
            line_in = line_in.strip()
            if line_in == '':
                continue
            count_in += 1
            if count_in == cp:
                react = line_in
                break
    ### 生成输入文本
    react = react.strip()
    parts_in = react.split()
    nuc_1 = after_element(parts_in[2])
    nuc_2 = after_element(parts_in[4])
    nuc_1_name = parts_in[2]
    nuc_2_name = parts_in[4]
    with open(path_new_mass_excess, 'r') as f:
        lines_in = f.readlines()
        for line_in in lines_in:
            line_in = line_in.strip()
            if line_in == '':
                continue
            parts_in = line_in.split()
            nuc_all = [int(parts_in[0]), int(parts_in[0]) + int(parts_in[1]), parts_in[2]]
            if nuc_all[0] > nuc_1[0]:
                break
            elif nuc_all[0] == nuc_1[0]:
                if nuc_all[1] == nuc_1[1]:
                    excess_1 = float(nuc_all[2]) / 1000
                elif nuc_all[1] == nuc_2[1]:
                    excess_2 = float(nuc_all[2]) / 1000
    comment = (f'projectile n\n'
               f'element {element[nuc_1[0] - 1]}\n'
               f'mass {nuc_1[1]}\n'
               f'energy 1.\n'
               f'astro y\n'
               f'massexcess {nuc_1[0]} {nuc_1[1]} {excess_1}\n'
               f'massexcess {nuc_2[0]} {nuc_2[1]} {excess_2}\n'
               f'ldmodel 1')
    path_inp = os.path.join(dir_run, 'talys.inp')
    with open(path_inp, 'w') as f:
        f.writelines(comment)
    ### 开始计算
    cmd = f'cd {dir_run} && talys < talys.inp > talys.out'
    subprocess.run(cmd, shell=True)
    ### 将结果写入生成修改 β 反应率修改文件
    comment_1 = (f'rate_table\n'
               f'my_ws4\n'
               f'2\n'
               f'n\n'
               f'{nuc_1_name}\n'
               f'2\n'
               f'{nuc_2_name}\n'
               f'gamma\n')
    comment_2 = ''
    path_out = os.path.join(dir_run, 'astrorate.g')
    with open(path_out,'r') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            count += 1
            parts = line.split()
            comment_2 += f'{parts[0]}   {parts[1]}  1.00\n'
    comment_update = comment_1 + f'{count}\n' + comment_2 + '\n'
    with file_lock:
        with open(path_switch_gamma_rate, 'a') as f:
            f.write(comment_update)
    shutil.rmtree(dir_run, ignore_errors=True)
    semaphore.release()
## 启动多线程
total = len(reactions)
threads = []
for i in range(total):
    t = threading.Thread(target=run, args=(i + 1, total, model))
    t.start()
    threads.append(t)
for t in tqdm(threads, desc="计算进度:"):
    t.join()
print('已生成用于修改 (n,γ) 反应率的文件')

# %% 第五部分：生成新的网络文件
dir_misc = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'examples', 'misc')
path_old_nuc = os.path.join('.', 'old', 'nuc_old.xml')
path_new_nuc = os.path.join('.', f'{model}', f'nuc_{model}.xml')
abs_path_old_nuc = os.path.abspath(path_old_nuc)
abs_path_switch_mass_excess = os.path.abspath(path_switch_mass_excess)
abs_path_new_nuc = os.path.abspath(path_new_nuc)
cmd = (f'cd {dir_misc} && '
       f'./update_mass_excesses_from_text {abs_path_old_nuc} nuc {abs_path_switch_mass_excess} {model} {abs_path_new_nuc}')
subprocess.run(cmd, shell=True, check=True)
path_new_beta_xml = os.path.join(dir_temporary_data,'new_beta.xml')
path_new_gamma_xml = os.path.join(dir_temporary_data,'new_gamma.xml')
abs_path_switch_beta_rate = os.path.abspath(path_switch_beta_rate)
abs_path_new_beta_xml = os.path.abspath(path_new_beta_xml)
abs_path_switch_gamma_rate = os.path.abspath(path_switch_gamma_rate)
abs_path_new_gamma_xml = os.path.abspath(path_new_gamma_xml)
cmd = (f'python3 create_reaction_xml.py {abs_path_switch_beta_rate} {abs_path_new_beta_xml} && '
       f'python3 create_reaction_xml.py {abs_path_switch_gamma_rate} {abs_path_new_gamma_xml}')
subprocess.run(cmd, shell=True, check=True)
path_old_react = os.path.join('.', 'old','react_old.xml')
path_new_react = os.path.join('.', f'{model}', f'react_{model}.xml')
path_new_net = os.path.join('.', f'{model}', f'net_{model}.xml')
abs_path_old_react = os.path.abspath(path_old_react)
abs_path_new_react = os.path.abspath(path_new_react)
abs_path_new_net = os.path.abspath(path_new_net)
cmd = (f'cd {dir_libnucnet} && '
       f'./update_reac_data_to_xml {abs_path_old_react} {abs_path_new_beta_xml} {abs_path_new_react} && '
       f'./update_reac_data_to_xml {abs_path_new_react} {abs_path_new_gamma_xml} {abs_path_new_react} && '
       f'./merge_net {abs_path_new_nuc} {abs_path_new_react} {abs_path_new_net}')
subprocess.run(cmd, shell=True, check=True)
print('已生成新的网络文件')