# Jupyter Notebook Grader

This is a script that will compile a jupyter notebook with a specified structure into a python script that is pytest compatible.

For use in code, `extractor` handles extracting cells from a notebook with a given prefix into a `TestcellBlock` object. `compiler` deals more with taking an assignment notebook and a notebook with testcases,
which can be and often are the same notebook, and with specified prefixes and writing it into a python file capable of running against pytest. For example, the prefix for assignment code could be 
`### ASSIGNMENT CODE for Puzzle (.*) ==` where the group in the regex determines what test the code applies to. Prefixes must have at least one group to match against, and that first group will be the
identification used. To run as a CLI tool, use `python3 -m jupyter2pytest [code file] [code prefix] [test file] [test prefix] [pytest output file]`.
