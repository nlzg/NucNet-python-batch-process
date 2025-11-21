from batch_functions import putout_yz_sum
for s_final in range(5,401,5):
    putout_yz_sum(s_final,quality_model='ws4',ye=0.45,s_ref=300)