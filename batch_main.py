path_AME = r"D:\Users\sleep\Documents\xwechat_files\wxid_zz3w6nsle65x22_07e4\msg\file\2026-04\AME2012(1).txt"
path_new_AME = r"C:\Users\sleep\Desktop\AME2012.txt"
datas = []
with open(path_AME,'r') as f:
    count = 0
    lines = f.readlines()
    for line in lines:
        count += 1
        if count < 40:
            continue
        line = line.strip()
        parts = line.split()
        for part in parts:
            try:
                int(part)
            except:
                index = parts.index(part)
                break
        z = parts[index - 2]
        n = parts[index - 3]
        try:
            float(parts[index + 1])
            mass_excess = parts[index + 1]
        except:
            mass_excess = parts[index + 2]
        tag = 0
        for item in mass_excess:
            if item == '#':
                tag = 1
                break
        if tag == 1:
            continue
        datas.append([int(z),int(n),mass_excess])
new_datas = []
for data in datas:
    if len(new_datas) == 0:
        new_datas.append(data)
    else:
        for item in new_datas:
            if data[0] == item[0]:
                if data[1] < item[1]:
                    index = new_datas.index(item)
                    new_datas.insert(index,data)
                    break
            if data[0] < item[0]:
                index = new_datas.index(item)
                new_datas.insert(index,data)
                break
            if new_datas.index(item) == len(new_datas) - 1:
                new_datas.append(data)
                break
with open(path_new_AME,'w') as f:
    for data in new_datas:
        f.write(f'{data[0]}\t{data[1]}\t{data[2]}\n')

# %%
path_ws4 = r'D:\mine\python\NucNet-python-batch-process\修改核物理输入量\mass_excess_all'
ws4 = []
with open(path_ws4,'r') as f:
    for line in f.readlines():
        line = line.strip()
        if line == '':
            continue
        parts = line.split()
        ws4.append([int(parts[0]),int(parts[1]),parts[2]])

for i in range(len(ws4)):
    for data in new_datas:
        if data[0] == ws4[i][0] and data[1] == ws4[i][1]:
            ws4[i].append(data[2])
            break
path_mass_excess_AME_WS4 = r'C:\Users\sleep\Desktop\mass_excess_AME+WS4.txt'
with open(path_mass_excess_AME_WS4,'w') as f:
    f.write('#%4s%5s%15s%15s\n' % ('Z','N','WS4','AME'))
    for data in ws4:
        if len(data) == 3:
            f.write(f'{data[0]:>5}{data[1]:>5}{data[2]:>15}\n')
        else:
            f.write(f'{data[0]:>5}{data[1]:>5}{data[2]:>15}{data[3]:>15}\n')