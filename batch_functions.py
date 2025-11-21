import os

'''
001
计算 yz_sum 通过 s_final
'''
def putout_yz_sum(s_final:int,quality_model:str,ye:float,s_ref:int):
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
    path_out = os.path.join(path_dir_out,f'yz_s_final{s_final}')
    with open(path_out,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(yz_sum_str)
    print(f'基于质量模型{quality_model},ye = {ye},s_final = {s_final} 的 ye_sum 计算完成')







