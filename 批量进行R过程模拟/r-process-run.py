# 这是批量进行高熵风R-过程模拟的脚本
#使用前先开启 conda 环境
import os
import subprocess
import sys
import threading

from tqdm import tqdm

# Ye 列表
Yes = [0.45]
# S 列表
Ss = range(150,351,5)
# 质量模型列表（jina， ws4）
models = sys.argv[2:] #例：['AME+WS4']
# 最大并发数
MAX_THREADS = int(sys.argv[1]) #例：50
sem = threading.Semaphore(MAX_THREADS)
#定义一个单次计算函数
def run(model, Ye, S):

    sem.acquire()

    print(f'{model}\t{Ye}\t{S}\t开始计算')

    path_misc = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'examples', 'misc')
    path_my_net = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'data_pub', 'my_net.xml')
    path_root = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'input_and_output')
    path_dir = os.path.join(path_root, f'{model}', f'{Ye}', f'{S}')
    os.makedirs(path_dir, exist_ok=True)

    # 准备输入文件
    path_zone = os.path.join(path_dir, 'zone.xml')
    path_lod = os.path.join(path_dir, 'lod.txt')
    with open(path_lod, 'w') as f:
        content = (f'0 1 {1 - Ye}\n'
                   f'1 1 {Ye}')
        f.write(content)
    cmd1 = (f'cd {path_misc} && '
            f'./create_zone_xml_from_text {path_my_net} {path_lod} {path_zone} "abundances" "[z <= 10]"')
    subprocess.call(cmd1, shell=True)

    path_props = os.path.join(path_dir, 'props.txt')
    with open(path_props, 'w') as f:
        content = (f'iterative solver method\n'
                   f'gmres\n'
                   f'\n'
                   f't9 for iterative solver\n'
                   f'2.\n'
                   f'\n'
                   f'steps\n'
                   f'20\n'
                   f'\n'
                   f'tend\n'
                   f'1.e6\n'
                   f'\n'
                   f'munuekT\n'
                   f'-inf\n'
                   f'\n'
                   f'v_exp\n'
                   f'7500\n'
                   f'\n'
                   f'r_0\n'
                   f'130\n'
                   f'\n'
                   f't9_0\n'
                   f'9\n'
                   f'\n'
                   f's\n'
                   f'{S}\n')
        f.write(content)
    cmd2 = (f'cd {path_misc} && '
            f'./add_properties_to_zone_xml {path_my_net} {path_zone} 0 0 0 {path_props} {path_zone}')
    subprocess.call(cmd2, shell=True)

    # 开始计算
    path_model_dir = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'switch-mass-model')
    path_network = os.path.join(path_model_dir, f'{model}', f'net_{model}.xml')
    path_run = os.path.join('/', 'home', 'xsli', 'projects', 'nucnet-tools-code', 'my_examples', 'network')
    path_output = os.path.join(path_dir, 'output.xml')
    cmd3 = (f'cd {path_run} && '
            f'./run_single_zone {path_network} {path_zone} {path_output} "[z <= 90]" > /dev/null 2>&1')
    proc = subprocess.Popen(cmd3, shell=True)
    proc.wait()

    sem.release()

print('开始计算')
## 启动多线程
threads = []
for model in models:
    for Ye in Yes:
        for S in Ss:
            t = threading.Thread(target=run, args=(model, Ye, S))
            threads.append(t)
            t.start()
for t in tqdm(threads, desc="计算进度"):
    t.join()

print('全部计算完成')