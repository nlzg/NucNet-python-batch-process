# 输入文件 ( 在 data 文件中 )
- [abundance_thuxreply](data/abundance_thuxreply)
- [r-process data_in](data/r-process%20data_in)
- [r-process data_out](data/r-process%20data_out)\
输入文件，提供了各个质量模型的 r- 过程模拟结果\
随便选择一个使用
- [stellar](data/stellar)\
包含了多个以天体名称命名的文件夹，如 [BD+17°3248](data/stellar/BD%2B17%C2%B03248) ；\
每个文件夹下包含一个文件 [abundance_log](data/stellar/BD%2B17%C2%B03248/abundance_log) ,
这是该各个核素的观测丰度，\
格式为：[ Z ， 观测丰度(对数坐标) ， 观测误差1 ， 观测误差2 ]\
两个观测误差计算时会取最大值

# 代码
## [age_functions.py](age_functions.py)
可以计算天体年龄

# 输出文件
在以天体命名的文件夹下生成文件 [analysis](data/stellar/BD%2B17%C2%B03248/analysis) ，用于输出计算结果
