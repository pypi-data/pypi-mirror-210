from random import choices
from string import ascii_lowercase, ascii_uppercase
from textwrap import indent

from .extractor import TestcellBlock 

def compile_code_and_tests_into_py(
    code_blocks: TestcellBlock,
    test_blocks: TestcellBlock
    ):
    """Given code and test blocks with testcase names matched by codeblock names, 
    return a python file that is pytest testable.

    Args:
        code_blocks: TestcellBlock containing relevant code.
        test_blocks: TestcellBlock containing relevant tests.

    Returns:
        A string containing the python code that can be written to a file for pytest testing.
    """
    part_name = choices(ascii_lowercase + ascii_uppercase, k=20)
    part_name = "".join(part_name)

    func_name = choices(ascii_lowercase + ascii_uppercase, k=20)
    func_name = "".join(func_name)
    py_code = f"def {func_name}({part_name}):\n"
    content = ""

    for testcase in code_blocks.cases:
        print(f"Adding code for {testcase}")
        code_content = code_blocks.get_code_for_testcase(testcase)
        test_content = test_blocks.get_code_for_testcase(testcase)
        test_content += "\nreturn\n"

        content += code_content
        content += "\n"
        if len(test_content) > 8:
            print(f"Adding test for {testcase}")
            content += f"if {part_name} == \"{testcase}\":\n"
            content += indent(test_content, "\t")

    py_code += indent(content, "\t")
    py_code += "\n"

    for testcase in test_blocks.cases:
        py_code += f"def test_{testcase}():\n\t{func_name}(\"{testcase}\")\n\n"

    return py_code
