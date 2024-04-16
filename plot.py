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


def instruction_count(data: dict):
    """Plots data.key against data.value\n
    Used to plot the instruction count if its supplied as a dict"""
    fig = plt.figure()
    ax: matplotlib.axes.Axes = fig.subplots()  # type: ignore
    x, y = zip(*sorted(data.items(), key=lambda x: x[1]))
    ax.bar(x=x, height=y)
    # ax.plot("Instruction", "Count", data=data)
    plt.show()


def instruction_count_across_benchmarks_wip(
    df: pd.DataFrame, dynamic_count: bool = True
):
    """df: DataFrame containing the instruction count across models
    This is currently not working as the bars are not stacked"""
    col_name = "TraceCountsGen" if dynamic_count else "DumpCountsGen"
    # Removing Benchmarks with no generated instructions and turning the "dicts" into real dicts
    df2 = df[df[col_name] != "{}"]
    df2.loc[:, col_name] = df2[col_name].apply(ast.literal_eval)

    fig = plt.figure()
    ax: matplotlib.axes.Axes = fig.subplots()  # type: ignore

    for i, row in df2.iterrows():
        instr_count: dict[str, int] = row[col_name]
        instructions, counts = zip(*sorted(instr_count.items(), key=lambda x: x[1]))
        ax.barh(y=instructions, width=counts, label=row["Model"])

    ax.legend(loc="upper right")

    plt.show()


def instruction_count_across_benchmarks(df: pd.DataFrame, dynamic_count: bool = True):
    """df: DataFrame containing the instruction count across models"""
    col_name = "TraceCountsGen" if dynamic_count else "DumpCountsGen"
    # Removing Benchmarks with no generated instructions and turning the "dicts" into real dicts
    df2 = df[df[col_name] != "{}"]
    df2.loc[:, col_name] = df2[col_name].apply(ast.literal_eval)

    new_df = pd.DataFrame(df2[col_name].tolist(), index=df2["Model"])
    print(new_df)
    # fig, axes = plt.subplots(nrows=1, ncols=2)

    ax = new_df.T.plot.barh(stacked=True)
    ax.set_ylabel("Instructions")
    plt.show()


def compare_relative_inst_count(df: pd.DataFrame):
    """Plots the relative Instruction count for each benchmark"""
    bench_instr_count = df.loc[df["Total Instructions (rel.)"] != 1.0]
    ax = df.plot.bar(x="Model", y="Total Instructions (rel.)", rot=0)
    plt.show()


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
