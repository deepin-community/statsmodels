#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import glob
import logging
import os
import textwrap

import nbconvert
from yapf.yapflib.yapf_api import FormatCode

BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
DO_NOT_EDIT = """
# DO NOT EDIT 
# Autogenerated from the notebook {notebook}. 
# Edit the notebook and then sync the output with this file.
#
# flake8: noqa
# DO NOT EDIT 
"""

logger = logging.getLogger("notebook-exporter")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

parser = argparse.ArgumentParser(
    description="""
Sync notebooks to python by exporting. The exported files are
always written in ../python relative to the notebooks. 
Requires nbconvert and yapf.
"""
)
parser.add_argument(
    "--full-path",
    "-fp",
    type=str,
    default=None,
    help="Full Path to notebook to convert. Converts all "
    "notebooks in FULL_PATH by default. If not "
    "specified, searches for examples in "
    "../examples/notebooks (relative to this file).",
)
parser.add_argument(
    "--notebook",
    "-nb",
    type=str,
    default=None,
    help="Name of a single notebook to export.  If not "
    "provided, all notebooks found are exported. Appends "
    ".ipynb if NOTEBOOK does not end with this "
    "extension.",
)
parser.add_argument(
    "--force",
    "-f",
    action="store_true",
    help="Force conversion if python file in destination "
    "exists and is newer than notebook.",
)


def is_newer(file1, file2, strict=True):
    """
    Determine if file1 has been modified after file2

    Parameters
    ----------
    file1 : str
        File path. May not exist, in which case False is returned.
    file1 : str
        File path. Must exist.
    strict : bool
        Use strict inequality test (>). If False, then returns True for files
        with the same modified time.

    Returns
    -------
    newer : bool
        True if file1 is strictly newer than file 2
    """
    try:
        t1 = os.path.getmtime(file1)
        t2 = os.path.getmtime(file2)
    except FileNotFoundError:
        return False
    if strict:
        return t1 > t2
    return t1 >= t2


def main():
    args = parser.parse_args()
    full_path = args.full_path
    force = args.force
    if full_path is None:
        full_path = os.path.join(BASE_PATH, "..", "examples", "notebooks")
    notebook = args.notebook
    if notebook is None:
        notebooks = glob.glob(os.path.join(full_path, "*.ipynb"))
    else:
        if not notebook.endswith(".ipynb"):
            notebook = notebook + ".ipynb"
        notebook = os.path.abspath(os.path.join(full_path, notebook))
        if not os.path.exists(notebook):
            raise FileNotFoundError("Notebook {0} not found.".format(notebook))
        notebooks = [notebook]
    if not notebooks:
        import warnings

        warnings.warn("No notebooks found", UserWarning)
    for nb in notebooks:
        nb_full_name = os.path.split(nb)[1]
        nb_name = os.path.splitext(nb_full_name)[0]
        py_name = nb_name + ".py"
        # Get base directory to notebook
        out_file = os.path.split(nb)[0]
        # Write to ../python
        out_file = os.path.join(out_file, "..", "python", py_name)
        if is_newer(out_file, nb) and not force:
            logger.info(
                "Skipping {0}, exported version newer than "
                "notebook".format(nb_name)
            )
            continue
        logger.info("Converting {0}".format(nb_name))
        with open(nb, "r", encoding="utf8") as nb_file:
            converter = nbconvert.PythonExporter()
            python = converter.from_file(nb_file)
            code = python[0].split("\n")
            code_out = []
            for i, block in enumerate(code):
                if "get_ipython" in block:
                    continue
                elif block.startswith("# In[ ]:"):
                    continue
                if block.startswith("#"):
                    # Wrap comments from Markdown
                    block = textwrap.fill(block, width=74)
                    block = block.replace("\n", "\n# ")
                code_out.append(block)
            if not code_out[0]:
                code_out = code_out[1:]
            loc = 0
            for i, line in enumerate(code_out):
                if "# coding: utf" in line:
                    loc = i + 1
                    break
            code_out.insert(loc, DO_NOT_EDIT.format(notebook=nb_full_name))
            code_out = "\n".join(code_out)
            code_out, success = FormatCode(code_out, style_config="pep8")
            with open(out_file, "w", encoding="utf8", newline="\n") as of:
                of.write(code_out)


if __name__ == "__main__":
    main()