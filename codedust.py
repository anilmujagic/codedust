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
        for rule in rules_per_extension[ext].keys():
            try:
                rules_per_extension[ext][rule] = int(rules_per_extension[ext][rule])
            except:
                pass # Just a best effort try - if it's a string, then it should stay so.

    return rules_per_extension

def is_line_empty(line):
    return line.strip() == ""

def line_indent(line):
    return re.match(r' *', line).end()

def inspect_line(prev_line, curr_line, next_line, file_extension, rules):
    # Empty Lines
    if is_line_empty(curr_line) and prev_line == None:
        yield "There should be no empty lines at the start of the file."

    if is_line_empty(curr_line) and next_line == None:
        yield "There should be no empty lines at the end of the file."

    if not curr_line.endswith("\n") and next_line == None:
        yield "There should be a line break at the end of the file."

    if curr_line != None and prev_line != None:
        if is_line_empty(prev_line) and is_line_empty(curr_line):
            yield "There should be no multiple consecutive empty lines."

        # Spaces
        if "  " in curr_line.strip(): # CodeDust: SKIP
            yield "There should be no multiple consecutive spaces in a line."

        if curr_line.endswith(" \n"):
            yield "There should be no spaces at the end of a line."

        if " ," in curr_line.strip(): # CodeDust: SKIP
            yield "There should be no space before comma."

        if " ;" in curr_line.strip(): # CodeDust: SKIP
            yield "There should be no space before semicolon."

        if "( " in curr_line.strip(): # CodeDust: SKIP
            yield "There should be no space after opening parentheses."

        if " )" in curr_line.strip(): # CodeDust: SKIP
            yield "There should be no space before closing parentheses."

        if re.search(r'\,[\w\(]', curr_line):
            yield "There should be a space after comma."

        if re.search(r'\;[\w\(]', curr_line):
            yield "There should be a space after semicolon."

        if re.search(r'[a-z0-9\)\]\}\"\']\=', curr_line) and "====" not in curr_line:
            yield "There should be a space before equal sign."

        if re.search(r'\=[a-z0-9\(\[\{\"\']', curr_line) and "====" not in curr_line: # CodeDust: SKIP
            yield "There should be a space after equal sign."

        # Indentation
        indent_size = rules[file_extension]["indent_size"]

        if "\t" in curr_line:
            yield f"Don't use tabs, use {indent_size} spaces."

        if line_indent(curr_line) % indent_size != 0:
            yield f"Use {indent_size} spaces per indentation level."

        if not is_line_empty(prev_line) \
        and line_indent(curr_line) > line_indent(prev_line) \
        and line_indent(curr_line) - line_indent(prev_line) != indent_size:
            yield f"Don't indent for more than one level ({indent_size} spaces) at a time."

        # Length
        max_line_length = rules[file_extension]["max_line_length"]

        if len(curr_line.rstrip()) > max_line_length:
            yield f"Line should not be longer than {max_line_length} characters."

        section_header_length = rules[file_extension]["section_header_length"]

        is_section_header = False
        if re.search(r'(^\#+$)|(^\/+$)|(^\-+$)', curr_line.strip()): # CodeDust: SKIP
            is_section_header = True
            if len(curr_line.strip()) != section_header_length:
                yield f"Section header should be {section_header_length} characters long."

        # Comments
        line_comment = rules[file_extension]["line_comment"]
        if line_comment and len(line_comment) and line_comment in curr_line and not is_section_header:
            if not f"{line_comment} " in curr_line:
                yield "There should be a space between comment syntax characters and comment text."

            if not f" {line_comment}" in curr_line and not curr_line.startswith(f"{line_comment} "):
                yield "There should be a space before comment syntax characters."

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

def inspect_file(file_path, file_extension, rules):
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

        for issue in inspect_line(pl, cl, nl, file_extension, rules):
            yield (line_number, issue)

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
            for line_number, issue in inspect_file(file_path, file_extension, rules):
                issue_count += 1
                print(f"{file_path} [{line_number}]: {issue}")

    print(f"{issue_count} issue(s)")
    if issue_count > 0:
        sys.exit(1)
