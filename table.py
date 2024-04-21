"""Formating the reports into LaTeX tables"""

import pandas as pd


def relative_inst_count(df: pd.DataFrame):
    """Total Instructions or ROM code and their respective relative value"""
    col_name = (
        "Total Instructions" if "Total Instructions" in df.columns else "ROM code"
    )
    df2 = df.iloc[1::2].sort_values(by=col_name + " (rel.)", ascending=False)
    print(f"Average: {df2[col_name + ' (rel.)'].mean():.2f}")
    print(
        df2.to_latex(
            columns=["Model", col_name, col_name + " (rel.)"],
            index=False,
            float_format="%.2f",
        )
    )
