"""Functions to plot the reports"""

import ast
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd


# TODO adapt functions to use the report df


def dump(row_count: int = 20):
    """Plots the default mlonmcu instruction dump"""
    path = "dump_counts.csv"
    instruction_counts = pd.read_csv(path)
    instruction_counts.fillna("UNKNOWN", inplace=True)
    # the data is already sorted in descending order
    instruction_counts.sort_values(by=["Count"], inplace=True)
    top_n = instruction_counts.head(n=row_count)

    fig, ax = plt.subplots()
    # plt.subplots_adjust(bottom=0.25)
    ax.bar(x=top_n["Instruction"], height=top_n["Count"])
    ax.tick_params(axis="x", labelrotation=90)

    plt.show()


def analyse_inst(df: pd.DataFrame):
    """Plots the Major Opcode against the instruction Count"""
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    ax.bar(x=df["Major"], height=df["Count"])
    ax.tick_params(axis="x", labelrotation=90)

    plt.show()


def combined_instruction_count(df: pd.DataFrame):
    """Sums up the Instruction counts and plots them"""
    col_name = "TraceCountsGen" if "TraceCountsGen" in df.columns else "DumpCountsGen"
    # Removing Benchmarks with no generated instructions and turning the "dicts" into real dicts
    df2 = df[(df[col_name] != "{}") & (df[col_name].notna())]
    df2.loc[:, col_name] = df2[col_name].apply(ast.literal_eval)

    instruction_counts = (
        pd.DataFrame(df2[col_name].tolist(), index=df2["Model"])
        .fillna(0)
        .astype("int32")
        .sum()
        .sort_values()
    )
    ax = instruction_counts.plot.barh()
    # new_df.plot.barh()
    ax.set_xscale("log")
    ax.bar_label(ax.containers[0], padding=4)  # type: ignore
    ax.set_xlim(left=None, right=3000)
    plt.subplots_adjust(left=0.2)
    plt.show()


def instruction_count_across_benchmarks(df: pd.DataFrame):
    """df: DataFrame containing the instruction count across models"""
    col_name = "TraceCountsGen" if "TraceCountsGen" in df.columns else "DumpCountsGen"
    # Removing Benchmarks with no generated instructions and turning the "dicts" into real dicts
    df2 = df[(df[col_name] != "{}") & (df[col_name].notna())]
    df2.loc[:, col_name] = df2[col_name].apply(ast.literal_eval)

    instructions_per_model = (
        pd.DataFrame(df2[col_name].tolist(), index=df2["Model"])
        .fillna(0)
        .astype("int32")
    )
    # Sorting the columns by their sums
    sums = instructions_per_model.sum()
    instructions_per_model = instructions_per_model[
        sums.sort_values(ascending=False).index
    ]
    # side by side for comparison
    # fig, axes = plt.subplots(nrows=1, ncols=2)
    # new_df.plot.barh(stacked=True, ax=axes[0])
    # new_df.T.plot.barh(stacked=True, ax=axes[1])
    # axes[1].set_ylabel("Instructions")
    ax = instructions_per_model.plot.barh(stacked=True, figsize=(10, 7))
    # ax.set_xscale("log")
    ax.set_ylabel("Benchmarks")
    ax.legend(title="Instructions")
    # plt.subplots_adjust(left=0.15)
    plt.tight_layout(pad=1)

    plt.show()


def compare_relative_inst_count(df: pd.DataFrame):
    """Plots either the relative Instruction count or the relative ROM size for each benchmark"""
    # bench_instr_count = df.loc[df["Total Instructions (rel.)"] != 1.0]
    # ax = df.plot.bar(x="Model", y="Total Instructions (rel.)", rot=90)
    # plt.show()

    col_name = (
        "Total Instructions (rel.)"
        if "Total Instructions (rel.)" in df.columns
        else "ROM code (rel.)"
    )
    df2 = df.iloc[1::2].sort_values(by=col_name, ascending=True)
    ax = df2.plot.barh(x="Model", y=col_name)
    ax.set_xlim(df2[col_name].min() - 0.1, df2[col_name].max() + 0.1)
    ax.bar_label(ax.containers[0], fmt="%.2f")
    plt.axvline(1, color="black", ls="--", lw=1)
    plt.tight_layout(pad=1)

    plt.show()


# Not used
def compare_runs(report: pd.DataFrame):
    # This should be the same as in one of the mlonmcu examples
    columns = ["ROM code", "Total Instructions"]

    # collumns to plot: ROM code & Total Instructions
    fig, axs = plt.subplots(1, len(columns))
    axs: list[matplotlib.axes.Axes]
    for i, col in enumerate(columns):
        # axs[i].bar(x=report["config_etiss.arch"].astype(str), height=report[col])
        report.plot(x="config_etiss.arch", y=col, kind="bar", ax=axs[i])

    plt.show()
