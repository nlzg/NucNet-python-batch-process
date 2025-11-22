import os

'''
001
计算 yz_sum 通过 s_final
'''
def putout_yz_sum(s_final:int,quality_model:str,ye:float,s_ref:float):
    s = 5
    yz_sum = []
    while s <= s_final:
        path_dir_yz = f'./data/abundance_thuxreply/{quality_model}/Ye_{ye}'
        path_yz = os.path.join(path_dir_yz,f'yz_s{s}')
        with open(path_yz,'r',encoding='utf-8',newline='\n') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                parts = line.split()
                new_y = float(parts[1]) * s_ref / s
                search = 0
                for i in range(len(yz_sum)):
                    if yz_sum[i][0] == int(parts[0]):
                        yz_sum[i][1] += new_y
                        search = 1
                        break
                if search == 0:
                    yz_sum.append([int(parts[0]),new_y])
        s += 5
    yz_sum_str = [ f'{i[0]} {i[1]}\n' for i in yz_sum]
    path_dir_out = f'./data/y_sum/{quality_model}/Ye_{ye}'
    os.makedirs(path_dir_out,exist_ok=True)
    path_out = os.path.join(path_dir_out,f'yz_s_final{s_final}')
    with open(path_out,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(yz_sum_str)
    print(f'基于质量模型{quality_model},ye = {ye},s_final = {s_final} 的 ye_sum 计算完成')


'''
002
合并同一个 ye 下的 y_sum 文件
表头为：z  s_5  s_10  ...
'''
def marge_y_sum_with_ye(quality_model:str,ye:float):
    path_dir_y_sum = f'./data/y_sum/{quality_model}/Ye_{ye}'
    header = ['z']
    yz_sum = []
    for s_final in range(5,401,5):
        header.append(f's_{s_final}')
        path_y_sum = os.path.join(path_dir_y_sum,f'yz_s_final{s_final}')
        with open(path_y_sum,'r',encoding='utf-8',newline='\n') as f:
            if len(yz_sum) == 0:
                for line in f:
                    line = line.strip()
                    parts = line.split()
                    yz_sum.append([int(parts[0]),float(parts[1])])
            else:
                for line in f:
                    line = line.strip()
                    parts = line.split()
                    for i in range(len(yz_sum)):
                        if yz_sum[i][0] == int(parts[0]):
                            yz_sum[i].append(float(parts[1]))
                            break
    path_marge = os.path.join(path_dir_y_sum,f'marge_ye_{ye}')
    with open(path_marge,'w',encoding='utf-8',newline='\n') as f:
        header_str = ''
        for i in header:
            header_str += f'{i}  '
        header_str = header_str.strip()
        header_str += '\n'
        f.write(header_str)
        yz_sum_str = []
        for i in range(len(yz_sum)):
            comment = ''
            for j in range(len(yz_sum[i])):
                comment += f'{yz_sum[i][j]}  '
            comment = comment.strip()
            comment += '\n'
            yz_sum_str.append(comment)
        f.writelines(yz_sum_str)
    print(f'已生成 marge_ye_{ye} 文件')


'''
003
检索某一核素 yz、yz_sum 随 s 的变化
'''
def output_yz_vs_s(quality_model:str,ye:float,z:int):
    path_dir_yz = f'./data/abundance_thuxreply/{quality_model}/Ye_{ye}'
    path_dir_yz_sum = f'./data/y_sum/{quality_model}/Ye_{ye}'
    yz_vs_s = []
    for s in range(5,401,5):
        one_s = [s]
        path_yz = os.path.join(path_dir_yz,f'yz_s{s}')
        with open(path_yz,'r',encoding='utf-8',newline='\n') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                parts = line.split()
                if int(parts[0]) == z:
                    one_s.append(float(parts[1]))
        path_yz_sum = os.path.join(path_dir_yz_sum,f'yz_s_final{s}')
        with open(path_yz_sum,'r',encoding='utf-8',newline='\n') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                parts = line.split()
                if int(parts[0]) == z:
                    one_s.append(float(parts[1]))
        yz_vs_s.append(one_s)
    content = [ f'{yz_vs_s[i][0]}  {yz_vs_s[i][1]}  {yz_vs_s[i][2]}\n' for i in range(len(yz_vs_s))]
    path_yz_vs_s = os.path.join(path_dir_yz,f'yz_vs_s_{z}')
    with open(path_yz_vs_s,'w',encoding='utf-8',newline='\n') as f:
        f.write(f'# {quality_model} ye:{ye}\n\n# s 或 s_final  yz  yz_sum\n\n')
        f.writelines(content)
    print(f'已生成 yz_vs_s_{z}')






