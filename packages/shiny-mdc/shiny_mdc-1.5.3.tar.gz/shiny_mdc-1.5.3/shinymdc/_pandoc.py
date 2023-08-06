import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

BASE_METADATA = {
    "nameInLink": "true",
    "link-citations": "true",
    "linkReferences": "true",
    "reference-section-title": "References",
    "figPrefix": "Figure",
    "eqnPrefix": "Equation",
    "tblPrefix": "Table",
    "lstPrefix": "List",
    "secPrefix": "Section",
}


def run_pandoc(
    input_path: Path,
    template_path: Path,
    bib_path: Optional[Path] = None,
    metadata_path: Optional[Path] = None,
    default_img_ext: Optional[str] = None,
    natbib: bool = False,
    verbose: bool = False,
    **metadata,
) -> str:
    """Run `pandoc` to convert input markdown to LaTeX.

    Args:
        input_path: Path to input file.
        template_path: Path to template file.
        bib_path: Path to bibliography file.
        metadata_path: Path to metadata file.
        default_img_ext: Default image extension.
        natbib: Whether to use natbib for bibliography.
        verbose: Whether to enable verbose output.
        metadata: Pandoc metadata (each key-value pair will be added using `-M`).

    Returns:
        Generated LaTeX text.

    Raises:
        subprocess.CalledProcessError: If `pandoc` subprocess fails.
    """
    cmd = ["pandoc"]
    cmd.append("--from=markdown")
    cmd.append("--to=latex")
    cmd.append("--filter=pandoc-crossref")
    cmd.append("--citeproc")

    cmd.append("--wrap=none")

    cmd.append(f"--template={template_path}")
    if metadata_path is not None:
        cmd.append(f"--metadata-file={metadata_path}")
    if bib_path is not None:
        cmd.append(f"--bibliography={bib_path}")
        if natbib:
            cmd.append("--natbib")

    if default_img_ext is not None:
        cmd.append(f"--default-image-extension={default_img_ext}")
    if verbose:
        cmd.append("--verbose")

    base_metadata = BASE_METADATA.copy()
    base_metadata.update(metadata)
    for mk, mv in base_metadata.items():
        cmd.append(f"--metadata={mk}={mv}")

    cmd.append(str(input_path))

    if verbose:
        print("+", *cmd, file=sys.stderr)
    else:
        print(f"+ pandoc '{input_path}' -t '{template_path}'", file=sys.stderr)
    pdone = subprocess.run(
        cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=sys.stderr
    )
    output = _fix_tables(_fix_subfigures(pdone.stdout))
    return output


def _fix_tables(latexs):
    """Modify LaTeX text to use regular `table` instead of `longtable`."""

    def _fix(match):
        match_str = match.group(1)

        # Capture caption to move to the end.
        cap_match = re.search(
            r"\\caption(\[.*\])?\{(.*)\}(\\tabularnewline)?", match_str
        )
        cap = ""
        if cap_match:
            cap_match_str, cap = cap_match.group(0), cap_match.group(2)
            match_str = match_str.replace(cap_match_str, "")
            if cap:
                cap = "\\caption{" + cap + "}"

        # Remove everything between '\endfirsthead' and '\endlastfoot'.
        match_str = re.sub(
            r"(\\endfirsthead.*?)?\\endlastfoot", "", match_str, flags=re.DOTALL
        )

        # Replace '\<top/mid/bottom>rule()' with '\<top/mid/bottom>rule'.
        for _rule in ["top", "mid", "bottom"]:
            match_str = re.sub(rf"\\{_rule}rule\(\)", rf"\\{_rule}rule", match_str)

        return (
            "\\begin{table}\n"
            "\\centering\n"
            "\\begin{tabular}"
            f"{match_str.strip()}\n"
            "\\bottomrule\\noalign{}\n"
            "\\end{tabular}\n"
            f"{cap}\n"
            "\\end{table}"
        )

    return re.sub(
        r"\\begin{longtable}(.*?)\\end{longtable}", _fix, latexs, flags=re.DOTALL
    )


def _fix_subfigures(latexs):
    """Modify figures by wrapping sub-figures in an 'adjustbox'."""

    def _fix(match):
        match_str = match.group(1)

        # First extract the subfloats. Each subfloat is on a single line.
        subfloats = re.findall(r"\\subfloat.*\n", match_str)
        # Remove the subfloats from the match string.
        match_str = re.sub(r"\\subfloat.*\n", "", match_str)
        # Clean up the match string.
        match_str = match_str.strip().replace("\n\n", "\n")

        # Add '\quad' between the subfloats.
        subfloats = "\\quad\n".join(subfloats)
        # Wrap the subfloats and the rest of the figure in a 'figure' environment.
        return "\\begin{figure}\n" + subfloats + match_str + "\n\\end{figure}"

    _env = "pandoccrossrefsubfigures"
    return re.sub(
        rf"\\begin{{{_env}}}(.*?)\\end{{{_env}}}", _fix, latexs, flags=re.DOTALL
    )
