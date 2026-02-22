# 输入文件
## 1. [nuclides_jina.txt](nuclides_jina.txt)
JINA 数据库提供的核素列表，格式为： [ 序号 , Z , A , 核素名称 ,质量剩余 ,...] 
## 2. [beta_reaction_jina.txt](beta_reaction_jina.txt)
JINA 数据库提供的 β 衰变反应方程
## 3. [gamma_reaction_jina.txt](gamma_reaction_jina.txt)
JINA 数据库提供的 (n,γ) 反应方程
## 4. [mass_excess_all](mass_excess_all)
使用者自己提供的核素列表，格式为： [ Z , N , 质量剩余 (KeV) ]
## 5. [ws4_T.txt](ws4_T.txt)
使用者自己提供的 β 反应率，格式为 [ Z , N , rate ]

# 代码
##  1. [update_input_quantities.py](update_input_quantities.py)
包含 3 个部分的函数：
- 第一部分可生成文件 update_bata_by_python.txt
- 第二部分可生成文件 update_mass_excess.txt
- 第三部分可生成文件 gamma_reaction_jina_choice.txt

# 输出文件
## 1. update_bata_by_python.txt
用于修改 NucNet 中的 β 反应率
## 2. update_mass_excess.txt
用于修改 NucNet 中的质量剩余 (MeV)
## 3. gamma_reaction_jina_choice.txt
用于计算 (n,y) 反应率
## 4. update_gamma_by_python.txt
用于修改 NucNet 中的（n，γ）反应率，生成步骤见下文

# 计算（n，γ）反应率 步骤
1. 将输出文件 gamma_reaction_jina_choice.txt 复制到文件夹 [计算（n，γ）反应率](%E8%AE%A1%E7%AE%97%EF%BC%88n%EF%BC%8C%CE%B3%EF%BC%89%E5%8F%8D%E5%BA%94%E7%8E%87)
中
2. 将文件夹 [计算（n，γ）反应率](%E8%AE%A1%E7%AE%97%EF%BC%88n%EF%BC%8C%CE%B3%EF%BC%89%E5%8F%8D%E5%BA%94%E7%8E%87)
上传到 Linux 系统中
3. 运行脚本 [begin.py](%E8%AE%A1%E7%AE%97%EF%BC%88n%EF%BC%8C%CE%B3%EF%BC%89%E5%8F%8D%E5%BA%94%E7%8E%87/begin.py)
，脚本中的变量 n 为进程数，可手动修改
4. 运行结束后生成文件 update_gamma_by_python.txt