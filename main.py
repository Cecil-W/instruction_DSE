"""Script to evaluate the effectiveness of custom instrucitons
"""

import argparse
import ast
import subprocess

import pandas as pd

import config
import plot


def compile_benchmarks(benchmarks: list[str]):
    """Compiles the given benchmarks"""
    subprocess.run(
        [
            "./venv/bin/python",
            "-m",
            "mlonmcu.cli.main",
            "flow",
            "compile",
            *benchmarks,
            "--target",
            "etiss",
            "-c",
            "mlif.toolchain=llvm",
            "-c",
            "mlif.extend_attrs=1",
            "-c",
            "mlif.strip_strings=1",
            "-c",
            "mlif.global_isel=1",
            "--post",
            "config2cols",
            "-c",
            "config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll",
            # "-v",
            "--parallel",
            "-c",
            f"llvm.install_dir={config.LLVM_PATH}",
            "--post",
            "analyse_dump",
            "--post",
            "rename_cols",
            "-c",
            "rename_cols.mapping={'config_mlif.global_isel':'GIsel',"
            "'config_auto_vectorize.custom_unroll':'Unroll'}",
            "--post",
            "filter_cols",
            "-c",
            "filter_cols.keep=Model,ROM code,GIsel,Reason,DumpCountsGen,Total Instructions,Unroll",
            # "-c",
            # "mlif.strip_strings=0",
            "-c",
            "analyse_dump.to_df=1",
            "-c",
            f"etissvp.script={config.ETISS_RUN_HELPER}",
            "--post",
            "compare_rows",
            "-f",
            "auto_vectorize",
            "--config-gen3",
            "auto_vectorize.custom_unroll=1",
            # "--config-gen2",
            # 'etiss.attr="+m"',
            "--config-gen2",
            f"etiss.attr=\"+m,{','.join(config.EXTENSIONS)}\"",
        ],
        check=True,
        cwd=config.MLONMCU_PATH,
    )


def compile_and_filter(benchmarks: list[str]) -> tuple[dict[str, int], list[str]]:
    """
    Compiles the given benchmarks and returns a list with used instructions and their static count
    Also returns a list of benchmarks which use the new instructions
    Return: (used_instructions, effective_benchmarks)"""
    compile_benchmarks(benchmarks)

    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    effective_benchmarks = report.loc[report["DumpCountsGen"] != "{}"]["Model"]
    # TODO make sure this refactoring works

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

    return (used_instructions, effective_benchmarks.to_list())


def instruction_to_extension(instructions: list[str]):
    """Returns the coresponding extensions for each instruction"""
    extensions: list[str] = []
    for i in instructions:
        for ext in config.EXTENSIONS:
            if i.replace(".", "") in ext:
                extensions.append(ext)

    return extensions


def validate_benchmarks(benchmarks: list[str], extensions: list[str]):
    """Calls MLonMCU with the validate feature and returns a list with all passing benchmarks"""
    # running every benchmark with the extensions
    subprocess.run(
        [
            "python3",
            "-m",
            "mlonmcu.cli.main",
            "flow",
            "run",
            *benchmarks,
            "--target",
            "etiss",
            "-c",
            "mlif.toolchain=llvm",
            "-c",
            "mlif.extend_attrs=1",
            "--config-gen",
            "mlif.global_isel=1",
            "--post",
            "config2cols",
            "-c",
            "config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll",
            # "-v",
            "--parallel",
            "-c",
            f"llvm.install_dir={config.LLVM_PATH}",
            "--post",
            "rename_cols",
            "-c",
            "rename_cols.mapping={'config_mlif.global_isel':'GIsel',"
            "'config_auto_vectorize.custom_unroll':'Unroll'}",
            "--post",
            "filter_cols",
            "-c",
            "filter_cols.keep=Model,ROM code,GIsel,Reason,Total"
            "Instructions,Unroll,Validation",
            "-c",
            "mlif.strip_strings=0",
            "-c",
            f"etissvp.script={config.ETISS_RUN_HELPER}",
            "-f",
            "auto_vectorize",
            "--config-gen3",
            "auto_vectorize.custom_unroll=1",
            "--config-gen2",
            f"etiss.attr=\"+m,{','.join(extensions)}\"",
            "-f",
            "validate",
        ],
        check=True,
        cwd=config.MLONMCU_PATH,
    )
    # then, remove failing benchmarks
    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    passing_benchmarks = report.loc[report["Validation"] is True]["Model"]

    return passing_benchmarks.to_list()


def compare_static_counts(
    benchmarks: list[str], extensions: list[str], new_run: bool = True
):
    """
    Runs a list of benchmarks, with and without the extensions,
    and compares the static code size
    """
    # TODO as im only looking at the static code size anyway,
    # this could be combined with the compile flow as it would make no difference
    if new_run:
        subprocess.run(
            [
                "./venv/bin/python",
                "-m",
                "mlonmcu.cli.main",
                "flow",
                "run",
                *benchmarks,
                "--target",
                "etiss",
                "-c",
                "mlif.toolchain=llvm",
                "-c",
                "mlif.extend_attrs=1",
                "--config-gen",
                "mlif.global_isel=1",
                "--post",
                "config2cols",
                "-c",
                "config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll",
                # "-v",
                "--parallel",
                "-c",
                f"llvm.install_dir={config.LLVM_PATH}",
                "--post",
                "analyse_dump",
                "--post",
                "rename_cols",
                "-c",
                "rename_cols.mapping={'config_mlif.global_isel':'GIsel',"
                "'config_auto_vectorize.custom_unroll':'Unroll'}",
                "--post",
                "filter_cols",
                "-c",
                "filter_cols.keep=Model,ROM code,GIsel,"
                "Reason,DumpCountsGen,Total Instructions,Unroll",
                "-c",
                "mlif.strip_strings=0",
                "-c",
                "analyse_dump.to_df=1",
                "-c",
                f"etissvp.script={config.ETISS_RUN_HELPER}",
                "--post",
                "compare_rows",
                "-f",
                "auto_vectorize",
                "--config-gen3",
                "auto_vectorize.custom_unroll=1",
                "--config-gen2",
                'etiss.attr="+m"',
                "--config-gen2",
                f"etiss.attr=\"+m,{','.join(extensions)}\"",
            ],
            check=True,
            cwd=config.MLONMCU_PATH,
        )
    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    return report


def compare_dynamic_counts(
    benchmarks: list[str], extensions: list[str], new_run: bool = True
):
    """
    Runs a list of benchmarks, with and without the extensions,
    It generates an instruction trace, so it takes a while,
    The trace gets filtered for custom instructions
    It also compares the code size
    """
    if new_run:
        subprocess.run(
            [
                "./venv/bin/python",
                "-m",
                "mlonmcu.cli.main",
                "flow",
                "run",
                *benchmarks,
                "--target",
                "etiss",
                "-c",
                "mlif.toolchain=llvm",
                "-c",
                "mlif.extend_attrs=1",
                "--config-gen",
                "mlif.global_isel=1",
                "--post",
                "config2cols",
                "-c",
                "config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll",
                # "-v",
                "--parallel",
                "-c",
                f"llvm.install_dir={config.LLVM_PATH}",
                "--post",
                "rename_cols",
                "-c",
                "rename_cols.mapping={'config_mlif.global_isel':'GIsel',"
                "'config_auto_vectorize.custom_unroll':'Unroll'}",
                "-f",
                "log_instrs",
                "-c",
                "log_instrs.to_file=1",
                "--post",
                "analyse_instructions",
                "-c",
                "analyse_instructions.to_df=1",
                "-c",
                "analyse_instructions.seq_depth=1",
                "-c",
                "analyse_instructions.top=100000",
                "--post",
                "filter_cols",
                "-c",
                "filter_cols.keep=Model,ROM code,GIsel,Reason,"
                "TraceCountsGen,Total Instructions,Unroll",
                "-c",
                "mlif.strip_strings=0",
                "-c",
                "analyse_dump.to_df=1",
                "-c",
                f"etissvp.script={config.ETISS_RUN_HELPER}",
                "--post",
                "compare_rows",
                "-c",
                "compare_rows.to_compare=Total Instructions",
                "-f",
                "auto_vectorize",
                "--config-gen3",
                "auto_vectorize.custom_unroll=1",
                "--config-gen2",
                'etiss.attr="+m"',
                "--config-gen2",
                f"etiss.attr=\"+m,{','.join(extensions)}\"",
            ],
            check=True,
            cwd=config.MLONMCU_PATH,
        )
    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    return report


def old_main():
    """Main entry"""
    benchmarks2 = ["coremark", "dhrystone"]
    benchmarks = ["coremark"]
    used_instructions, effective_benchmarks = compile_and_filter(benchmarks)
    # remove unused benchmarks

    # validate_benchmarks(benchmarks2, EXTENSIONS)

    used_extensions = instruction_to_extension(list(used_instructions.keys()))
    # static_report = compare_static_counts(used_benchmarks, used_extensions)
    dynamic_report = compare_dynamic_counts(effective_benchmarks, used_extensions)
    # dynamic_report = compare_dynamic_counts(benchmarks, EXTENSIONS, False)
    # plot.compare_relative_inst_count(dynamic_report)
    # plot.instruction_count(data=used_instructions)
    plot.instruction_count_across_benchmarks(df=dynamic_report)


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

    if "compile" in args.flow:
        used_instructions, unused_benchmarks = compile_and_filter(benchmarks)


def test_plots():
    """Testing the plots"""
    df = pd.read_csv("/home/cecil/Documents/Cecil/cecil_bench_v1/cecil_other_trace.csv")
    plot.instruction_count_across_benchmarks(df)


if __name__ == "__main__":
    main()
    # test_plots()

    # compile_benchmarks(["coremark"])
