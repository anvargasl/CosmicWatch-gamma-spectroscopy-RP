import pandas as pd

df = pd.read_csv("../data/PICO/bkgd.txt", delimiter="\t", skiprows=1, names=["event", "adc", "deadt"])

duplicates = df["event"].duplicated()
print(df.loc[duplicates])

