"""MLonMCU commands"""

import subprocess

import pandas as pd

import config


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
            "--config-gen2",
            'etiss.attr="+m"',
            "--config-gen2",
            f"etiss.attr=\"+m,{','.join(config.EXTENSIONS)}\"",
        ],
        check=True,
        cwd=config.MLONMCU_PATH,
    )
    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    return report


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
    report = pd.read_csv(config.MLONMCU_HOME + "/temp/sessions/latest/report.csv")
    return report


def run_benchmarks(benchmarks: list[str], extensions: list[str], new_run: bool = True):
    """
    Runs a list of benchmarks, with and without the extensions,
    Useful to compares the static code size
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


def run_analyse_instructions(
    benchmarks: list[str], extensions: list[str], new_run: bool = True
):
    """
    Runs a list of benchmarks, with and without the extensions,
    It generates an full instruction trace using 'analyse_instructions', so it takes a while,
    The report contains the the counts of each extension instruction
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
