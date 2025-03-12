import pandas as pd

df = pd.read_html("EGX30.xls")[0]  # Read the first table
print(df)