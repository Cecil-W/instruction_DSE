"""ISA DSE Tool to evaluate the effectiveness of custom instrucitons"""

import argparse
import ast
import logging

import pandas as pd

import config
import mlonmcu_commands as cmds
import plot


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


def validate(benchmarks: list[str], extensions: list[str]):
    """filters out failing runs"""
    # then, remove failing benchmarks
    report = cmds.validate_benchmarks(benchmarks, extensions)
    passing_benchmarks = report.loc[report["Validation"] is True]["Model"]

    return passing_benchmarks.to_list()


def main():
    """Main app entry"""
    parser = argparse.ArgumentParser(description="ISA DSE", add_help=True)
    parser.add_argument(
        "flow",
        choices=["compile", "validate", "static_dump", "trace"],
        nargs="+",
        help="Select DSE flow steps that will be performed in succsesion",
    )
    parser.add_argument(
        "-b",
        "--benchmarks",
        choices=config.BENCHMARKS + ["all"],
        nargs="+",
        help="Selected benchmarks",
    )
    parser.add_argument("-p", "--plot", choices=["compare_inst_count"], nargs="+")
    parser.add_argument(
        "-u",
        "--minimum-usage",
        help="Filter out new instructions that are below the minimum relative count",
    )
    parser.add_argument(
        "-r",
        "--minimum-relative-rom-size",
        help="Filter out Benchmarks that don't improve by x%",
        type=float,
    )
    # parser.add_argument(
    #     "-r",
    #     "--runtime-factor",
    #     help="Weigth that influences the importance of runtime when selecting instructions",
    # )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # set the initial benchmarks
    benchmarks = args.benchmarks
    if "all" in benchmarks:
        benchmarks = config.BENCHMARKS
        # TODO add the other benchmarks
    logger.info("Benchmarks: %s", benchmarks)

    if "compile" in args.flow or "runtime" in args.flow:
        compile_report = cmds.compile_benchmarks(benchmarks)

        if args.minimum_relative_rom_size:
            above_threshold: set[str] = set(
                compile_report.loc[
                    (compile_report["ROM code (rel.)"] > args.minimum_relative_rom_size)
                    & (compile_report["DumpCountsGen"] != "{}")
                ]["Model"]
            )

            removed_benchmarks = []
            for b in above_threshold:
                removed_benchmarks.append(b)
                benchmarks.remove(b)
            if removed_benchmarks:
                logger.info(
                    "Discarding Benchmarks that didn't meet rom size threshold: %s",
                    removed_benchmarks,
                )
        used_instructions = count_instructions(compile_report)
        used_extensions = instruction_to_extension(list(used_instructions.keys()))

    if args.minimum_usage:
        # TODO filter out instructions that are barely utilized
        ...

    if "runtime" in args.flow:
        report = cmds.run_analyse_instructions(
            benchmarks=benchmarks,
            extensions=used_extensions,
        )
        if "compare_inst_count" in args.plot:
            plot.instruction_count_across_benchmarks(report, dynamic_count=True)


def test_plots():
    """Testing the plots"""
    df = pd.read_csv("/home/cecil/Documents/Cecil/cecil_bench_v1/cecil_other_trace.csv")
    plot.instruction_count_across_benchmarks(df)


if __name__ == "__main__":
    main()
    # test_plots()

    # compile_benchmarks(["coremark"])
