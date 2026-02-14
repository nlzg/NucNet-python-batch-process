import os
import shutil
import subprocess

n = 50

original_dir = os.getcwd()
all_reaction = os.path.join(original_dir, 'gamma_reaction_jina_choice.txt')
path_make_all = os.path.join("/", "home", "xsli", "projects", "talys", "run_gamma")
if os.path.exists(path_make_all):
    shutil.rmtree(path_make_all, ignore_errors=True)
os.makedirs(path_make_all, exist_ok=True)
for i in range(n):
    path_source = os.path.join(original_dir, 'data_to_cp')
    path_target = os.path.join(path_make_all, f'run_{i+1}')
    shutil.copytree(path_source, path_target)
    path_available = os.path.join(original_dir, f'available', f'run_{i+1}.txt')
    with open(path_available, 'w') as f:
        pass
print('进程创建完成，开始分配任务')
subprocess.Popen("python3 distribute.py", shell=True)


