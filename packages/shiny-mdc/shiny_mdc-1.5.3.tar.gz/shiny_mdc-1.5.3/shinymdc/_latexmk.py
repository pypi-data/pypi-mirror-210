import subprocess
import sys
from pathlib import Path


def run_latexmk(
    input_path: Path, build_dir: Path, clean: bool = False, verbose: bool = False
) -> Path:
    """Compile a LaTeX file using `latexmk`.

    Args:
        input_path: Path to input file.
        build_dir: Path to build directory.
        clean: Whether to do a clean build by passing `-gg` to `latexmk`.
        verbose: Whether to enable verbose output.

    Returns:
        Path to output file.

    Raises:
        subprocess.CalledProcessError: If `latexmk` subprocess fails.
    """
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-lualatex", "-f"]

    if clean:
        cmd.append("-gg")
    if not verbose:
        cmd.append("-silent")

    cmd.append(f"-output-directory={build_dir}")
    cmd.append(str(input_path))

    print("+", *cmd, file=sys.stderr)
    subprocess.run(
        cmd,
        check=True,
        stdout=sys.stdout if verbose else subprocess.DEVNULL,
        stderr=sys.stderr,
    )
    return build_dir / input_path.with_suffix(".pdf").name
