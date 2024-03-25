import os.path
from copy import deepcopy
import subprocess
import logging


import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
from mlonmcu.context.context import MlonMcuContext
from mlonmcu.session.session import Run


import config
import seal5_script

logger = logging.getLogger("ISA_DSE")


# figure out how to do something simmilar to config gen
# -> just create another run with a different config

# Config instruction dump; aka get this cli command into python
# --post analyse_dump -c mlif.toolchain=llvm -f log_instrs --post analyse_instructions -c log_instrs.to_file=1
# should be fixed, but the data still does not show in the report.df
# -> the data gets added as a string to the df making it complex to parse, just log to file and read the csv

# Gather instr. data and plot it
# -> bar plot works, not sure if its the right way to represent the data
# -> TODO maybe addapt the postprocess to count every instruction not just major op codes

# Change the way i run the benchmarks
# The goal is to compare multiple instruction sets, so i should configure multiple cpu/arch configs
# e.g. rv32imafdc + ext1, ext2, ext3
# and then plot comparisons between the different extensions
# -> maybe then look at which extensions instructions were most used
# -> then i can repeat those test for different benchmarks/workloads
# to see which benchmarks benefit the most from which instructions
#
# This works now for any amounts of runs, showing inst. count and rom code size
# TODO Next step is to show which new instructions were used
# => pop every std instructions and plot the left over instr.

dynamic_CFG = {
    "config2cols.limit": ["etiss.arch", "etiss.cpu_arch", "mlif.optimize"],
    "etiss.arch": "rv32imafdc",
    "etiss.cpu_arch": "RV32IMACFD",
    "mlif.toolchain": "llvm",
    "mlif.optimize": 3,
    "log_instrs.to_file": 1,
    # "analyse_instructions.to_df": 1, # this gets saved as a str in the dataframe,
    # making it mostly useless, parsing it is harder than just reading the csv
    "analyse_instructions.to_file": 1,
}

static_CFG = {
    "config2cols.limit": ["etiss.arch", "etiss.cpu_arch", "mlif.optimize"],
    "etiss.arch": "rv32imfdc",
    "etiss.cpu_arch": "RV32IMACFD",
    "mlif.toolchain": "llvm",
    "mlif.optimize": 3,
    "analyse_dump": 1,
}

POSTPROCESSES_static = ["config2cols", "analyse_dump", "analyse_instructions"]

POSTPROCESSES_dynamic = ["config2cols", "analyse_instructions"]

MLONMCUDir = os.path.expandvars("$MLONMCU_HOME")
MLONMCULatestSession = MLONMCUDir + "/temp/sessions/latest/"
MLONMCULatestRun = MLONMCULatestSession + "runs/latest/"


def plot_dump(row_count: int = 20):
    path = MLONMCULatestRun + "dump_counts.csv"
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


def plot_analyse_inst():
    path = MLONMCULatestRun + "analyse_instructions_majors.csv"
    instruction_counts = pd.read_csv(path)

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    ax.bar(x=instruction_counts["Major"], height=instruction_counts["Count"])
    ax.tick_params(axis="x", labelrotation=90)

    plt.show()


def plot_compare_runs(report: pd.DataFrame):
    # TODO Pick back up here, familiarize with df's and select each run
    # This should be the same as in one of the mlonmcu examples
    columns = ["ROM code", "Total Instructions"]

    # collumns to plot: ROM code & Total Instructions
    fig, axs = plt.subplots(1, len(columns))
    axs: list[matplotlib.axes.Axes]
    for i, col in enumerate(columns):
        # axs[i].bar(x=report["config_etiss.arch"].astype(str), height=report[col])
        report.plot(x="config_etiss.arch", y=col, kind="bar", ax=axs[i])

    plt.show()


def run_embench_crc(run: Run, context: MlonMcuContext):
    run.add_frontend_by_name("embench", context=context)
    run.add_feature_by_name("log_instrs")
    run.add_model_by_name("crc32", context=context)
    run.add_platform_by_name("mlif", context=context)
    run.add_target_by_name("etiss", context=context)
    run.add_postprocesses_by_name(
        [
            "config2cols",
            "analyse_dump",
            # "analyse_instructions",
        ]  # TODO select static or dynamic instr count depending on config
    )


def run_sine_model(run: Run, context: MlonMcuContext):
    run.add_frontend_by_name("tflite", context=context)
    run.add_feature_by_name("log_instrs")
    run.add_model_by_name("sine_model", context=context)
    run.add_backend_by_name("tvmaot", context=context)
    run.add_platform_by_name("mlif", context=context)
    run.add_target_by_name("etiss", context=context)
    run.add_postprocesses_by_name(
        [
            "config2cols",
            "analyse_dump",
            "analyse_instructions",
        ]  # TODO select static or dynamic instr count depending on config
    )


def config_etiss_arch(arch: str, cpu_arch: str, config: dict):
    """Copies a config and sets the etiss arch to the specified arch strings"""
    cfg = deepcopy(config)
    cfg["etiss.arch"] = arch
    cfg["etiss.cpu_arch"] = cpu_arch
    return cfg


def run_mlonmcu():
    with MlonMcuContext() as context:
        session = context.create_session()
        cfg_imafdc = config_etiss_arch("rv32imafdc", "RV32IMACFD", static_CFG)
        crc_run1 = session.create_run(features=[], config=cfg_imafdc)
        run_embench_crc(crc_run1, context)

        cfg_imafd = config_etiss_arch("rv32imafd", "RV32IMACFD", static_CFG)
        crc_run2 = session.create_run(features=[], config=cfg_imafd)
        run_embench_crc(crc_run2, context)

    session.open()
    session.process_runs(context=context)
    report = session.get_reports().df
    session.close()

    print(report)
    print(report[["Run"]])
    print(type(report[["Run"]].astype(int)))
    # plot_dump()
    plot_compare_runs(report)


def generate_m2isar_model(filepath: str):
    subprocess.run(
        [
            f"./{config.VENV_NAME}/bin/python",
            "-m",
            "m2isar.frontends.gen_custom_insns",
            filepath,
            "-c",
        ],  # TODO adapt CLI options for seal5
        cwd=config.M2_ISA_R_PATH,
        check=True,
    )


def generate_cdsl_files(filepath: str):
    subprocess.run(
        [
            f"./{config.VENV_NAME}/bin/python",
            "-m",
            "m2isar.backends.coredsl2_set.writer",
            filepath,
        ],
        cwd=config.M2_ISA_R_PATH,
        check=True,
    )


def generate_etiss_patch(model_path: str):
    subprocess.run(
        [
            f"./{config.VENV_NAME}/bin/python",
            "-m",
            "m2isar.backends.etiss.writer",
            model_path,
            "--separate",
            "--static-scalars",
        ],
        cwd=config.M2_ISA_R_PATH,
        check=True,
    )


def patch_etiss(model_path: str):
    # TODO create a folder in this dir to copy files around, or use TMP
    # TODO cwd depends on where i want to save the tmp files
    subprocess.run(
        [
            "cp",
            "-r",
            model_path + "/gen_output/top/*",
            config.ETISS_PATH + "/ArchImpl/",
        ],
        cwd="TODO",
        check=True,
    )

    subprocess.run(
        ["git", "restore", "ArchImpl/RV32IMACFD/RV32IMACFDArchSpecificImp.cpp"],
        cwd=config.ETISS_PATH,
        check=True,
    )
    subprocess.run(
        ["git", "restore", "ArchImpl/RV64IMACFD/RV64IMACFDArchSpecificImp.cpp"],
        cwd=config.ETISS_PATH,
        check=True,
    )
    # TODO figure out if mlonmcu rebuilds etiss, or if i need to do it here
    subprocess.run(
        ["make", "-C", "build", "-j$(nproc)", "install"],
        cwd=config.ETISS_PATH,
        check=True,
    )


def patch_llvm():
    seal5_script.patch()


def main():
    generate_m2isar_model("TODO")
    generate_cdsl_files("TODO")
    generate_etiss_patch("TODO")
    patch_etiss("TODO")
    patch_llvm()
    run_mlonmcu()


if __name__ == "__main__":
    run_mlonmcu()
