import os
import subprocess

print('\n')

original_dir = os.getcwd()
path_available_dir = os.path.join(original_dir, f'available')
path_reaction_all = os.path.join(original_dir, 'gamma_reaction_jina_choice.txt')
n = len(os.listdir(path_available_dir))
with open(path_reaction_all, 'r') as f:
    lines = f.readlines()
    cp = 0
    for line in lines:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        cp += 1
        files = os.listdir(path_available_dir)
        while len(files) == 0:
            files = os.listdir(path_available_dir)
        run_name = files[0].split('.')[0]
        path_run = os.path.join("/", "home", "xsli", "projects", "talys", "run_gamma", run_name)
        path_reaction = os.path.join(path_run, 'reaction.txt')
        with open(path_reaction, 'w') as f:
            f.write(line)
        os.chdir(path_run)
        subprocess.Popen("python3 run.py", shell=True)
        os.chdir(original_dir)
        os.remove(os.path.join(path_available_dir, files[0]))
        print(f'{run_name} 开始计算第 {cp} 个反应')

files = os.listdir(path_available_dir)
while len(files) < n:
    files = os.listdir(path_available_dir)
print('计算完毕')

subprocess.Popen("python3 end.py", shell=True)
