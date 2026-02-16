import os

original_dir = os.getcwd()
path_available_dir = os.path.join(original_dir, f'available')
n = len(os.listdir(path_available_dir))

update = []
path_run_dir = os.path.join("/", "home", "xsli", "projects", "talys", "run_gamma")
for i in range(n):
    path_run_update = os.path.join(path_run_dir, f'run_{i+1}', 'update_gamma_by_python.txt')
    with open(path_run_update, 'r') as f:
        lines = f.readlines()
        for line in lines:
            update.append(line)
path_update = os.path.join(original_dir, 'update_gamma_by_python.txt')
with open(path_update, 'w') as f:
    f.writelines(update)

print('数据整理完毕')