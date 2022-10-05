#!/usr/bin/env python3

import argparse
import configparser
import os
import sys
import re

####################################################################################################
# CLI Arguments
####################################################################################################
def parse_args():
    args_parser = argparse.ArgumentParser(
        prog = "codedust",
        description = "CodeDust - code hygiene inspector",
    )

    args_parser.add_argument(
        "-e",
        "--extension",
        metavar = "extension",
        type = str,
        required = True,
        action = "append",
        help = "File type to inspect (e.g. -e py -e js -e java). Can occur multiple times.",
    )

    args_parser.add_argument(
        "-p",
        "--path",
        metavar = "path",
        type = str,
        required = True,
        action = "append",
        help = "Path to the directory containing code to inspect. Can occur multiple times.",
    )

    args_parser.add_argument(
        "-i",
        "--ignore",
        metavar = "ignore",
        type = str,
        action = "append",
        help = "Regex pattern for filtering out file paths. Can occur multiple times.",
    )

    args_parser.add_argument(
        "-c",
        "--config",
        metavar = "configfile",
        type = str,
        help = "Path to the file containing configuration",
    )

    return args_parser.parse_args()

def validate_args(args):
    for path in args.path:
        if not os.path.isdir(path):
            print(f"Path not found: '{path}'")
            sys.exit()

    if args.config and not os.path.isfile(args.config):
        print(f"File not found: '{args.config}'")
        sys.exit()

####################################################################################################
# Inspection Rules
####################################################################################################
def load_rules(config_file, extensions):
    static_rules = {
        "indent_size": 4,
        "max_line_length": 120,
        "section_header_length": 100,
        "line_comment": None,
    }

    config = {}
    if config_file:
        config = configparser.ConfigParser()
        config.read(config_file)

    default_rules_from_file = config["default"] if "default" in config else {}
    default_rules = {**static_rules, **default_rules_from_file}

    rules_per_extension = {}
    for ext in extensions:
        extension_rules_from_file = config[ext] if ext in config else {}
        rules_per_extension[ext] = {**default_rules, **extension_rules_from_file}
        for rule in list(rules_per_extension[ext].keys()):
            if re.match(r"CD[0-9]{4}", rule.upper()):
                bool_value = False if rules_per_extension[ext].pop(rule).lower() == "disable" else True
                rules_per_extension[ext][rule.upper()] = bool_value
            else:
                try:
                    rules_per_extension[ext][rule] = int(rules_per_extension[ext][rule])
                except:
                    pass # Just a best effort try - if it's a string, then it should stay so.

    return rules_per_extension

def is_line_empty(line):
    return line.strip() == ""

def line_indent(line):
    return re.match(r' *', line).end()

def inspect_line(prev_line, curr_line, next_line, rules):
    # Empty Lines
    if is_line_empty(curr_line) and prev_line == None:
        if rules.get("CD0101") != False:
            yield ("CD0101", "There should be no empty lines at the start of the file.")

    if is_line_empty(curr_line) and next_line == None:
        if rules.get("CD0102") != False:
            yield ("CD0102", "There should be no empty lines at the end of the file.")

    if not curr_line.endswith("\n") and next_line == None:
        if rules.get("CD0103") != False:
            yield ("CD0103", "There should be a line break at the end of the file.")

    if curr_line != None and prev_line != None:
        if is_line_empty(prev_line) and is_line_empty(curr_line):
            if rules.get("CD0104") != False:
                yield ("CD0104", "There should be no multiple consecutive empty lines.")

        if is_line_empty(curr_line) and re.search(r'[\{\[\(\<]$', prev_line.strip()):
            if rules.get("CD0105") != False:
                yield ("CD0105", "There should be no empty lines at the start of a parenthesis block.")

        if is_line_empty(curr_line) and re.search(r'^[\}\]\)\>]', next_line.strip()):
            if rules.get("CD0106") != False:
                yield ("CD0106", "There should be no empty lines at the end of a parenthesis block.")

        # Spaces
        if "  " in curr_line.strip(): # CodeDust: SKIP
            if rules.get("CD0201") != False:
                yield ("CD0201", "There should be no multiple consecutive spaces in a line.")

        if curr_line.endswith(" \n"):
            if rules.get("CD0202") != False:
                yield ("CD0202", "There should be no spaces at the end of a line.")

        if " ," in curr_line.strip(): # CodeDust: SKIP
            if rules.get("CD0203") != False:
                yield ("CD0203", "There should be no space before comma.")

        if " ;" in curr_line.strip(): # CodeDust: SKIP
            if rules.get("CD0204") != False:
                yield ("CD0204", "There should be no space before semicolon.")

        if "( " in curr_line.strip(): # CodeDust: SKIP
            if rules.get("CD0205") != False:
                yield ("CD0205", "There should be no space after opening parentheses.")

        if " )" in curr_line.strip(): # CodeDust: SKIP
            if rules.get("CD0206") != False:
                yield ("CD0206", "There should be no space before closing parentheses.")

        if re.search(r'\,[\w\(]', curr_line):
            if rules.get("CD0207") != False:
                yield ("CD0207", "There should be a space after comma.")

        if re.search(r'\;[\w\(]', curr_line):
            if rules.get("CD0208") != False:
                yield ("CD0208", "There should be a space after semicolon.")

        if re.search(r'[a-z0-9\)\]\}\"\']\=', curr_line) and "====" not in curr_line:
            if rules.get("CD0209") != False:
                yield ("CD0209", "There should be a space before equal sign.")

        if re.search(r'\=[a-z0-9\(\[\{\"\']', curr_line) and "====" not in curr_line: # CodeDust: SKIP
            if rules.get("CD0210") != False:
                yield ("CD0210", "There should be a space after equal sign.")

        # Indentation
        indent_size = rules["indent_size"]

        if "\t" in curr_line:
            if rules.get("CD0301") != False:
                yield ("CD0301", f"Don't use tabs, use {indent_size} spaces.")

        if line_indent(curr_line) % indent_size != 0:
            if rules.get("CD0302") != False:
                yield ("CD0302", f"Use {indent_size} spaces per indentation level.")

        if not is_line_empty(prev_line) \
        and line_indent(curr_line) > line_indent(prev_line) \
        and line_indent(curr_line) - line_indent(prev_line) > indent_size:
            if rules.get("CD0303") != False:
                yield ("CD0303", f"Don't indent for more than one level ({indent_size} spaces) at a time.")

        # Length
        max_line_length = rules["max_line_length"]

        if len(curr_line.rstrip()) > max_line_length:
            if rules.get("CD0401") != False:
                yield ("CD0401", f"Line should not be longer than {max_line_length} characters.")

        section_header_length = rules["section_header_length"]

        is_section_header = False
        if re.search(r'(^\#+$)|(^\/+$)|(^\-+$)', curr_line.strip()): # CodeDust: SKIP
            is_section_header = True
            if len(curr_line.strip()) != section_header_length:
                if rules.get("CD0402") != False:
                    yield ("CD0402", f"Section header should be {section_header_length} characters long.")

        # Comments
        line_comment = rules["line_comment"]
        if line_comment and len(line_comment) and line_comment in curr_line and not is_section_header:
            if not f"{line_comment} " in curr_line:
                if rules.get("CD0501") != False:
                    yield ("CD0501", "There should be a space between comment syntax characters and comment text.")

            if not f" {line_comment}" in curr_line and not curr_line.startswith(line_comment):
                if rules.get("CD0502") != False:
                    yield ("CD0502", "There should be a space before comment syntax characters.")

####################################################################################################
# Execution
####################################################################################################
def get_files(path, extensions, ignored_patterns):
    for d, _, files in os.walk(path):
        for f in files:
            file_path = os.path.join(d, f)
            if should_ignore(file_path, ignored_patterns):
                continue
            file_extension = os.path.splitext(f)[1].strip(".")
            if file_extension in extensions:
                yield (file_path, file_extension)

def should_ignore(file_path, ignored_patterns):
    if ignored_patterns:
        for p in ignored_patterns:
            if re.search(p, file_path):
                return True

    return False

def inspect_file(file_path, rules):
    try:
        with open(file_path) as file:
            lines = file.readlines()
    except Exception as e:
        raise Exception(f"Cannot read file {file_path}") from e

    lines_with_context = zip(
        [None] + lines[:-1],
        lines,
        lines[1:] + [None],
    )

    line_number = 0
    code_dust_enabled = True
    code_dust_disabled_in_line = 0

    for pl, cl, nl in lines_with_context:
        line_number += 1
        if " CodeDust: OFF\n" in cl:
            code_dust_enabled = False
            code_dust_disabled_in_line = line_number
        if " CodeDust: ON\n" in cl:
            code_dust_enabled = True
            code_dust_disabled_in_line = 0
        if " CodeDust: SKIP\n" in cl or not code_dust_enabled:
            continue

        for issue_code, issue_message in inspect_line(pl, cl, nl, rules):
            yield (line_number, issue_code, issue_message)

    if code_dust_disabled_in_line > 0:
        yield (code_dust_disabled_in_line, "CodeDust should be re-enabled afterwards.")

####################################################################################################
# Composition
####################################################################################################
if __name__ == "__main__":
    args = parse_args()
    validate_args(args)

    extensions = [e.strip() for e in args.extension if e.strip()]
    paths = args.path
    ignored_patterns = args.ignore
    rules = load_rules(args.config, extensions)

    issue_count = 0
    for path in paths:
        for file_path, file_extension in get_files(path, extensions, ignored_patterns):
            for line_number, issue_code, issue_message in inspect_file(file_path, rules[file_extension]):
                issue_count += 1
                print(f"{file_path} [{line_number}]: ({issue_code}) {issue_message}")

    print(f"{issue_count} issue(s)")
    if issue_count > 0:
        sys.exit(1)
