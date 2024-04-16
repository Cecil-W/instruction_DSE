"""ISA DSE Tool to evaluate the effectiveness of custom instrucitons"""

import argparse
import ast
import logging

import pandas as pd

import config
import mlonmcu_commands as cmds
import plot


logger = logging.getLogger("ISA-DSE ")


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
        choices=["compile", "validate", "runtime"],
        nargs="+",
        help="Select DSE flow steps that will be performed in succsesion",
    )
    parser.add_argument(
        "-b",
        "--benchmarks",
        choices=["coremark", "dhrystone", "embench", "all"],
        nargs="+",
        help="Selected benchmarks",
    )
    parser.add_argument("-p", "--plot", choices=["compare_inst_count"], nargs="+")
    parser.add_argument(
        "-s",
        "--size-factor",
        help="Weigth that influences the importance of "
        "static code size when selecting instructions",
    )
    parser.add_argument(
        "-r",
        "--runtime-factor",
        help="Weigth that influences the importance of runtime when selecting instructions",
    )
    args = parser.parse_args()

    # set the initial benchmarks
    benchmarks = args.benchmarks
    if benchmarks == "all":
        benchmarks = ["coremark", "dhrystone", "embench"]
        # TODO add the other benchmarks
    logger.info("Benchmarks: %s", benchmarks)

    # if "compile" in args.flow or "runtime" in args.flow:
    compile_report = cmds.compile_benchmarks(benchmarks)
    new_benchmarks = compile_report.loc[compile_report["DumpCountsGen"] != "{}"][
        "Model"
    ]
    unused_benchmarks = compile_report.loc[compile_report["DumpCountsGen"] == "{}"][
        "Model"
    ]
    if not unused_benchmarks.empty:
        logger.info("Discarding Benchmarks: %s", unused_benchmarks.tolist())
    used_instructions = count_instructions(compile_report)
    used_extensions = instruction_to_extension(list(used_instructions.keys()))

    if "runtime" in args.flow:
        report = cmds.run_analyse_instructions(
            benchmarks=new_benchmarks.tolist(),
            extensions=used_extensions,
        )


def test_plots():
    """Testing the plots"""
    df = pd.read_csv("/home/cecil/Documents/Cecil/cecil_bench_v1/cecil_other_trace.csv")
    plot.instruction_count_across_benchmarks(df)


if __name__ == "__main__":
    main()
    # test_plots()

    # compile_benchmarks(["coremark"])
