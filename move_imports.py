import argparse
import ast
import logging
import re
import sys
from itertools import chain, dropwhile
from pathlib import Path
from textwrap import dedent

logging.basicConfig(stream=sys.stderr, format="%(levelname)s - %(message)s")

SKIP_MARK_PATTERN = re.compile(r"#\s+?(noqa|avoid circular import)")


def is_import(node, top=None):
    """
    check if node is an import statement.
    if top is given (as boolean), filter by top level not stop level
    """

    result = isinstance(node, (ast.Import, ast.ImportFrom))
    if top is not None:
        result = result and bool(node.col_offset) is not top
    return result


def refactor(mod: Path) -> str:
    """
    given a path to a module, traverse the code and move all non-top
    import statements to the header.
    """
    original_source = mod.read_text()
    source_lines = original_source.split("\n")
    root = ast.parse(original_source)
    list_of_nodes = list(ast.walk(root))

    def has_skip_mark(node):
        start = get_comment_above(node)
        end = node.lineno
        fragment = "\n".join(source_lines[start:end])
        return bool(re.findall(SKIP_MARK_PATTERN, fragment))

    def get_comment_above(node):
        start = node.lineno - 2
        while start:
            # check if line is a comment
            if not source_lines[start].strip().startswith("#"):
                break
            start -= 1
        return start

    def get_source_segment(node):
        """given a node, return it's  line number range (0-indexed)"""
        if node:
            try:
                next_node = list_of_nodes[list_of_nodes.index(node) + 1]
            except IndexError:
                next_node = list_of_nodes[-1]

            end = get_comment_above(next_node)
            return node.lineno - 1, end
        # block not found
        return (0, 0)

    def find_head_block():
        """
        find the line number ranges of all imports statements
        at the top of the module
        """
        first_import = None
        last_import = None
        for node in list_of_nodes:
            if last_import and not is_import(node, True):
                break
            elif not first_import and is_import(node, True):
                first_import = node
            elif is_import(node, True):
                last_import = node

        start, _ = get_source_segment(first_import)
        _, end = get_source_segment(last_import)
        logging.debug(f"head block of imports between ({start}, {end})")
        return start, end

    head_start, head_end = find_head_block()

    to_move = []
    for node in list_of_nodes:
        if is_import(node, top=False) and not has_skip_mark(node):
            to_move.append(get_source_segment(node))

    if to_move:
        logging.debug(f"blocks to move: {to_move}")
    else:
        logging.info("nothing to move")

    # get new imports to put at head_end
    imports = []
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
        "--start-from-last", action="store_true", help="Incremental refactor"
    )
    parser.add_argument(
        "--limit-to", type=int, default=0, help="Stop processing after N files. Use with --start-from-last",
    )
    parser.add_argument("--debug", action="store_true", help="Make verbose output")
    parser.add_argument("--rewrite", action="store_true", help="write the result to source's path")
    parser.add_argument("--isort", action="store_true", help="apply isort")

    args = parser.parse_args(argv)
    logging.root.setLevel(logging.DEBUG if args.debug else logging.INFO)

    all_files = chain.from_iterable(
        Path('.').glob(p) if not p.startswith("/") else [Path(p)] for p in args.src_path
    )
    last_processed = None
    if args.start_from_last:
        p = Path(".move-import")
        if p.exists():
            last_processed = p.read_text().strip()
            logging.debug(f"found last_processed: {last_processed}")
            # discard until the last processed
            all_files = dropwhile(lambda x: str(x) != last_processed, all_files)
            next(all_files) # discard last_processed itself

    new_sources = []
    for i, mod in enumerate(all_files):
        if args.limit_to and i == args.limit_to:
            break
        last_processed = mod
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
        if last_processed and args.start_from_last:
            p = Path(".move-import")
            p.write_text(str(mod))

    return new_sources if not print_source else ""

if __name__ == "__main__":
    main()
