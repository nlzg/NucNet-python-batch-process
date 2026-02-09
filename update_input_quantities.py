import math
import os

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
通过 ws4_T 生成 β 反应率文件（ws4_beta）
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
函数汇总
'''
choose_beta_reaction('ws4')
get_beta_rate('ws4')
update_beta_reaction_by_txt('ws4')
    