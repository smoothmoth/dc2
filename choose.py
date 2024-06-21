# Python学习
# 测试人：周晨骁
# 开发时间： 2024/6/12 8:47
import pandas as pd

df = pd.read_csv('2.csv',encoding='UTF-8',low_memory=False)
df1=df[['MONTH','ward_n','C2','Q1','Q13','Q60','Q61','Q62A','Q62C','Q62F','Q62TG','A121','Q131','Q133','NQ135BD','NQ135BH','Q65','Q79E','Q79J','Q136r','NQ147r','XQ135r']]

# df3=pd.merge(df1,df2,on='common_column', how='inner')
# print(df3)
df1.to_csv('text.csv',index=False)
