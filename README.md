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

Additionally a list of all the available extensions must be set in `EXTENSIONS`

## Usage
` Python main.py {compile,validate,traces,none} `
- compile: Compile the benchmarks and remove unused extensions and benchmarks which don't compile
- validate: Filter out benchmarks which fail to verify with the remaining instructions
- traces: Generate Instruction traces using the validated benchmarks
- none: used in conjunction with `-r PATH` to use the post processes with an existing report
