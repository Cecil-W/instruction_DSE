# Instruction DSE

Workflow to run and compare benchmarks with different RISC-V extensions


## Requirements

There are a few requirements which need to set up manually.
The path to those must then be set in `config.py`

- Patched LLVM, which supports the generated instructions
- Patched ETISS, which supports the generated instructions
- Path to ETISS' `run_helper.sh`
- MLonMCU