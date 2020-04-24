import argparse
import ast
import logging
import subprocess
import sys
from itertools import chain
from pathlib import Path
from tempfile import mkstemp
from textwrap import dedent

logging.basicConfig(stream=sys.stderr, format="%(asctime)s %(levelname)s - %(message)s", level=logging.DEBUG)


def is_import(node):
    return isinstance(node, (ast.Import, ast.ImportFrom))

def refactor(mod: Path) -> str:
    """
    given a path to a module, traverse the code and move all non-top
    import statements to the header.
    """
    original_source = mod.read_text()
    root = ast.parse(original_source)
    list_of_nodes = list(ast.walk(root))

    def get_source_segment(node):
        """given a node, return it's  line number range (0-indexed)"""
        next_node = list_of_nodes[list_of_nodes.index(node) + 1]
        return node.lineno - 1, next_node.lineno - 2

    def find_head_block():
        """find the line number ranges of all imports statements
        at the top of the module"""

        first_import = None
        last_import = None
        for node in list_of_nodes:
            if last_import and not is_import(node):
                break
            elif not first_import and is_import(node):
                first_import = node
            elif is_import(node):
                last_import = node

        start, _ = get_source_segment(first_import)
        _, end = get_source_segment(last_import)
        logging.debug(f"head block of imports between ({start}, {end})")
        return start, end

    head_start, head_end = find_head_block()

    to_move = []
    for node in list_of_nodes:
        if is_import(node) and node.col_offset:
            to_move.append(get_source_segment(node))

    logging.debug(f"blocks to move: {to_move}")

    # get new imports to put at head_end

    imports = []
    source_lines = original_source.split("\n")
    for segment in to_move:
        block = dedent("\n".join(source_lines[segment[0] : segment[1] + 1]))
        imports.append(block)

    imports_to_append = "\n".join(imports)

    to_exclude = list(chain.from_iterable(range(s, e + 1) for s, e in to_move))
    logging.debug(f"lines to exclude: {to_exclude}")

    new_source = [l for i, l in enumerate(source_lines) if i not in to_exclude]

    new_source.insert(head_end, imports_to_append)
    new_head_end = head_end + len(imports)

    return "\n".join(new_source), new_head_end


def main(argv=None, print_source=True):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "src_path", nargs="*", metavar="paths", type=str, help="Path/s to refactor. Glob supported enclosed in quotes",
    )
    parser.add_argument(
        "--limit-to", type=int, default=0, help="Stop processing after N files",
    )
    parser.add_argument("--rewrite", action="store_true", help="write the result to source's path")
    parser.add_argument("--isort", action="store_true", help="apply isort")

    args = parser.parse_args(argv)
    all_files = chain.from_iterable(
        Path('.').glob(p) if not p.startswith("/") else [Path(p)] for p in args.src_path
    )
    new_sources = []
    for i, mod in enumerate(all_files):
        if args.limit_to and i == args.limit_to:
            break
        logging.info(f"processing {mod}")
        new_source, new_head_end = refactor(mod)
        if args.isort:
            from isort import SortImports

            logging.debug("applying isort")
            # apply isort in black compatible mode
            new_source = SortImports(
                file_contents=new_source,
                combine_as_imports=True,
                multi_line_output=3,
                include_trailing_comma=True,
                force_grid_wrap=0,
                use_parentheses=True,
                line_length=120,
            ).output

        if args.rewrite:
            mod.write_text(new_source)
        elif print_source:
            print(new_source)
        else:
            new_sources.append(new_source)

    return new_sources if not print_source else ""

if __name__ == "__main__":
    main()
