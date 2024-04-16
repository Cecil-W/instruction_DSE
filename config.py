"""Paths to the used programms."""

import os.path

MLONMCU_HOME = os.path.expandvars("$MLONMCU_HOME")

LLVM_PATH = "/home/cecil/Documents/llvm-project/build"
ETISS_PATH = "/home/cecil/Documents/etissVK"
ETISS_RUN_HELPER = ETISS_PATH + "/build/installed/bin/run_helper.sh"
MLONMCU_PATH = "/home/cecil/Documents/mlonmcu"

# Currently not needed/used
VENV_NAME = "venv"
M2_ISA_R_PATH = "~/Documents/M2-ISA-R"
SEAL5_PATH = "~/Documents/seal5"

BENCHMARKS = ["coremark", "dhrystone", "embench"]

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
