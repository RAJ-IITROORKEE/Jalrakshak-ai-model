import pandas as pd

def load_data(path):
    df = pd.read_csv(path)

    # Keep only sensor friendly features
    df = df[['ph','Solids','Conductivity','Turbidity','Potability']]

    # Rename columns
    df.rename(columns={
        'ph':'ph',
        'Solids':'tds',
        'Conductivity':'conductivity',
        'Turbidity':'turbidity',
        'Potability':'potability'
    }, inplace=True)

    # Fill missing values
    df.fillna(df.mean(numeric_only=True), inplace=True)

    return df