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
def get_new_beta(quality_model:str):
    path_dir = os.path.join(r'.\data\quality_model', f'{quality_model}')
    path_all = os.path.join(path_dir,'mass_excess_all')
    path_beta = os.path.join(path_dir,'net_beta.txt')
    path_new_beta = os.path.join(path_dir,'new_beta.txt')
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
            list1.append(element[int(parts[0]) - 1] + parts[1])

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
通过一个核素，输出衰变后产生的核素
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
    if next_index == len(element):
        return 0
    else:
        next_name = element[next_index]
        next_ele = next_name + a
        return next_ele

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

get_beta_rate('ws4')

    