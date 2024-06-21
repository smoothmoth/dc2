# Python学习
# 测试人：周晨骁
# 开发时间： 2024/5/22 3:49
import glob
import os
import pandas as pd
import xlrd
import xlsxwriter

# inputfile = str(os.path.dirname(os.getcwd())) + "\dc2\combine_csv" + "\csv\*.csv"
# outputfile = str(os.path.dirname(os.getcwd())) + "\dc2\combine_csv" + "\csv\\testall.csv"
inputfile = r"C:\Users\User\Desktop\University\Y2\Q4\Data Challenge 2\Data Challenge 2" + r"\combine_csv\*.csv" # Insert the path to the project directory into the first citation marks
outputfile = r"C:\Users\User\Desktop\University\Y2\Q4\Data Challenge 2\Data Challenge 2" + r"\combine_csv\\PAS_joined.csv"  # Insert the path to the project directory into the first citation marks
csv_list = glob.glob(inputfile)

print(csv_list)
filepath = csv_list[0]
df = pd.read_csv(filepath, encoding="gbk", low_memory=False)
df = df.to_csv(outputfile, encoding="gbk", index=False)

for i in range(1, len(csv_list)):
    filepath = csv_list[i]
    df = pd.read_csv(filepath, encoding="gbk", low_memory=False)
    df = df.to_csv(outputfile, encoding="gbk", index=False, header=False, mode='a+')


# def open_xls(fil):
#     f = xlrd.open_workbook(fil)
#     return f

# def getsheet(f):
#     return f.sheets()

# def get_Allrows(f, sheet):
#     table = f.sheets()[sheet]
#     return table.nrows

# def getFile(fil, shnum):
#     f = open_xls(fil)
#     table = f.sheets()[shnum]
#     num = table.nrows
#     for row in range(num):
#         rdata = table.row_values(row)
#         datavalue.append(rdata)
#     return datavalue

# def getshnum(f):
#     x = 0
#     sh = getsheet(f)
#     for sheet in sh:
#         x += 1
#     return x


# if __name__ == '__main__':
#     allxls = ['PAS_ward_level_FY_15_17.csv',
#               'PAS_ward_level_FY_17_18.csv',
#               'PAS_ward_level_FY_18_19.csv',
#               'PAS_ward_level_FY_19_20.csv'
#               ]

#     datavalue = []
#     for fl in allxls:
#         f = open_xls(fl)
#         x = getshnum(f)
#         for shnum in range(x):
#             print("正在读取文件：" + str(fl) + "的第" + str(shnum) + "个sheet表的内容...")
#             rvalue = getFile(fl, shnum)

#     endfile = '结果.xls'
#     wb = xlsxwriter.Workbook(endfile)

#     ws = wb.add_worksheet()
#     for a in range(len(rvalue)):
#         for b in range(len(rvalue[a])):
#             c = rvalue[a][b]
#             ws.write(a, b, c)
#     wb.close()

#     print("文件合并完成")
