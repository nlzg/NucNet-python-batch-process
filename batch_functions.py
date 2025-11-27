import math
import os


'''
001
计算 yz_sum 通过 s_final,将极小的数值置零
建议 s_final = 50000
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
    for i in range(len(yz_sum)):
        if yz_sum[i][1] <= s_ref/1e8 :
            yz_sum[i][1] = 0
    yz_sum_str = [ f'{i[0]} {i[1]}\n' for i in yz_sum]
    path_dir_out = f'./data/y_sum/{quality_model}/Ye_{ye}'
    os.makedirs(path_dir_out,exist_ok=True)
    path_out = os.path.join(path_dir_out,f'yz_s_final{s_final}')
    with open(path_out,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(yz_sum_str)
    # print(f'基于质量模型{quality_model},ye = {ye},s_final = {s_final} 的 ye_sum 计算完成')


'''
002
合并同一个 ye 下的 y_sum 文件
表头为：z  s_5  s_10  ...
剔除了 y_sum 全为零的核素
'''
def marge_y_sum_about_ye(quality_model:str, ye:float):
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
    search = 1
    while search != 0:
        search = 0
        for i in range(len(yz_sum)):
            if yz_sum[i][-1] == 0:
                search = 1
                del yz_sum[i]
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
    content = [ f'{yz_vs_s[i][0]}  {yz_vs_s[i][1]:.4e}  {yz_vs_s[i][2]:.4e}\n' for i in range(len(yz_vs_s))]
    path_yz_vs_s = os.path.join(path_dir_yz,f'yz_vs_s_{z}')
    with open(path_yz_vs_s,'w',encoding='utf-8',newline='\n') as f:
        f.write(f'# {quality_model} ye:{ye}\n\n# s 或 s_final  yz  yz_sum\n\n')
        f.writelines(content)
    print(f'已生成 yz_vs_s_{z}')


'''
004
合并同一个 s_final 下的 y_sum 文件
表头为：z  ye_0.4  ye_0.45  ...
剔除了 y_sum = 0 的核素
'''
def marge_y_sum_about_s_final(quality_model:str, s_final:int):
    header = ['z']
    yz_sum = []
    ye = 0.4
    end = 0.481
    step = 0.005
    while ye < end:
        header.append(f'ye_{ye:.3}')
        path_y_sum = os.path.join('./','data','y_sum',f'{quality_model}',f'Ye_{ye:.3}',f'yz_s_final{s_final}')
        with open(path_y_sum,'r',encoding='utf-8',newline='\n') as f:
            if len(yz_sum) == 0:
                for line in f:
                    line = line.strip()
                    if line == '':
                        continue
                    parts = line.split()
                    yz_sum.append([int(parts[0]),float(parts[1])])
            else:
                for line in f:
                    line = line.strip()
                    if line == '':
                        continue
                    parts = line.split()
                    for i in range(len(yz_sum)):
                        if yz_sum[i][0] == int(parts[0]):
                            yz_sum[i].append(float(parts[1]))
                            break
        ye += step
    search = 1
    while search != 0:
        search = 0
        for i in range(len(yz_sum)):
            if yz_sum[i][-1] == 0:
                search = 1
                del yz_sum[i]
                break
    path_marge = os.path.join('./','data','y_sum',f'{quality_model}',f'marge_s_final_{s_final}')
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
    print(f'已生成 marge_s_final_{s_final} 文件')


'''
005
对齐函数：使文件中某一核素的 y_sum 对齐到某一指定的值 align_y
'''
def align_marge_for_z(z:int,align_y:float,path_marge:str):
    ks = []
    comtents = []
    with open(path_marge,'r',encoding='utf-8',newline='\n') as f:
        for line in f:
            line = line.strip()
            parts = line.split()
            comtent = ''
            for i in range(len(parts)):
                comtent += f'{parts[i]}  '
            comtent = comtent.strip()
            comtent += '\n'
            comtents.append(comtent)
            break
    with open(path_marge, 'r', encoding='utf-8', newline='\n') as f:
        for line in f:
            line = line.strip()
            if line == '' or line[0] == 'z':
                continue
            parts = line.split()
            if int(parts[0]) == z:
                for i in range(1,len(parts)):
                    if float(parts[i]) == 0.0:
                        print(f'z = {z} 时，存在 y_sum = 0，不能对齐')
                        return False
                    k = align_y / float(parts[i])
                    ks.append(k)
                break
    with open(path_marge, 'r', encoding='utf-8', newline='\n') as f:
        for line in f:
            line = line.strip()
            if line == '' or line[0] == 'z':
                continue
            parts = line.split()
            for i in range(1,len(parts)):
                parts[i] = float(parts[i])
                parts[i] *= ks[i - 1]
            comtent = ''
            for i in range(len(parts)):
                comtent += f'{parts[i]}  '
            comtent = comtent.strip()
            comtent += '\n'
            comtents.append(comtent)
    with open(path_marge,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(comtents)
    print(f'已将 {path_marge} 文件中 z = {z} 的 y_sum 对齐')


'''
006
当 ye 一定时，计算一系列 s_final 所得出的星体年龄，并输出时钟同步时的 s_final 和年龄
可选：输出年龄随时间变化数据文件
'''
def output_age_by_ye(ye:float,quality_model:str,stellar:str,s_ref:int):
    z = []
    y_x_pre = []
    path_dir_stellar = f'./data/stellar/{stellar}'
    path_y_pre = os.path.join(path_dir_stellar,'abundance_pre')
    with open(path_y_pre,'r',encoding='utf-8',newline='\n') as f:
        for line in f:
            line = line.strip()
            if line == '' or line[0] == 'z':
                continue
            parts = line.split()
            if parts[0] == '90':
                y_th_pre = float(parts[1])
            elif parts[0] == '92':
                y_u_pre = float(parts[1])
            else:
                z.append(int(parts[0]))
                y_x_pre.append(float(parts[1]))
    th_x_i_pre = [y_th_pre / x for x in y_x_pre]
    u_x_i_pre = [y_u_pre / x for x in y_x_pre]
    th_u_pre = y_th_pre / y_u_pre
    a = len(z)

    path_dir_y_ini = f'./data/y_sum/{quality_model}/Ye_{ye}'
    path_y_ini = os.path.join(path_dir_y_ini,f'marge_ye_{ye}')
    with open(path_y_ini,'r',encoding='utf-8',newline='\n') as f:
        for line in f:
            parts = line.split()
            s_finals = [int(part[2:]) for part in parts if part != 'z']
            break

    path_age_by_ye_dir = f'./data/stellar/{stellar}/{quality_model}'
    os.makedirs(path_age_by_ye_dir, exist_ok=True)
    path_age_by_ye = os.path.join(path_age_by_ye_dir,f'ye_{ye}')
    with open(path_age_by_ye,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(f's_final  th/x  u/x  th/u\n')
    y_x_ini = []
    z_ini = []
    no_z = []
    for s_final in s_finals:
        y_x_ini.clear()
        z_ini.clear()
        unsuitable = False
        with open(path_y_ini,'r',encoding='utf-8',newline='\n') as f:
            inedx = s_finals.index(s_final) + 1
            for line in f:
                line = line.strip()
                if line == '' or line[0] == 'z':
                    continue
                parts = line.split()
                if int(parts[0]) == 90:
                    if float(parts[inedx]) == 0.0:
                        unsuitable = True
                        break
                    y_th_ini = float(parts[inedx])
                elif int(parts[0]) == 92:
                    if float(parts[inedx]) == 0.0:
                        unsuitable = True
                        break
                    y_u_ini = float(parts[inedx])
                elif int(parts[0]) in z:
                    if float(parts[inedx]) == 0.0:
                        unsuitable = True
                        break
                    y_x_ini.append(float(parts[inedx]))
                    z_ini.append(int(parts[0]))

        if unsuitable:
            continue
        b = len(z_ini)
        no_z.clear()
        if a != b:
            for i in range(len(z)):
                if z[i] not in z_ini:
                    no_z.append(z[i])
        y_u_ini = get_u238_y_sum(quality_model=quality_model,ye=ye,s_final=s_final,s_ref=s_ref)
        th_x_i_ini = [y_th_ini / x for x in y_x_ini]
        u_x_i_ini = [y_u_ini / x for x in y_x_ini]
        th_u_ini = y_th_ini / y_u_ini
        age_th_x_i = []
        for i in range(len(z)):
            d = 0
            if z[i] in no_z:
                d = no_z.index(z[i])
                continue
            j = i - d
            age = 46.67 * ( math.log10( th_x_i_ini[j] ) - math.log10( th_x_i_pre[i] ) )
            age_th_x_i.append(age)
        age_th_x = sum(age_th_x_i) / len(age_th_x_i)
        age_u_x_i = []
        for i in range(len(z)):
            d = 0
            if z[i] in no_z:
                d = no_z.index(z[i])
                continue
            j = i - d
            age = 14.84 * ( math.log10( u_x_i_ini[j] ) - math.log10( u_x_i_pre[i] ) )
            age_u_x_i.append(age)
        age_u_x = sum(age_u_x_i) / len(age_u_x_i)
        age_th_u = -21.8 * (math.log10( th_u_ini ) - math.log10( th_u_pre ) )
        with open(path_age_by_ye,'a',encoding='utf-8',newline='\n') as f:
            f.writelines(f'{s_final}  {age_th_x}  {age_u_x}  {age_th_u}\n')

    with open(path_age_by_ye,'r',encoding='utf-8',newline='\n') as f:
        change = 0
        for line in f:
            line = line.strip()
            if line == '' or line[0] == 's':
                continue
            parts = line.split()
            if float(parts[3]) > float(parts[2]):
                th_u_a = float(parts[3])
                u_x_a = float(parts[2])
                s_final_a = int(parts[0])
            else:
                th_u_b = float(parts[3])
                u_x_b = float(parts[2])
                s_final_b = int(parts[0])
                change = 1
                break
        if change == 1:
            best_s_final = (s_final_b - s_final_a) * (th_u_a - u_x_a) / (th_u_a - u_x_a + u_x_b - th_u_b) + s_final_a
            best_age = (th_u_b - th_u_a) * (th_u_a - u_x_a) / (th_u_a - u_x_a + u_x_b - th_u_b) + th_u_a


    path_age = os.path.join(path_age_by_ye_dir,f'ages')
    if change == 1:
        with open(path_age,'a+',encoding='utf-8',newline='\n') as f:
            comtents = []
            if os.path.getsize(path_age) == 0:
                comtents.append('ye  s_final  age\n')
            comtents.append(f'{ye}  {best_s_final}  {best_age}\n')
            f.writelines(comtents)

    print(f'{quality_model} 利用 {quality_model} 质量模型在 ye={ye} 条件下的年龄计算完成')


'''
007
计算 u238 在 s_final 下的 y_sum 
'''
def get_u238_y_sum(quality_model:str, ye:float, s_final:int, s_ref:int):
    path_u238_dir = f'./data/abundance_thuxreply/{quality_model}/Ye_{ye}'
    y_sum = 0.0
    for s in range(5,s_final+1,5):
        path_u238 = os.path.join(path_u238_dir,f'yza_S{s}')
        with open(path_u238,'r',encoding='utf-8',newline='\n') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                parts = line.split()
                if int(parts[0]) == 92 and int(parts[1]) == 238:
                    y_sum += float(parts[2]) * s_ref / s
    return y_sum


'''
008
将天体的观测丰度从 log 转化为 float
'''
def stellar_abundance_from_log_to_float(stellar:str):
    path_dir = f'./data/stellar/{stellar}'
    path_log = os.path.join(path_dir,'abundance_log')
    comtents = ['z  abundance\n']
    with open(path_log,'r',encoding='utf-8',newline='\n') as f:
        for line in f:
            line = line.strip()
            if line == '' or line[0] == 'z':
                continue
            parts = line.split()
            z = int(parts[0])
            abundance = 10 ** float(parts[1])
            comtents.append(f'{z}  {abundance}\n')
    path_pre = os.path.join(path_dir,'abundance_pre')
    with open(path_pre,'w',encoding='utf-8',newline='\n') as f:
        f.writelines(comtents)


'''
集合了上述函数：通过 r 过程模拟结果，预测星体的年龄
'''
def output_stellar_age(stellar:str):
    stellar_abundance_from_log_to_float(stellar)
    s_ref = 50000
    quality_models = os.listdir(f'./data/abundance_thuxreply')
    for i in range(len(quality_models)):
        if quality_models[i] == 'output':
            del quality_models[i]
            break

    for quality_model in quality_models:
        path_ye_dir = f'./data/abundance_thuxreply/{quality_model}'
        yes = os.listdir(path_ye_dir)
        for i in range(len(yes)):
            yes[i] = yes[i][3:]
        path_age_dir = f'./data/stellar/{stellar}/{quality_model}'
        os.makedirs(path_age_dir,exist_ok=True)
        path_age = os.path.join(path_age_dir, 'ages')
        with open(path_age, 'w', encoding='utf-8', newline='\n') as f:
            f.write('')
        for ye in yes:
            for s_final in range(5, 401, 5):
                putout_yz_sum(s_final=s_final, quality_model=quality_model, ye=float(ye), s_ref=s_ref)
            marge_y_sum_about_ye(quality_model=quality_model, ye=float(ye))
            output_age_by_ye(quality_model=quality_model, ye=float(ye), stellar=stellar, s_ref=s_ref)

    print(f'天体 {stellar} 的年龄计算完成')

# output_stellar_age('J2038−0023')
# output_age_by_ye(ye=0.455, quality_model='hfb24', stellar='J2038−0023', s_ref=50000)