import importlib.resources
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import AbstractContextManager, contextmanager, ExitStack
from importlib.abc import Traversable
from pathlib import Path
from typing import final


class Template(ABC):
    """Base class for LaTeX templates."""

    @abstractmethod
    def load(
        self,
    ) -> AbstractContextManager[tuple[Path, dict[str, Path], dict[str, Path]]]:
        """Load the template, and any associated resources.

        Yields:
            A tuple of (template path, a dictionary mapping static resource names
            to their paths, a dictionary mapping dynamic resource names to paths).
        """

    @staticmethod
    @final
    def make(arg: str) -> "Template":
        """Get a template from a name (`BuiltinTemplate`), or path (`CustomTemplate`).

        Args:
            arg: Name of a builtin template, or path to a custom template.
        """
        if arg in BuiltinTemplate.BUILTIN_TEMPLATE_NAMES:
            return BuiltinTemplate(arg)
        return CustomTemplate(Path(arg))


class BuiltinTemplate(Template):
    _builtin_template_paths: dict[str, Traversable] = {}

    _static_resources = defaultdict(
        list,
        {
            # These are per-template static resources. The '*' key if for resources
            # that are common to all templates.
            "*": ["reqsetup.tex", "floatsetup.tex", "mathsetup.tex", "miscsetup.tex"],
            "basic": ["bibsupersetup.tex"],
            "stylish": ["bibsupersetup.tex"],
            "standalone": ["bibsupersetup.tex"],
            "spacious": ["bibsupersetup.tex"],
            "iccv": [
                "iccv/iccv.sty",
                "iccv/esopic.sty",
                "iccv/everyshi.sty",
                "iccv/bibstyle.bst",
                "bibnonatsetup.tex",
            ],
            "iclr": [
                "iclr/iclr.sty",
                "iclr/bibstyle.bst",
                "iclr/mathcommands.tex",
                "bibnosupersetup.tex",
            ],
            "icml": ["icml/icml.sty", "icml/bibstyle.bst", "bibnosupersetup.tex"],
            "neurips": ["neurips/neurips.sty", "bibnosupersetup.tex"],
        },
    )
    _dynamic_resources = defaultdict(
        list,
        {
            # Dynamic resources, defined similarly to static resources.
            "*": ["addappendices.tex"],
            "basic": ["authsetup.tex"],
            "iccv": ["authsetup.tex", "dblfloatsetup.tex"],
            "iclr": ["authsetup.tex"],
            "icml": ["dblfloatsetup.tex"],
            "neurips": ["authsetup.tex"],
            "spacious": ["authsetupshort.tex"],
            "stylish": ["authsetupshort.tex", "dblfloatsetup.tex"],
        },
    )

    # Get available builtin templates.
    for _template_path in (
        _path
        for _path in (importlib.resources.files(__package__) / "templates").iterdir()
        if _path.name.endswith(".tex")
    ):
        _name = _template_path.name.removesuffix(".tex")
        _builtin_template_paths[_name] = _template_path

    BUILTIN_TEMPLATE_NAMES = list(_builtin_template_paths.keys())

    def __init__(self, name: str):
        if name not in self.BUILTIN_TEMPLATE_NAMES:
            raise ValueError(f"no builtin template named {name!r}")
        self.name = name

    @contextmanager
    def load(self):
        ctx_stk = ExitStack()
        template_path = ctx_stk.enter_context(
            importlib.resources.as_file(self._builtin_template_paths[self.name])
        )

        static_resc_paths = {}
        dynamic_resc_paths = {}

        # Load resources for the template.
        _resources_root = importlib.resources.files(__package__) / "resources"
        for _kind, _kind_src_dict, _kind_target_dict in zip(
            ["static", "dynamic"],
            [self._static_resources, self._dynamic_resources],
            [static_resc_paths, dynamic_resc_paths],
        ):
            for _resc in _kind_src_dict["*"] + _kind_src_dict[self.name]:
                _resc_path = _resources_root / _kind / _resc
                _resc_name = str(_resc_path.with_suffix("").name)
                print(f"+ load resource {_resc_name!r}", file=sys.stderr)
                _kind_target_dict[_resc_name] = ctx_stk.enter_context(
                    importlib.resources.as_file(_resc_path)
                )

        try:
            yield (template_path, static_resc_paths, dynamic_resc_paths)
        finally:
            ctx_stk.pop_all().close()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class CustomTemplate(Template):
    def __init__(self, path: Path):
        if not path.exists():
            raise ValueError(f"custom template does not exist: '{path}'")
        self.path = path

    @contextmanager
    def load(self):
        yield (self.path, {}, {})

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"
