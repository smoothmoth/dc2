import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def plot_line_graph(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    grouped_df = df.groupby('Period')

    for name, group in grouped_df:
        plt.figure(figsize=(10, 6))
        for column in ['Trust in MPS', 'Worry about crime', 'Good job local']:
            plt.plot(group['FY & Quarter'], group[column], label=column)

        plt.xlabel('FY & Quarter')
        plt.ylabel('Value')
        plt.title(f'Line Graph for {name}')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.show()

file_path = 'DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx'
sheet_name = 'PAS London Level'

plot_line_graph(file_path, sheet_name)
