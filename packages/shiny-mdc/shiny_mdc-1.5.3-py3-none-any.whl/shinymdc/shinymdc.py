import os
import shutil
import sys
from argparse import ArgumentParser
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from typing import Annotated, Literal

import yaml
from corgy import Corgy, corgychecker, CorgyHelpFormatter, corgyparser, NotRequired
from corgy.types import KeyValuePairs

from ._latexmk import run_latexmk
from ._liquid import run_liquidjs
from ._pandoc import run_pandoc
from ._templates import BuiltinTemplate, Template
from ._version import __version__ as corgy_version


class ShinyMDC(Corgy, corgy_required_by_default=True):
    Flag = Literal[True]

    clean: NotRequired[Annotated[Flag, "do a clean build", ["-c", "--clean"]]]
    verbose: NotRequired[Annotated[Flag, "enable verbose output", ["-v", "--verbose"]]]
    quiet: NotRequired[Annotated[Flag, "suppress all output", ["-q", "--quiet"]]]

    input_path: NotRequired[
        Annotated[
            Path,
            "input markdown file (will read from standard input if not specified)",
            ["-i", "--input"],
        ]
    ]
    output_path: NotRequired[
        Annotated[
            Path,
            "output file (will write to standard output if not specified)",
            ["-o", "--output"],
        ]
    ]

    template: Annotated[
        Template,
        f"LaTeX template (path to custom template file, or name of a builtin "
        f"template: {'/'.join(BuiltinTemplate.BUILTIN_TEMPLATE_NAMES)})",
        ["-t", "--template"],
    ] = BuiltinTemplate("basic")

    meta: NotRequired[
        Annotated[
            KeyValuePairs,
            "extra metadata to update the document metadata with",
            ["-m", "--meta"],
        ]
    ]
    default_img_ext: Annotated[
        str, "default image extension", ["-x", "--default-img-ext"]
    ] = "pdf"
    natbib: Annotated[bool, "whether to use 'natbib' for bibliography"] = True

    build_dir: Annotated[
        Path,
        "directory for storing intermediate files and dependencies",
        ["-d", "--build-dir"],
    ] = Path(".shinymdc")
    tex_files_dir: NotRequired[
        Annotated[
            Path,
            "store main tex files in this directory instead of '<build-dir>/main'",
            ["-D", "--tex-files-dir"],
        ]
    ]
    main_tex_path: NotRequired[
        Annotated[
            Path, "write main tex to this file instead of '<tex-files-dir>/main.tex'",
        ]
    ]
    copy_statics: NotRequired[
        Annotated[Flag, "copy static resources to the tex files directory"]
    ]

    @corgychecker("input_path")
    @staticmethod
    def _check_is_readable_file(path: Path) -> Path:
        if not path.exists():
            raise ValueError(f"no such file: '{path}'")
        if not path.is_file():
            raise ValueError(f"not a file: '{path}'")
        if not os.access(path, os.R_OK):
            raise ValueError(f"file not readable: '{path}'")
        return path

    @corgychecker("output_path", "main_tex_path")
    @staticmethod
    def _check_is_writable_file(path: Path) -> Path:
        if path.exists():
            if not path.is_file():
                raise ValueError(f"not a file: '{path}'")
            if not os.access(path, os.W_OK):
                raise ValueError(f"file not writable: '{path}'")
        else:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            except OSError as e:
                raise ValueError(f"failed to create file: '{path}': {e}") from None
        return path

    @corgychecker("build_dir", "tex_files_dir")
    @staticmethod
    def _check_is_writable_dir(path: Path) -> Path:
        if path.exists():
            if not path.is_dir():
                raise ValueError(f"not a directory: '{path}'")
            if not os.access(path, os.W_OK):
                raise ValueError(f"directory not writable: '{path}'")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ValueError(f"failed to create directory: '{path}': {e}") from None
        return path

    @corgyparser("template", metavar="name|path")
    @staticmethod
    def _parse_template(arg: str) -> Template:
        return Template.make(arg)

    @corgyparser("input_path", metavar="file")
    @staticmethod
    def _parse_ifpath(arg: str) -> Path:
        return ShinyMDC._check_is_readable_file(Path(arg))

    @corgyparser("output_path", "main_tex_path", metavar="file")
    @staticmethod
    def _parse_ofpath(arg: str) -> Path:
        return ShinyMDC._check_is_writable_file(Path(arg))

    @corgyparser("build_dir", "tex_files_dir", metavar="dir")
    @staticmethod
    def _parse_odpath(arg: str) -> Path:
        return ShinyMDC._check_is_writable_dir(Path(arg))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "tex_files_dir"):
            self.tex_files_dir = self.build_dir / "main"
            self.tex_files_dir.mkdir(exist_ok=True)
        if not hasattr(self, "main_tex_path"):
            self.main_tex_path = self.tex_files_dir / "main.tex"
            self.main_tex_path.touch()
        if not hasattr(self, "meta"):
            self.meta = KeyValuePairs("")

    def __call__(self) -> int:
        # Wrap the actual call with stdout/stderr redirections.
        # If 'output_path' is not specified, output has to be written to stdout.
        # So, redirect stdout to stderr to prevent subprocesses from writing
        # to stdout. The redirect is done unconditionaly to be consistent.
        # If 'quiet', redirect stderr to a temp file, so that the output can be
        # printed if there is an error.
        true_stdout = sys.stdout
        true_stderr = sys.stderr
        with ExitStack() as stack:
            if hasattr(self, "quiet"):
                # Redirect stderr and stdout to a temp file.
                temp_file = stack.enter_context(NamedTemporaryFile("r+"))
                stack.enter_context(redirect_stderr(temp_file))
                stack.enter_context(redirect_stdout(temp_file))
            else:
                # Redirect stdout to stderr.
                temp_file = None
                stack.enter_context(redirect_stdout(sys.stderr))

            try:
                self._call(true_stdout)
            except ValueError as e:
                print(f"ERROR: {e}", file=true_stderr)
                ret = 1
            except OSError as e:
                print(f"ERROR: {e.filename + ': ' or ''}{e.strerror}", file=true_stderr)
                ret = e.errno
            except CalledProcessError as e:
                ret = e.returncode
                print(f"ERROR: command failed (code {ret}):", *e.cmd, file=true_stderr)
            except KeyboardInterrupt:
                return -1
            else:
                ret = 0

            if ret != 0 and temp_file is not None:
                # Print stderr output from temp file.
                temp_file.seek(0)
                print(temp_file.read(), file=true_stderr)
        return ret

    def _call(self, stdout) -> None:
        ## 0. Clean up.
        if hasattr(self, "clean"):
            for _f in self.tex_files_dir.glob("*.tex"):
                if _f.is_file():
                    print(f"+ rm '{_f}'", file=sys.stderr)
                    _f.unlink()
            _rescs_dir = self.tex_files_dir / "resources"
            if _rescs_dir.is_dir():
                print(f"+ rm -rf '{_rescs_dir}'", file=sys.stderr)
                shutil.rmtree(_rescs_dir, ignore_errors=True)

        ## 1. Load input and parse metadata.

        # Read input from the input file or stdin.
        if hasattr(self, "input_path"):
            print(f"+ read '{self.input_path}'", file=sys.stderr)
            input_data = self.input_path.read_text()
        else:
            print("+ read stdin", file=sys.stderr)
            input_data = sys.stdin.read()

        # Extract header from input data.
        input_lines = input_data.splitlines()
        input_lines_iter = iter(input_lines)
        header = ""
        if next(input_lines_iter) == "---":
            try:
                while (line := next(input_lines_iter)) != "---":
                    header += line + "\n"
            except StopIteration:
                raise ValueError("header end not found") from None
        else:
            input_lines_iter = iter(input_lines)

        # Rest of the input data is the main body.
        body_md = "\n".join(input_lines_iter).strip()

        # Parse metadata from header.
        metadata = yaml.safe_load(header)
        if metadata is None:
            metadata = {}
        try:
            bib_path = Path(metadata["bibliography"])
        except KeyError:
            bib_path = None

        # Link authors to institutes using institute IDs. This is for templates
        # which don't use superscripts for author affiliations.
        # Institutes are specified as a list of dicts with keys 'id' and 'name'.
        # Author affiliations are specified as a list of institute IDs.
        institutes = metadata.get("institute", [])
        inst_id_to_name = {_inst["id"]: _inst["name"] for _inst in institutes}
        authors = metadata.get("author", [])
        for author in authors:
            author["institute"] = []
            for inst_id in author.get("affiliation", []):
                try:
                    author["institute"].append(inst_id_to_name[inst_id])
                except KeyError:
                    raise ValueError(
                        f"unknown institute id '{inst_id}' in author '{author['name']}'"
                    ) from None
        metadata["authors"] = authors

        # Set 'skipequal' to True if no authors have equal contribution.
        if metadata.get("skipequal", False) is False:
            metadata["skipequal"] = (
                sum(int(author.get("equalcontrib", False)) for author in authors) < 2
            )

        # Get the longest author name, email, and institute name.
        # This can be used by templates to align the author list.
        metadata["longest_author_name"] = (
            max((_a.get("name", "") for _a in authors), key=len) if authors else 0
        )
        metadata["longest_email"] = (
            max((_a.get("email", "") for _a in authors), key=len) if authors else 0
        )
        metadata["longest_inst_name"] = (
            max((_i.get("name", "") for _i in institutes), key=len) if institutes else 0
        )

        ############################################################

        ## 2. Prepare input for first stage processing.

        # Create combined input for first stage processing.
        # This input combines the body, abstract, includes, and appendices.
        # The pieces are separated by a non-printing unicode character, so they can
        # be split apart later.
        primary_sep = "\n\n\ufdd0\n\n"
        secondary_sep = "\n\n\ufdd1\n\n"

        combined_md = body_md + primary_sep
        combined_md += metadata.get("abstract", "") + primary_sep

        def _read_files_and_add_to_combined(pstrs: list[str]):
            nonlocal combined_md
            for _i, _pstr in enumerate(pstrs):
                # Separate each piece by a non-printing character.
                if _i != 0:
                    combined_md += secondary_sep
                print(f"+ read '{_pstr}'", file=sys.stderr)
                combined_md += Path(_pstr).read_text()
            combined_md += primary_sep

        for _kind in ["sections", "includes", "appendices"]:
            _read_files_and_add_to_combined(metadata.get(_kind, []))

        # Save combined markdown to a file.
        combined_md_path = Path(self.build_dir / "combined.md")
        print(f"+ write '{combined_md_path}'", file=sys.stderr)
        combined_md_path.write_text(combined_md)

        ############################################################

        ## 3. Generate raw latex for input.

        # Process combined markdown with liquidjs.
        combined_liquified_md_path = self.build_dir / "combined.liquified.md"
        run_liquidjs(
            combined_md_path, combined_liquified_md_path, self.build_dir, **self.meta
        )

        # Process liquidjs output with pandoc.
        with NamedTemporaryFile(suffix=".tex") as stub_template_file:
            stub_template_path = Path(stub_template_file.name)
            stub_template_path.write_text("$body$")
            combined_tex = run_pandoc(
                combined_liquified_md_path,
                stub_template_path,
                bib_path,
                None,  # metadata_path
                self.default_img_ext,
                self.natbib,
                hasattr(self, "verbose"),
                **self.meta,
            )

        # Split compiled latex into constituent parts.
        parts = combined_tex.split(primary_sep.strip())
        body_tex = parts[0].strip()
        abstract_tex = parts[1].strip()
        sections_tex = parts[2].split(secondary_sep.strip())
        includes_tex = parts[3].split(secondary_sep.strip())
        appendices_tex = parts[4].split(secondary_sep.strip())

        ############################################################

        ## 4. Link raw latex parts into metadata dictionary for final processing.

        # The different parts are written to files, and 'include' statements linking
        # to them are added to the metadata dictionary. This is to prevent pandoc
        # from reprocessing them.

        _input_template = r"\input{%s}"

        # Save body.
        if body_tex:
            body_tex_path = self.tex_files_dir / "body.tex"
            print(f"+ write '{body_tex_path}'", file=sys.stderr)
            body_tex_path.write_text(body_tex)
            metadata["body"] = _input_template % body_tex_path.with_suffix("")

        # Save abstract.
        if abstract_tex:
            abstract_tex_path = self.tex_files_dir / "abstract.tex"
            print(f"+ write '{abstract_tex_path}'", file=sys.stderr)
            abstract_tex_path.write_text(abstract_tex)
            metadata["abstract"] = _input_template % abstract_tex_path.with_suffix("")

        def _write_tex_and_get_pstrs(texs, metadata_key, otype):
            new_pstrs = []
            for _tex, _old_pstr in zip(texs, metadata.get(metadata_key, [])):
                _tex = _tex.strip()
                if not _tex:
                    continue
                old_fname = Path(_old_pstr).stem
                new_tex_path = self.tex_files_dir / f"{otype}_{old_fname}.tex"
                print(f"+ write '{new_tex_path}'", file=sys.stderr)
                new_tex_path.write_text(_tex)
                new_pstrs.append(str(new_tex_path.with_suffix("")))
            return new_pstrs

        section_tex_pstrs = _write_tex_and_get_pstrs(
            sections_tex, "sections", "section"
        )
        include_tex_pstrs = _write_tex_and_get_pstrs(
            includes_tex, "includes", "include"
        )
        appendix_tex_pstrs = _write_tex_and_get_pstrs(
            appendices_tex, "appendices", "appendix"
        )

        for _kind, _pstrs in zip(
            ["sections", "includes", "appendices"],
            [section_tex_pstrs, include_tex_pstrs, appendix_tex_pstrs],
        ):
            metadata[_kind] = [_input_template % _pstr for _pstr in _pstrs]

        # Write metadata to file.
        metadata_path = self.build_dir / "metadata.yaml"
        print(f"+ write '{metadata_path}'", file=sys.stderr)
        metadata_path.write_text(yaml.dump(metadata))

        ############################################################

        ## 5. Combine raw latex parts with user template.

        # Now, all the necessary parts are linked through the metadata.
        # So we can pass a dummy empty file to pandoc with the user template.
        rescs_dir = self.tex_files_dir / "resources"
        rescs_dir.mkdir(exist_ok=True)
        with self.template.load() as (
            template_path,
            static_resc_paths,
            dynamic_resc_paths,
        ):
            # Add static resources to metadata.
            for resc_name, resc_path in static_resc_paths.items():
                if hasattr(self, "copy_statics"):
                    # Copy the resource to the tex files dir if it is not already there.
                    copy_resc_path = rescs_dir / f"{resc_name}{resc_path.suffix}"
                    if not copy_resc_path.exists():
                        print(f"+ cp '{resc_path}' '{copy_resc_path}'", file=sys.stderr)
                        shutil.copy(resc_path, copy_resc_path)
                    resc_path = copy_resc_path
                metadata[resc_name] = str(resc_path.with_suffix(""))

            # Process dynamic resources with pandoc.
            for resc_name, resc_path in dynamic_resc_paths.items():
                processed_resc_tex = run_pandoc(
                    Path(os.devnull),
                    resc_path,
                    bib_path,
                    metadata_path,
                    self.default_img_ext,
                    self.natbib,
                    hasattr(self, "verbose"),
                    **self.meta,
                )
                processed_resc_path = rescs_dir / f"{resc_name}{resc_path.suffix}"
                print(f"+ write '{processed_resc_path}'", file=sys.stderr)
                processed_resc_path.write_text(processed_resc_tex)
                metadata[resc_name] = str(processed_resc_path.with_suffix(""))

            # Write updated metadata to file.
            print(f"+ write '{metadata_path}'", file=sys.stderr)
            metadata_path.write_text(yaml.dump(metadata))

            # Process main tex with pandoc.
            main_tex = run_pandoc(
                Path(os.devnull),
                template_path,
                bib_path,
                metadata_path,
                self.default_img_ext,
                self.natbib,
                hasattr(self, "verbose"),
                **self.meta,
            )

        # Write main tex to file.
        print(f"+ write '{self.main_tex_path}'", file=sys.stderr)
        self.main_tex_path.write_text(main_tex)

        ############################################################

        ## 6. Generate pdf using latexmk.

        # Compile main tex with latexmk.
        latexmk_build_dir = self.build_dir / "latexmk"
        print(f"+ mkdir -p '{latexmk_build_dir}'", file=sys.stderr)
        latexmk_build_dir.mkdir(exist_ok=True)
        result_path = run_latexmk(
            self.main_tex_path,
            latexmk_build_dir,
            hasattr(self, "clean"),
            hasattr(self, "verbose"),
        )

        # Copy result to output file or write it to stdout.
        if hasattr(self, "output_path"):
            print(f"+ cp '{result_path}' '{self.output_path}'", file=sys.stderr)
            shutil.copy(result_path, self.output_path)
        else:
            print(f"+ cat '{result_path}'", file=sys.stderr)
            stdout.buffer.write(result_path.read_bytes())


def main():
    parser = ArgumentParser(formatter_class=CorgyHelpFormatter)
    parser.add_argument("-V", "--version", action="version", version=corgy_version)
    mdc = ShinyMDC.parse_from_cmdline(parser)
    return mdc()
