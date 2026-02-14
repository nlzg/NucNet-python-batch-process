import os.path
import shutil
import subprocess

n = 50

original_dir = os.getcwd()
all_reaction = os.path.join(original_dir, 'gamma_reaction_jina_choice.txt')
path_make_all = os.path.join("/", "home", "xsli", "projects", "talys", "run_gamma")
if os.path.exists(path_make_all):
    shutil.rmtree(path_make_all, ignore_errors=True)
os.makedirs(path_make_all, exist_ok=True)
with open(all_reaction, 'r') as f:
    lines = f.readlines()
    count = 0
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        count += 1
leng = int(count / n) + 1

for i in range(n):
    path_source = os.path.join(original_dir, 'run_gamma')
    path_target = os.path.join(path_make_all, f'run_{i+1}')
    shutil.copytree(path_source, path_target)
    wri = []
    with open(all_reaction, 'r') as f:
        a = 0
        lines = f.readlines()
        for line in lines:
            if line == '':
                continue
            else:
                a += 1
            if a > leng * (i + 1):
                break
            elif a <= leng * i:
                continue
            else:
                wri.append(line)
    gamma_reaction = os.path.join(path_target, 'data', 'quality_model', 'ws4', 'gamma_reaction_jina_choice.txt')
    with open(gamma_reaction, 'w') as f:
        f.writelines(wri)
    os.chdir(path_target)
    subprocess.Popen("python3 batch_main.py", shell=True)


