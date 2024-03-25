import os

# import logging
from pathlib import Path

from seal5.flow import Seal5Flow
from seal5.logging import set_log_level
from seal5.types import PatchStage

import config


def patch():
    # TODO
    """Demo script for Seal5 Python API."""


    # set_log_level(console_level=logging.DEBUG, file_level=logging.DEBUG)
    set_log_level(console_level="DEBUG", file_level="DEBUG")

    EXAMPLES_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
    VERBOSE = False
    # VERBOSE = True
    # FAST = False
    FAST = True
    SKIP_PATTERNS = False
    # SKIP_PATTERNS = True
    INTERACTIVE = False


    seal5_flow = Seal5Flow("/tmp/seal5_llvm_demo", "demo")

    # Optional: clean existing settings/models for fresh run
    seal5_flow.reset(settings=True, interactive=False)
    seal5_flow.clean(temp=True, patches=True, models=True, inputs=True, interactive=INTERACTIVE)

    # Clone LLVM and init seal5 metadata directory
    seal5_flow.initialize(
        clone=True,
        clone_url="https://github.com/llvm/llvm-project.git",
        # clone_ref="llvmorg-17.0.6",
        clone_ref="llvmorg-18.1.0-rc3",
        force=True,
        verbose=VERBOSE,
    )

    # Load CoreDSL inputs
    cdsl_files = [
        # XCOREV
        EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMac.core_desc",
        EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVAlu.core_desc",
        # EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVBitmanip.core_desc",
        # EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVSimd.core_desc",
        # EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMem.core_desc",
        # EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVBranchImmediate.core_desc",
        # RVP (will not work)
        # EXAMPLES_DIR / "cdsl" / "RV32P.core_desc",
        # EXAMPLES_DIR / "cdsl" / "RVP.core_desc",
        # S4E (untested) -> undefined XLEN
        # EXAMPLES_DIR / "cdsl" / "rv_s4e" / "s4e-mac.core_desc",
        # TUMEDA (untested)
        EXAMPLES_DIR / "cdsl" / "rv_tumeda" / "XCoreVNand.core_desc",
        # GENERATED (untested)
        EXAMPLES_DIR / "cdsl" / "rv_gen" / "test.core_desc",
        # OTHERS (untested)
        EXAMPLES_DIR / "cdsl" / "Example.core_desc",
    ]
    seal5_flow.load(cdsl_files, verbose=VERBOSE, overwrite=True)

    # Load test inputs
    test_files = [
        # EXAMPLES_DIR / "tests" / "xcorev" / "cv_abs.test.c",
        EXAMPLES_DIR / "tests" / "cv_nand" / "cv_nand.c",
        EXAMPLES_DIR / "tests" / "cv_nand" / "cv_nand.s",
        EXAMPLES_DIR / "tests" / "cv_nand" / "cv_nand_invalid.s",
        # TODO: support subdirectories to avoid duplicate test names (WARN!)
        # EXAMPLES_DIR / "tests" / "cv_nand" / "*.c",  # TODO: support glob patterns
    ]
    seal5_flow.load(test_files, verbose=VERBOSE, overwrite=True)

    # Load YAML inputs
    cfg_files = [
        # XCOREV
        EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVMac.yml",
        EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVAlu.yml",
        # EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVBitmanip.yml",
        # EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVSimd.yml",
        # EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVMem.yml",
        # EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVBranchImmediate.yml",
        # S4E
        # TUMEDA
        # GENERATED
        # OTHERS
        EXAMPLES_DIR / "cfg" / "llvm.yml",
        EXAMPLES_DIR / "cfg" / "filter.yml",
        EXAMPLES_DIR / "cfg" / "patches.yml",
        EXAMPLES_DIR / "cfg" / "riscv.yml",
        EXAMPLES_DIR / "cfg" / "tests.yml",
        EXAMPLES_DIR / "cfg" / "git.yml",
    ]
    seal5_flow.load(cfg_files, verbose=VERBOSE, overwrite=False)

    # Clone & install Seal5 dependencies
    # 1. CDSL2LLVM (add PHASE_0 patches)
    seal5_flow.setup(force=True, verbose=VERBOSE)

    # Apply initial patches
    seal5_flow.patch(verbose=VERBOSE, stages=[PatchStage.PHASE_0])

    if not FAST:
        # Build initial LLVM
        seal5_flow.build(verbose=VERBOSE, config="release")

    # Transform inputs
    #   1. Create M2-ISA-R metamodel
    #   2. Convert to Seal5 metamodel (including aliases, builtins,...)
    #   3. Analyse/optimize instructions
    seal5_flow.transform(verbose=VERBOSE)

    # Generate patches (except Patterns)
    seal5_flow.generate(verbose=VERBOSE, skip=["pattern_gen"])

    # Apply next patches
    seal5_flow.patch(verbose=VERBOSE, stages=[PatchStage.PHASE_1, PatchStage.PHASE_2])

    if not FAST:
        # Build patched LLVM
        seal5_flow.build(verbose=VERBOSE, config="release")
    if not SKIP_PATTERNS:
        # Build PatternGen & llc
        seal5_flow.build(verbose=VERBOSE, config="release", target="pattern-gen")
        seal5_flow.build(verbose=VERBOSE, config="release", target="llc")

        # Generate remaining patches
        seal5_flow.generate(verbose=VERBOSE, only=["pattern_gen"])

        # Apply patches
        seal5_flow.patch(verbose=VERBOSE)

    # Build patched LLVM
    seal5_flow.build(verbose=VERBOSE, config="release")

    # Test patched LLVM
    seal5_flow.test(verbose=VERBOSE, ignore_error=True)

    # Deploy patched LLVM (combine commits and create tag)
    seal5_flow.deploy(verbose=VERBOSE)

    # Export patches, logs, reports
    seal5_flow.export("/tmp/seal5_llvm_demo.tar.gz", verbose=VERBOSE)

    # Optional: cleanup temorary files, build dirs,...
    # seal5.clean(temp=True, build=True, deps=True, interactive=INTERACTIVE)
