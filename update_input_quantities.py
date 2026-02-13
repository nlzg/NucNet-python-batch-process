import math
import os
import subprocess

# 小写化学元素符号列表：索引=原子序数-1，1-118号完整（核反应/编程适配）
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


#########################################################################################
# 第一部分 修改 β 反应率
#########################################################################################


'''
001
选取需要修改反应率的 β 衰变方程
'''
def choose_beta_reaction(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_all = os.path.join(path_dir,'mass_excess_all')
    path_beta = os.path.join(path_dir,'beta_reaction_jina.txt')
    path_new_beta = os.path.join(path_dir,'beta_reaction_jina_choice.txt')
    list1 = []
    with open(path_all,'r') as f:
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
        with open(path_beta,'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == '':
                    continue
                parts = line.split()
                if parts[0] == item:
                    list2.append(line + '\n')

    with open(path_new_beta,'w') as f:
        f.writelines(list2)

'''
002
通过一个核素，输出 Z A 衰变后产生的核素
如 o19 -> f19
'''
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

'''
003
通过 ws4_T 生成 β 反应率文件（ws4_beta_rate.txt）
'''
def get_beta_rate(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_t = os.path.join(path_dir,'ws4_T.txt')
    path_rate = os.path.join(path_dir,'ws4_beta_rate.txt')
    with open(path_t,'r') as f:
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
    with open(path_rate,'w') as f:
        f.writelines(list1)

'''
004
结合 ws4_beta 和 new_beta 生成修改反应率的文本（update_beta_by_python.txt）
'''
def update_beta_reaction_by_txt(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_rate = os.path.join(path_dir,'ws4_beta_rate.txt')
    path_new_beta = os.path.join(path_dir,'beta_reaction_jina_choice.txt')
    path_update_beta = os.path.join(path_dir,'update_beta_by_python.txt')
    with open(path_rate,'r') as f:
        lines = f.readlines()
        rates = []
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            rates.append(line)
    with open(path_new_beta,'r') as f:
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
    with open(path_update_beta,'w') as f:
        f.writelines(update_txt)
    print(f'找到了 {count} 个 β 衰变反应')

'''
005
筛选某个元素的 β 衰变反应
'''
def search_reaction(quality_model:str,element_index:int):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_beta = os.path.join(path_dir,'beta_reaction_jina.txt')
    with open(path_beta,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            if int(next_element(parts[0])[0]) == element_index:
                print(f'{line}')

'''
006
修改 β 反应率的函数汇总
需要的文件：mass_excess_all   beta_reaction_jina.txt  ws4_T.txt
输出的文件：update_beta_by_python.txt
'''
def updata_beta(quality_model:str):
    choose_beta_reaction(quality_model)
    get_beta_rate(quality_model)
    update_beta_reaction_by_txt(quality_model)


#######################################################################################
# 第二部分 修改质量剩余
#######################################################################################

'''
007
生成修改质量剩余的文件（update_mass_excess.txt）
'''
def update_mass_excess(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_all = os.path.join(path_dir,'mass_excess_all')
    path_jina = os.path.join(path_dir,'nuclides_jina.txt')
    path_update = os.path.join(path_dir,'update_mass_excess.txt')
    with open(path_all,'r') as f:
        lines = f.readlines()
        list_all = []
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            list_all.append([int(parts[0]), int(parts[0])+int(parts[1]), (parts[2])])
    with open(path_jina,'r') as f:
        lines = f.readlines()
        list_jina = []
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            list_jina.append([int(parts[1]), int(parts[2])])

    list_update = []
    count = 0
    for nuc_jina in list_jina:
        tag = 0
        for nuc_all in list_all:
            if nuc_all[0] > nuc_jina[0]:
                break
            elif nuc_all[0] > nuc_jina[0]:
                continue
            elif nuc_all[1] == nuc_jina[1]:
                tag = 1
                count += 1
                z = nuc_jina[0]
                a = nuc_jina[1]
                mass_excess = float(nuc_all[2])/1000
        if tag == 0 :
            continue
        list_update.append(f'{z}  {a}  {mass_excess}\n')

    with open(path_update,'w') as f:
        f.writelines(list_update)
    print(f'匹配了 {count} 个核素')


################################################################################
# 第三部分 修改 (n,γ) 反应率
################################################################################


'''
002
通过一个核素，输出 Z A 衰变后产生的核素
如 o19 -> f19
'''
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


'''
008
统计 nucnet 中被 ws4 模型覆盖的 (n,γ) 反应，并排序，生成 gamma_reaction_jina_choice.txt
'''
def choose_gamma_reaction(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_gamma = os.path.join(path_dir,'gamma_reaction_jina.txt')
    path_all = os.path.join(path_dir,'mass_excess_all')
    path_choice = os.path.join(path_dir,'gamma_reaction_jina_choice.txt')
    list_all = []
    with open(path_all,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            list_all.append([int(parts[0]), int(parts[0])+int(parts[1])])

    list_gamma = []
    with open(path_gamma,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
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

    with open(path_choice,'w') as f:
        f.writelines(reactions)


'''
009
为一个 (n,γ) 反应方程生成 talys.inp 文件
输出计算命令，并收集运算结果到 update_gamma_by_python.txt
这个程序只能在 Linux 里面运行
'''
def make_inp(quality_model:str,reaction:str):
    path_dir = os.path.join('.', 'data', 'quality_model', f'{quality_model}')
    path_all = os.path.join(path_dir, 'mass_excess_all')
    path_inp = os.path.join('.', 'talys.inp')
    reaction = reaction.strip()
    parts = reaction.split()
    nuc_gamma_1 = after_element(parts[2])
    nuc_gamma_2 = after_element(parts[4])
    nuc_gamma1_name = parts[2]
    nuc_gamma2_name = parts[4]
    with open(path_all,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            nuc_all = [int(parts[0]), int(parts[0])+int(parts[1]), (parts[2])]
            if nuc_all[0] > nuc_gamma_1[0]:
                break
            elif nuc_all[0] == nuc_gamma_1[0]:
                if nuc_all[1] == nuc_gamma_1[1]:
                    excess_1 = float(nuc_all[2])/1000
                elif nuc_all[1] == nuc_gamma_2[1]:
                    excess_2 = float(nuc_all[2])/1000
    comment = (f'projectile n\n'
               f'element {element[nuc_gamma_1[0]-1]}\n'
               f'mass {nuc_gamma_1[1]}\n'
               f'energy 1.\n'
               f'astro y\n'
               f'massexcess {nuc_gamma_1[0]} {nuc_gamma_1[1]} {excess_1}\n'
               f'massexcess {nuc_gamma_2[0]} {nuc_gamma_2[1]} {excess_2}\n')
    with open(path_inp,'w') as f:
        f.writelines(comment)

    subprocess.run("talys < talys.inp > talys.out", shell=True)

    comment_1 = (f'rate_table\n'
               f'my_ws4\n'
               f'2\n'
               f'{nuc_gamma1_name}\n'
               f'n\n'
               f'2\n'
               f'{nuc_gamma2_name}\n'
               f'gamma\n')
    comment_2 = ''
    path_out = os.path.join('.', 'astrorate.g')
    path_update = os.path.join('.', 'update_gamma_by_python.txt')
    with open(path_out,'r') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            count += 1
            parts = line.split()
            comment_2 += f'{parts[0]}   {parts[1]}\n'
    comment_update = comment_1 + f'{count}\n' + comment_2 + '\n'

    with open(path_update,'a') as f:
        f.writelines(comment_update)





    