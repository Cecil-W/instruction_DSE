"""ISA DSE Tool to evaluate the effectiveness of custom instrucitons"""

import argparse
import ast
import logging

import pandas as pd

import config
import mlonmcu_commands as cmds
import plot
import table


logger = logging.getLogger("ISA DSE")


def count_instructions(report: pd.DataFrame) -> dict[str, int]:
    """Counts how often instructions have been used across benchmarks"""
    # TODO add more information to the used instructions, e.g. in which benchmark were they used
    used_instructions: dict[str, int] = {}
    for series in report["DumpCountsGen"]:
        d: dict = ast.literal_eval(series)
        # Update the usage count of the instructions
        for instruction, count in d.items():
            if instruction in used_instructions:
                used_instructions[instruction] += count
            else:
                used_instructions[instruction] = count

    return used_instructions


def instruction_to_extension(instructions: list[str]):
    """Returns the coresponding extensions for each instruction"""
    extensions: list[str] = []
    for i in instructions:
        for ext in config.EXTENSIONS:
            if i.replace(".", "") in ext:
                extensions.append(ext)

    return extensions


def main():
    """Main app entry"""
    parser = argparse.ArgumentParser(description="ISA DSE", add_help=True)
    parser.add_argument(
        "steps",
        choices=["compile", "validate", "traces", "none"],
        # nargs="+",
        help="Select DSE steps that will be performed in succsesion",
    )
    parser.add_argument(
        "-b",
        "--benchmarks",
        choices=config.BENCHMARKS + ["all"],
        nargs="+",
        help="Selected benchmarks",
    )
    parser.add_argument(
        "-p",
        "--plot",
        choices=[
            "benchmark_inst_count",
            "combined_inst_count",
            "compare_relative_inst_count",
        ],
        nargs="*",
    )
    parser.add_argument(
        "-r", "--report", help="Path to to the report that should be used for plotting"
    )
    parser.add_argument(  # TODO add
        "-u",
        "--minimum-usage",
        help="Filter out custom instructions that are below a given amount",
    )
    parser.add_argument(
        "-c",
        "--minimum-code-size-improvement",
        help="Filter out Benchmarks that don't improve by "
        "the given percentage after the compile step",
        type=float,
    )
    parser.add_argument(
        "-l",
        "--latex",
        choices=["relative_inst_count"],
        help="Uses the given function to printa latex table",
    )
    # parser.add_argument(
    #     "-r",
    #     "--runtime-factor",
    #     help="Weigth that influences the importance of runtime when selecting instructions",
    # )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if "none" in args.steps:
        if "report" not in vars(args):
            parser.error("To use the plot step, the path to a report must be supplied")
        report = pd.read_csv(args.report)
        benchmarks = []

    # set the initial benchmarks
    benchmarks = args.benchmarks
    if benchmarks and "all" in benchmarks:
        benchmarks = config.BENCHMARKS
        benchmarks.remove("embench")  # removing duplicate
        # same woulb be needed for taclebench
    elif benchmarks and "embench" in benchmarks:
        benchmarks.remove("embench")
        benchmarks.extend(config.EMBENCH)
    logger.info("Benchmarks: %s", benchmarks)

    if "compile" in args.steps or "validate" in args.steps or "traces" in args.steps:
        report, error = cmds.compile_benchmarks(benchmarks)

    # removing failing benchmarks
    if "Reason" in report.columns:
        # collect failing benchmarks
        failing_benchmarks = report.loc[report["Reason"] == "AssertionError @ COMPILE"][
            "Model"
        ]

        logger.info(
            "Discarding Benchmarks that don't compile: %s",
            failing_benchmarks.unique().tolist(),
        )
        if not "none" in args.steps:
            for b in failing_benchmarks.unique():
                benchmarks.remove(b)

        # remove failing benchmarks from df, not sure if i need this anymore
        report.drop(failing_benchmarks.index.unique(), inplace=True)
        if report.empty:
            raise RuntimeError("Every Benchmark failed")

    # remove benchmarks which dont use new instructions
    if "compile" in args.steps or "validate" in args.steps or "traces" in args.steps:
        useless_benchmarks = report.iloc[1::2].loc[report["DumpCountsGen"] == "{}"][
            "Model"
        ]
        for b in useless_benchmarks:
            benchmarks.remove(b)
        logger.info(
            "Removing Benchmarks that don't use the new Instructions: %s",
            useless_benchmarks.tolist(),
        )

        # remove unused extensions
        instruction_count = count_instructions(report)
        used_extensions = instruction_to_extension(list(instruction_count.keys()))

    if args.minimum_code_size_improvement:
        above_threshold = report.loc[
            (report["ROM code (rel.)"] > args.minimum_relative_rom_size)
            & (report["DumpCountsGen"] != "{}")
        ]["Model"].unique()

        for b in above_threshold:
            benchmarks.remove(b)
        if above_threshold:
            logger.info(
                "Discarding Benchmarks that didn't meet relative rom decrease threshold: %s",
                above_threshold.tolist(),
            )

    logger.info("Benchmarks after the compile stage: %s", benchmarks)

    if "validate" in args.steps or "traces" in args.steps:
        validate_report, return_code = cmds.validate_benchmarks(
            benchmarks, used_extensions
        )
        if return_code != 0:
            invalid_benchmarks = validate_report.loc[
                (validate_report["Validation"] == False)  # ignore
                | (validate_report["Validation"].isna())
            ]["Model"].unique()
            # Pylint suggests to use "is" instead of "==" but this causes the wrong behavior
            logger.info(
                "Discarding invalid Benchmarks: %s", invalid_benchmarks.tolist()
            )
            for b in invalid_benchmarks:
                benchmarks.remove(b)
        else:
            logger.info("All benchmarks validated succesfuly!")

    # if args.inst_count:
    #     plot.instruction_count(instruction_usage)

    if "traces" in args.steps:
        report = cmds.run_analyse_instructions(
            benchmarks=benchmarks,
            extensions=used_extensions,
        )

    if args.minimum_usage:
        # logger.info("Minimum usage--------------")
        # TODO filter out instructions that are barely utilized, percentage of total instructions
        ...
        logger.info("Discarded instructions: %s")
        # TODO used_extensions.remove()
    logger.info("Final Instructions")

    if args.plot and "combined_inst_count" in args.plot:
        plot.combined_instruction_count(report)

    if args.plot and "benchmark_inst_count" in args.plot:
        plot.instruction_count_across_benchmarks(report)

    if args.plot and "compare_relative_inst_count" in args.plot:
        plot.compare_relative_inst_count(report)

    if args.latex and "relative_inst_count" in args.latex:
        table.relative_inst_count(report)


def test_plots():
    """Testing the plots"""
    df = pd.read_csv("/home/cecil/Documents/Cecil/cecil_bench_v1/cecil_other_trace.csv")
    plot.instruction_count_across_benchmarks(df)


if __name__ == "__main__":
    main()
    # test_plots()

    # compile_benchmarks(["coremark"])
