path_1 = r"C:\Users\sleep\Desktop\talys.out"
path_2 = r"D:\Users\sleep\Documents\xwechat_files\wxid_zz3w6nsle65x22_07e4\msg\file\2026-04\talys.log"
path_dif = r"C:\Users\sleep\Desktop\dif.txt"

log_1 = []
log_2 = []
dif = []
with open(path_1,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        log_1.append(line)
with open(path_2,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        log_2.append(line)
for i in range(len(log_1)):
    if log_1[i] != log_2[i]:
        dif.append(f'{log_1[i]}\t(1)\n{log_2[i]}\t(2)\n')
with open(path_dif,'w') as f:
    f.writelines(dif)