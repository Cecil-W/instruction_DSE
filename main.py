"""Script to evaluate the effectiveness of
"""

import subprocess
import ast


import pandas as pd


import config

EXTENSIONS = [
    "+xseal5testalucvabs16",
    "+xseal5testalucvabs32",
    "+xseal5testalucvabs8",
    "+xseal5testalucvaddnrsi16",
    "+xseal5testalucvaddnrsi32",
    "+xseal5testalucvaddnrui16",
    "+xseal5testalucvaddnrui32",
    "+xseal5testalucvaddns",
    "+xseal5testalucvaddnu",
    "+xseal5testalucvaddrnrsi16",
    "+xseal5testalucvaddrnrsi32",
    "+xseal5testalucvaddrnrui16",
    "+xseal5testalucvaddrnrui32",
    "+xseal5testalucvaddrns",
    "+xseal5testalucvaddrnu",
    "+xseal5testalucvextbs",
    "+xseal5testalucvextbz",
    "+xseal5testalucvexths",
    "+xseal5testalucvexthz",
    "+xseal5testalucvmaxi1216",
    "+xseal5testalucvmaxi1232",
    "+xseal5testalucvmaxi516",
    "+xseal5testalucvmaxi532",
    "+xseal5testalucvmaxs16",
    "+xseal5testalucvmaxs32",
    "+xseal5testalucvmaxs8",
    "+xseal5testalucvmaxu16",
    "+xseal5testalucvmaxu32",
    "+xseal5testalucvmaxu8",
    "+xseal5testalucvmini1216",
    "+xseal5testalucvmini1232",
    "+xseal5testalucvmini516",
    "+xseal5testalucvmini532",
    "+xseal5testalucvmins16",
    "+xseal5testalucvmins32",
    "+xseal5testalucvmins8",
    "+xseal5testalucvminu16",
    "+xseal5testalucvminu32",
    "+xseal5testalucvminu8",
    "+xseal5testalucvsletsi16",
    "+xseal5testalucvsletsi32",
    "+xseal5testalucvsletui16",
    "+xseal5testalucvsletui32",
    "+xseal5testalucvsubnrsi16",
    "+xseal5testalucvsubnrsi32",
    "+xseal5testalucvsubnrui16",
    "+xseal5testalucvsubnrui32",
    "+xseal5testalucvsubns",
    "+xseal5testalucvsubnu",
    "+xseal5testalucvsubrnrsi16",
    "+xseal5testalucvsubrnrsi32",
    "+xseal5testalucvsubrnrui16",
    "+xseal5testalucvsubrnrui32",
    "+xseal5testalucvsubrns",
    "+xseal5testalucvsubrnu",
    "+xseal5testmaccvmachhns",
    "+xseal5testmaccvmachhnu",
    "+xseal5testmaccvmachhrns",
    "+xseal5testmaccvmachhrnu",
    "+xseal5testmaccvmacns",
    "+xseal5testmaccvmacnu",
    "+xseal5testmaccvmacrns",
    "+xseal5testmaccvmacrnu",
    "+xseal5testmaccvmacsi16",
    "+xseal5testmaccvmacsi32",
    "+xseal5testmaccvmacui16",
    "+xseal5testmaccvmacui32",
    "+xseal5testmaccvmsusi16",
    "+xseal5testmaccvmsusi32",
    "+xseal5testmaccvmsuui16",
    "+xseal5testmaccvmsuui32",
    "+xseal5testmaccvmulhhns",
    "+xseal5testmaccvmulhhnu",
    "+xseal5testmaccvmulhhrns",
    "+xseal5testmaccvmulhhrnu",
    "+xseal5testmaccvmulns",
    "+xseal5testmaccvmulnu",
    "+xseal5testmaccvmulrns",
    "+xseal5testmaccvmulrnu",
    "+grp32v",
]


def compile_benchmarks(benchmarks: list[str]):
    """Compiles the given benchmarks"""
    # TODO look at the commands philipp sent me and update arguments
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
            "--config-gen",
            "mlif.global_isel=1",
            "--post",
            "config2cols",
            "-c",
            "config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll",
            "-v",
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
            f"etiss.attr=\"+m,{','.join(EXTENSIONS)}\"",
        ],
        check=True,
        cwd=config.MLONMCU_PATH,
    )


def remove_unused_extensions(
    benchmarks: list[str], new_run: bool = True
) -> tuple[dict[str, int], list[str]]:
    """
    Compiles the given benchmarks and returns a list with used instructions and their static count
    Also returns a list of benchmarks which don't make use of the new instructions
    Return: (used_instructions, resultless_benchmarks)"""
    if new_run:
        compile_benchmarks(benchmarks)

    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    resultless_benchmarks = report.loc[report["DumpCountsGen"] == "{}"]["Model"]

    used_instructions: dict[str, int] = {}
    for series in report["DumpCountsGen"]:
        d: dict = ast.literal_eval(series)
        # Update the usage count of the instructions
        for instruction, count in d.items():
            if instruction in used_instructions:
                used_instructions[instruction] += count
            else:
                used_instructions[instruction] = count

    return (used_instructions, resultless_benchmarks.to_list())


def instruction_to_extension(instructions: list[str]):
    """Returns the coresponding extensions for each instruction"""
    extensions: list[str] = []
    for i in instructions:
        for ext in EXTENSIONS:
            if i.replace(".", "") in ext:
                extensions.append(ext)

    return extensions


def compare_static_counts(new_run: bool, benchmarks: list[str], extensions: list[str]):
    """
    Runs a list of benchmarks, with and without the extensions,
    and compares the static code size
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
                "-v",
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


def main():
    """Main entry"""
    benchmarks = ["coremark", "dhrystone"]
    used_instructions, useless_benchmarks = remove_unused_extensions(benchmarks, True)
    # remove unused benchmarks
    new_benchmarks = [bench for bench in benchmarks if bench not in useless_benchmarks]

    # compare_static_counts(True, benchmarks, new_extensions)


if __name__ == "__main__":
    main()
