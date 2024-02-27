import matplotlib.pyplot as plt
import subprocess


def plot():
    fig = plt.figure()
    ax = fig.subplots()
    pass


def main():
    subprocess.run(
        [
            "python3",
            "-m",
            "mlonmcu.cli.main",
            "flow",
            "run",
            "sine_model",
            "--target",
            "etiss",
            "--config-gen",
            "etiss.arch=rv32imfdc",
            "etiss.cpu_arch=RV32IMACFD",
            "--config-gen",
            "etiss.arch=rv32imafdc",
            "etiss.cpu_arch=RV32IMACFD",
            "--parallel",
            "--post",
            "config2cols",
            "-c",
            "config2cols.limit=etiss.arch,etiss.cpu_arch,mlif.optimize",
        ],
        check=True,
        cwd="./mlonmcu",
    )


if __name__ == "__main__":
    main()
