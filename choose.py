
import pandas as pd

for fil in ['PAS_ward_level_FY_15_17', 'PAS_ward_level_FY_17_18','PAS_ward_level_FY_18_19','PAS_ward_level_FY_19_20']:
    df = pd.read_csv(fil+".csv",encoding='UTF-8',low_memory=False) 
    df1=df[['MONTH','ward_n','C2','Q1','Q13','Q60','Q61','Q62A','Q62C','Q62F','Q62TG','A121','Q131','Q133','NQ135BD','NQ135BH','Q65','Q79E','Q79J','Q136r','NQ147r','XQ135r']]
    df1.to_csv(fil+'_prep.csv',index=False)
