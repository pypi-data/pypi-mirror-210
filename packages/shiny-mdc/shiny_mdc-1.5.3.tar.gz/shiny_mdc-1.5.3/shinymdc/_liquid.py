import json
import subprocess
import sys
from pathlib import Path

# Template node.js script to read a file, process with liquidjs,
# and write the output to a file.
_NODE_TEMPLATE = """
const fs = require("fs");
var {{ Liquid }} = require({liquidjs_path});
var liquid = new Liquid({{
    jekyllinclude: true,
    dynamicPartials: false,
}});
metadata = {metadata};
data = fs.readFileSync({input_path}, "utf8");
data = liquid.parseAndRenderSync(data, metadata);
fs.writeFileSync({output_path}, data, "utf8");
"""

# Arguments to pass to `npm install` when installing liquidjs.
_NPM_INSTALL_ARGS = ("--no-save", "--no-fund", "--no-audit")


def run_liquidjs(input_path: Path, output_path: Path, install_dir: Path, **metadata):
    """Process a file using LiquidJS.

    Args:
        input_path: Path to input file.
        output_path: Path to output file.
        install_dir: Directory for installing LiquidJS (`node_modules` folder will be
            created here).
        metadata: Metadata to pass to LiquidJS.

    Raises:
        subprocess.CalledProcessError: If any subprocess fails.
    """
    liquidjs_path = (install_dir / "node_modules" / "liquidjs").absolute()
    if not liquidjs_path.exists():
        install_cmd = ["npm", "install", *_NPM_INSTALL_ARGS, "liquidjs"]
        print("+", *install_cmd, file=sys.stderr)
        subprocess.run(install_cmd, check=True, cwd=install_dir)

    node_script = _NODE_TEMPLATE.format(
        liquidjs_path=json.dumps(str(liquidjs_path)),
        metadata=json.dumps(metadata),
        input_path=json.dumps(str(input_path)),
        output_path=json.dumps(str(output_path)),
    )

    print("+ node <LIQUIDJS_TEMPLATE>", file=sys.stderr)
    subprocess.run(
        ["node", "-"],
        check=True,
        text=True,
        input=node_script,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
