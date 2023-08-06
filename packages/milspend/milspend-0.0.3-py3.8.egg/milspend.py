import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
import warnings
warnings.simplefilter("ignore")
import subprocess as sp
sp.call("wget -nc  https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2022.xlsx",shell=True)

# Load the xlsx file using openpyxl
wb = load_workbook('SIPRI-Milex-data-1949-2022.xlsx')
ws = wb['Constant (2021) US$']

# Delete the first 5 rows and the second and third columns
ws.delete_rows(1, 5)
ws.delete_cols(2, 2)

# Convert the worksheet to a DataFrame
data = ws.values
columns = next(data)[0:]
df = pd.DataFrame(data, columns=columns)

ct=[]
for i in df.Country:
 ct.append(i)
print(ct)
print('Enter up to 4 country names separated by colons: ')

# Convert column names to strings
df.columns = df.columns.astype(str)

# Set the index to be the 'Country' column
df.set_index('Country', inplace=True)
# Ask the user for up to 4 country names separated by colons
import sys
countries = sys.argv[1]
countries=countries.split(':')
print(countries)

def main(countries):
# Define line styles
 line_styles = ['-', '--', '-.', ':']

# Plot the data for each country
 for i, country in enumerate(countries):
    if country in df.index:
        data = df.loc[country, '2000':'2022']
        data.plot(label=country, linestyle=line_styles[i % len(line_styles)], color='k')

# Add labels and legend
 plt.xlabel('Year')
 plt.ylabel('Military Spending (Constant 2021 US$)')
 plt.legend()

# Show the plot
 plt.savefig('result.png')
 plt.show()
 plt.close()
 sys.exit()
main(countries)
