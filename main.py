import matplotlib.pyplot as plt
from mlonmcu.context.context import MlonMcuContext
from mlonmcu.session.session import Session
import pandas as pd
import os.path

# figure out how to do something simmilar to config gen
# -> just create another run with a different config

# Config instruction dump; aka get this cli command into python
# --post analyse_dump -c mlif.toolchain=llvm -f log_instrs --post analyse_instructions -c log_instrs.to_file=1
# should be fixed, but the data still does not show in the report.df
# -> the data gets added as a string to the df making it complex to parse, just log to file and read the csv

# Gather instr. data and plot it
# -> bar plot works, not sure if its the right way to represent the data
# -> TODO maybe addapt the postprocess to count every instruction not just major op codes

# TODO Change the way i run the benchmarks
# The goal is to compare multiple instruction sets, so i should configure multiple cpu/arch configs
# e.g. rv32imafdc + ext1, ext2, ext3
# and then plot comparisons between the different extensions
# -> maybe then look at which extensions instructions were most used
# -> then i can repeat those test for different benchmarks/workloads
# to see which benchmarks benefit the most from which instructions

dynamic_CFG = {
    "config2cols.limit": ["etiss.arch", "etiss.cpu_arch", "mlif.optimize"],
    "etiss.arch": "rv32imfdc",
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


def process_dump(row_count: int = 20):
    raw_path = (
        "$MLONMCU_HOME/temp/sessions/latest/runs/latest/dump_counts.csv"
    )
    path = os.path.expandvars(raw_path)
    instruction_counts = pd.read_csv(path)
    instruction_counts.fillna("UNKNOWN", inplace=True)
    # the data is already sorted in descending order
    instruction_counts.sort_values(by=['Count'],inplace=True)
    top_n = instruction_counts.head(n=row_count)

    fig, ax = plt.subplots()
    # plt.subplots_adjust(bottom=0.25)
    ax.bar(x=top_n["Instruction"], height=top_n["Count"])
    ax.tick_params(axis="x", labelrotation=90)

    plt.show()


def process_analyse_inst():
    raw_path = (
        "$MLONMCU_HOME/temp/sessions/latest/runs/latest/analyse_instructions_majors.csv"
    )
    path = os.path.expandvars(raw_path)
    instruction_counts = pd.read_csv(path)

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    ax.bar(x=instruction_counts["Major"], height=instruction_counts["Count"])
    ax.tick_params(axis="x", labelrotation=90)

    plt.show()


def run_embench_crc(session: Session, context: MlonMcuContext, cfg):
    crc_run = session.create_run(features=[], config=cfg)
    crc_run.add_frontend_by_name("embench", context=context)
    crc_run.add_feature_by_name("log_instrs")
    crc_run.add_model_by_name("crc32", context=context)
    # run.add_backend_by_name("tvmaot", context=context)
    crc_run.add_platform_by_name("mlif", context=context)
    crc_run.add_target_by_name("etiss", context=context)
    crc_run.add_postprocesses_by_name(
        ["config2cols", "analyse_dump", "analyse_instructions"] # TODO select static or dynamic instr count depending on config
    )


def run_sine_model(session: Session, context: MlonMcuContext, cfg):
    sine_model = session.create_run(features=[], config=cfg)
    sine_model.add_frontend_by_name("tflite", context=context)
    sine_model.add_feature_by_name("log_instrs")
    sine_model.add_model_by_name("sine_model", context=context)
    sine_model.add_backend_by_name("tvmaot", context=context)
    sine_model.add_platform_by_name("mlif", context=context)
    sine_model.add_target_by_name("etiss", context=context)
    sine_model.add_postprocesses_by_name(
        ["config2cols", "analyse_dump", "analyse_instructions"] # TODO select static or dynamic instr count depending on config
    )

def main():
    # with MlonMcuContext() as context:
        # session = context.create_session()
        # run_sine_model(session, context, static_CFG)

    # session.open()
    # session.process_runs(context=context)
    # session.close()

    process_dump()



if __name__ == "__main__":
    main()
