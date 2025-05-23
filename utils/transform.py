import pandas as pd


class Transformer:
    def __init__(self):
        self.dirty_patterns = {
            "Title": ["Unknown Product"],
            "Rating": ["Invalid Rating", "Not Rated"],
            "Price": ["Price Unavailable", None],
            }
        
    def remove_dirty(self, df: pd.DataFrame):
        mask = pd.Series(True, index=df.index)
        for col, dirty_values in self.dirty_patterns.items():
            if col in df.columns:  # Ensure column exists
                mask &= ~df[col].isin(dirty_values)
        return df[mask].reset_index(drop=True)
    
    def convert_type(self, df: pd.DataFrame):
        try:
            df["Rating"] = pd.to_numeric(df["Rating"])
        except ValueError as e:
            raise ValueError("Could not convert Rating column to numeric") from e
        return df
    
    def clean(self, df: pd.DataFrame):
        df = self.remove_dirty(df)
        df.dropna(inplace=True, how="all")
        return self.convert_type(df)
        