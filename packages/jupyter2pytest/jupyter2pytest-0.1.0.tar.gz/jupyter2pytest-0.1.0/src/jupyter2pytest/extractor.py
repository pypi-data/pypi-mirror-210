from typing import List, Dict
from collections import defaultdict
from re import compile

import nbformat

class TestcellBlock:
    """Class for associating testcases with code blocks.

    Attributes: 
        cases: List of all cases in notebook file (i.e. list of 'things' extracted)
        blocks: Association of cases with code blocks corresponding to them.
    """
    cases: List[str]
    blocks: Dict[str, List[str]]

    def __init__(
            self
        ):
        self.cases = []
        self.blocks = defaultdict(lambda: [])

    def add_codeblock(
            self, 
            testcase: str, 
            code: str
        ):
        """Adds a block of code corresponding to a testcase.

        Args:
            testcase: The testcase that this code belongs to.
            code: The code block to add.
        """
        block = self.blocks[testcase]
        if len(block) == 0:
            self.cases.append(testcase)

        block.append(code)

    def get_code_for_testcase(
            self,
            testcase: str
        ) -> str:
        """Gets all code corresponding to a given testcase.

        Args:
            testcase: The testcase to get code for.

        Returns:
            All blocks of code corresponding to the testcase, joined by newlines.
        """
        if testcase in self.cases:
            return "\n".join(self.blocks[testcase])
        else:
            return ""

def open_notebook(
        path: str    
    ) -> nbformat.NotebookNode:
    """Opens a python notebook at a given path as a NotebookNode object.

    Args:
        path: Path to the ipynb file.

    Returns:
        NotebookNode object representing the notebook.
    """
    with open(path, "r") as nfp:
        notebook = nbformat.read(nfp, as_version=4)
    return notebook

def extract_with_prefix(
        notebook: nbformat.NotebookNode,
        prefix: str
    ) -> TestcellBlock:
    """Extract code blocks from a notebook matching a given prefix.

    Args:
        notebook: Notebook to extract code blocks from.
        prefix: Regex prefix to both decide if a block is extaction worthy, and to extract the testcase name.
                E.g. "### ASSIGNMENT CODE for Puzzle (.*) ==" 

    Returns:
        TestcellBlock object associating testcase names with code blocks.
    """
    per_testcase_code = TestcellBlock()
    pat = compile(prefix)
    clean_pat = compile('\W|^(?=\d)')

    for cell in notebook.cells:
        if cell.cell_type == "code":
            source = cell.source
            newline_idx = source.find("\n")
            first_line = source[:newline_idx]
            rest = source[newline_idx+1:]
            re_match = pat.fullmatch(first_line)
            if re_match is not None:
                testcase_name = re_match.group(1)
                testcase_name = clean_pat.sub("_", testcase_name)
                per_testcase_code.add_codeblock(testcase_name, rest)
    
    return per_testcase_code

