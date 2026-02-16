import os
import subprocess

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

def run(reaction:str):
    path_all = os.path.join('.', 'mass_excess_all')
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
               f'n\n'
               f'{nuc_gamma1_name}\n'
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
            comment_2 += f'{parts[0]}   {parts[1]}  1.00\n'
    comment_update = comment_1 + f'{count}\n' + comment_2 + '\n'

    with open(path_update,'a') as f:
        f.writelines(comment_update)

    folder_name = os.path.basename(os.getcwd())
    path_available = os.path.join("/", "home", "xsli", "projects", "python_new", "available",f'{folder_name}.txt')
    with open(path_available,'w') as f:
        pass

path_reaction = os.path.join('.', 'reaction.txt')
with open(path_reaction,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        run(line)