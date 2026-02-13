import os
from update_input_quantities import make_inp

path_update = os.path.join('.', 'update_gamma_by_python.txt')
gamma_reaction = os.path.join('.', 'data', 'quality_model', 'ws4', 'gamma_reaction_jina_choice.txt')
folder_name = os.path.basename(os.getcwd())
count = 0
open(path_update, 'w').close()
with open(gamma_reaction,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        make_inp('ws4',f'{line}')
        count += 1
        print(f'{folder_name} 计算了第 {count} 个（n，γ）反应率')