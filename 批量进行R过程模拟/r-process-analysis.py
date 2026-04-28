# 这是批量分析 R-过程模拟结果的脚本
# 在 Linux 中运行，运行前执行 conda activate nucnet 命令
import os
import subprocess
import threading

# Ye 列表
Yes = [0.45]
# S 列表
Ss = range(150,351,5)
# 质量模型列表（nucnet， ws4）
models = ['AME+WS4']
# 按什么输出
analysis_types = ['a']

# 单次分析函数
sem = threading.Semaphore(50)
def analysis(model, Ye, S, analysis_type):
    sem.acquire()

    print(f'{model}\t{Ye}\t{S}\t{analysis_type}\t开始分析')

    path_analysis_tools = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'examples', 'analysis')
    path_root = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'input_and_output')
    path_dir = os.path.join(path_root, f'{model}', f'{Ye}', f'{S}')
    path_output = os.path.join(path_dir, 'output.xml')
    path_analysis = os.path.join(path_dir, f'y{analysis_type}.txt')

    cmd1 = (f'cd {path_analysis_tools} && '
            f'./print_abundances_vs_nucleon_number {path_output} {analysis_type} "[last()]" > {path_analysis}')
    proc = subprocess.Popen(cmd1, shell=True)
    proc.wait()
    sem.release()

print('开始分析')
threads = []
for model in models:
    for Ye in Yes:
        for S in Ss:
            for analysis_type in analysis_types:
                t = threading.Thread(target=analysis, args=(model, Ye, S, analysis_type))
                threads.append(t)
                t.start()
for t in threads:
    t.join()
print('全部分析完毕')

# 单次计算 y_sum
def y_sum(model, Ye, Ss:list, analysis_type):
    sem.acquire()

    print(f'{model}\t{Ye}\t{analysis_type}\t开始计算')

    path_root = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'input_and_output')
    path_ye = os.path.join(path_root, f'{model}', f'{Ye}')

    content = []
    for S in Ss:
        path_analysis = os.path.join(path_ye, f'{S}',f'y{analysis_type}.txt')
        with open(path_analysis, 'r') as f:

            if len(content) == 0:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line == '':
                        continue
                    parts = line.split()
                    if len(parts) == 1:
                        continue
                    if parts[0].isdigit() == False:
                        continue

                    content.append([parts[0], float(parts[1])/int(S)])
            else:
                index = 0
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line == '':
                        continue
                    parts = line.split()
                    if len(parts) == 1:
                        continue
                    if parts[0].isdigit() == False:
                        continue

                    content[index][1] += float(parts[1])/int(S)
                    index += 1

    path_y_sum = os.path.join(path_ye, f"y_sum_{analysis_type}.txt")
    with open(path_y_sum, 'w') as f:
        for i in content:
            f.write(f'{i[0]}\t{i[1]:.5e}\n')

    sem.release()

print('开始计算 y_sum')
threads = []
for model in models:
    for Ye in Yes:
        for analysis_type in analysis_types:
            t = threading.Thread(target=y_sum, args=(model, Ye, Ss, analysis_type))
            threads.append(t)
            t.start()

for t in threads:
    t.join()

print('y_sum 计算完毕')