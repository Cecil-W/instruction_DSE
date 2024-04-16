# Instruction DSE

Workflow to run and compare benchmarks with different RISC-V extensions


## Requirements

There are a few requirements which need to set up manually.
- Patched LLVM, which supports the generated instructions
- Patched ETISS, which supports the generated instructions
- MLonMCU

### Config

These paths need to be set in config.py
- `LLVM_PATH`
- `ETISS_RUN_HELPER`
- `MLONMCU_PAT`

Additionally a list of all the used extensions must be set in `EXTENSIONS`

