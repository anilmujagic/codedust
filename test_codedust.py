#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codedust import (
    inspect_line,
    inspect_file,
    is_line_empty,
    line_indent,
    is_line_comment,
    is_section_header
)


class TestCodeDustInspections(unittest.TestCase):
    """Test suite for CodeDust inspection rules"""

    def setUp(self):
        """Set up default rules for testing"""
        self.default_rules = {
            "indent_size": 4,
            "max_line_length": 120,
            "section_header_length": 100,
            "line_comment": "#",
        }

    # Helper method to run inspection and get issues
    def get_issues(self, prev_line, curr_line, next_line, rules=None):
        if rules is None:
            rules = self.default_rules
        return list(inspect_line(prev_line, curr_line, next_line, rules))

    ####################################################################################################
    # CD0101: Empty lines at start of file
    ####################################################################################################

    def test_cd0101_empty_line_at_start_of_file(self):
        # ARRANGE
        prev_line = None
        curr_line = "\n"
        next_line = "some code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0], "CD0101")
        self.assertIn("no empty lines at the start", issues[0][1])

    def test_cd0101_no_issue_when_file_starts_with_code(self):
        # ARRANGE
        prev_line = None
        curr_line = "#!/usr/bin/env python3\n"
        next_line = "import os\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0101", [i[0] for i in issues])

    def test_cd0101_disabled_when_configured(self):
        # ARRANGE
        prev_line = None
        curr_line = "\n"
        next_line = "some code\n"
        rules = {**self.default_rules, "CD0101": False}

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line, rules)

        # ASSERT
        self.assertNotIn("CD0101", [i[0] for i in issues])

    ####################################################################################################
    # CD0102: Empty lines at end of file
    ####################################################################################################

    def test_cd0102_empty_line_at_end_of_file(self):
        # ARRANGE
        prev_line = "some code\n"
        curr_line = "\n"
        next_line = None

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0], "CD0102")
        self.assertIn("no empty lines at the end", issues[0][1])

    def test_cd0102_no_issue_when_file_ends_with_code(self):
        # ARRANGE
        prev_line = "some code\n"
        curr_line = "last line\n"
        next_line = None

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0102", [i[0] for i in issues])

    ####################################################################################################
    # CD0103: Missing line break at end of file
    ####################################################################################################

    def test_cd0103_no_line_break_at_end_of_file(self):
        # ARRANGE
        prev_line = "some code\n"
        curr_line = "last line"
        next_line = None

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0103", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0103"][0]
        self.assertIn("line break at the end", issue[1])

    def test_cd0103_no_issue_when_line_break_exists(self):
        # ARRANGE
        prev_line = "some code\n"
        curr_line = "last line\n"
        next_line = None

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0103", [i[0] for i in issues])

    ####################################################################################################
    # CD0104: Multiple consecutive empty lines
    ####################################################################################################

    def test_cd0104_multiple_consecutive_empty_lines(self):
        # ARRANGE
        prev_line = "\n"
        curr_line = "\n"
        next_line = "some code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0104", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0104"][0]
        self.assertIn("no multiple consecutive empty lines", issue[1])

    def test_cd0104_single_empty_line_allowed(self):
        # ARRANGE
        prev_line = "some code\n"
        curr_line = "\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0104", [i[0] for i in issues])

    ####################################################################################################
    # CD0105: Empty line after opening bracket
    ####################################################################################################

    def test_cd0105_empty_line_after_opening_brace(self):
        # ARRANGE
        prev_line = "if (true) {\n"
        curr_line = "\n"
        next_line = "    code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0105", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0105"][0]
        self.assertIn("no empty lines at the start of a parenthesis block", issue[1])

    def test_cd0105_empty_line_after_opening_bracket(self):
        # ARRANGE
        prev_line = "array = [\n"
        curr_line = "\n"
        next_line = "    item\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0105", [i[0] for i in issues])

    def test_cd0105_empty_line_after_opening_paren(self):
        # ARRANGE
        prev_line = "function(\n"
        curr_line = "\n"
        next_line = "    arg\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0105", [i[0] for i in issues])

    def test_cd0105_empty_line_after_opening_angle_bracket(self):
        # ARRANGE
        prev_line = "List<\n"
        curr_line = "\n"
        next_line = "    String\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0105", [i[0] for i in issues])

    ####################################################################################################
    # CD0106: Empty line before closing bracket
    ####################################################################################################

    def test_cd0106_empty_line_before_closing_brace(self):
        # ARRANGE
        prev_line = "    code\n"
        curr_line = "\n"
        next_line = "}\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0106", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0106"][0]
        self.assertIn("no empty lines at the end of a parenthesis block", issue[1])

    def test_cd0106_empty_line_before_closing_bracket(self):
        # ARRANGE
        prev_line = "    item\n"
        curr_line = "\n"
        next_line = "]\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0106", [i[0] for i in issues])

    def test_cd0106_empty_line_before_closing_paren(self):
        # ARRANGE
        prev_line = "    arg\n"
        curr_line = "\n"
        next_line = ")\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0106", [i[0] for i in issues])

    ####################################################################################################
    # CD0107: Empty line after section header
    ####################################################################################################

    def test_cd0107_empty_line_after_section_header(self):
        # ARRANGE
        prev_line = "####################################################################################################\n"
        curr_line = "\n"
        next_line = "def function():\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0107", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0107"][0]
        self.assertIn("no empty lines after the section header", issue[1])

    def test_cd0107_no_issue_when_comment_follows_header(self):
        # ARRANGE
        prev_line = "####################################################################################################\n"
        curr_line = "\n"
        next_line = "# This is a comment\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0107", [i[0] for i in issues])

    ####################################################################################################
    # CD0201: Multiple consecutive spaces
    ####################################################################################################

    def test_cd0201_multiple_consecutive_spaces(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable  = value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0201", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0201"][0]
        self.assertIn("no multiple consecutive spaces", issue[1])

    def test_cd0201_leading_spaces_allowed(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "    indented code\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0201", [i[0] for i in issues])

    ####################################################################################################
    # CD0202: Trailing spaces
    ####################################################################################################

    def test_cd0202_trailing_space(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "some code \n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0202", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0202"][0]
        self.assertIn("no spaces at the end of a line", issue[1])

    def test_cd0202_no_issue_without_trailing_space(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "some code\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0202", [i[0] for i in issues])

    ####################################################################################################
    # CD0203: Space before comma
    ####################################################################################################

    def test_cd0203_space_before_comma(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(a , b)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0203", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0203"][0]
        self.assertIn("no space before comma", issue[1])

    def test_cd0203_no_issue_without_space_before_comma(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(a, b)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0203", [i[0] for i in issues])

    ####################################################################################################
    # CD0204: Space before semicolon
    ####################################################################################################

    def test_cd0204_space_before_semicolon(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "statement ;\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0204", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0204"][0]
        self.assertIn("no space before semicolon", issue[1])

    def test_cd0204_no_issue_without_space_before_semicolon(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "statement;\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0204", [i[0] for i in issues])

    ####################################################################################################
    # CD0205: Space after opening parenthesis
    ####################################################################################################

    def test_cd0205_space_after_opening_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func( arg)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0205", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0205"][0]
        self.assertIn("no space after opening parentheses", issue[1])

    def test_cd0205_no_issue_without_space_after_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(arg)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0205", [i[0] for i in issues])

    ####################################################################################################
    # CD0206: Space before closing parenthesis
    ####################################################################################################

    def test_cd0206_space_before_closing_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(arg )\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0206", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0206"][0]
        self.assertIn("no space before closing parentheses", issue[1])

    def test_cd0206_no_issue_without_space_before_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(arg)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0206", [i[0] for i in issues])

    ####################################################################################################
    # CD0207: Missing space after comma
    ####################################################################################################

    def test_cd0207_missing_space_after_comma(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(a,b)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0207", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0207"][0]
        self.assertIn("should be a space after comma", issue[1])

    def test_cd0207_no_issue_with_space_after_comma(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func(a, b)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0207", [i[0] for i in issues])

    ####################################################################################################
    # CD0208: Missing space after semicolon
    ####################################################################################################

    def test_cd0208_missing_space_after_semicolon(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "for (i=0;i<10;i++)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        issue_codes = [i[0] for i in issues]
        self.assertIn("CD0208", issue_codes)
        issue = [i for i in issues if i[0] == "CD0208"][0]
        self.assertIn("should be a space after semicolon", issue[1])

    def test_cd0208_no_issue_with_space_after_semicolon(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "for (i=0; i<10; i++)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0208", [i[0] for i in issues])

    ####################################################################################################
    # CD0209: Missing space before equal sign
    ####################################################################################################

    def test_cd0209_missing_space_before_equal_alphanumeric(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable= value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0209", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0209"][0]
        self.assertIn("should be a space before equal sign", issue[1])

    def test_cd0209_missing_space_before_equal_after_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "func()= value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0209", [i[0] for i in issues])

    def test_cd0209_missing_space_before_equal_after_bracket(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "array[0]= value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0209", [i[0] for i in issues])

    def test_cd0209_no_issue_with_space_before_equal(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0209", [i[0] for i in issues])

    def test_cd0209_no_issue_with_four_equals(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "if a==== b\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0209", [i[0] for i in issues])

    ####################################################################################################
    # CD0210: Missing space after equal sign
    ####################################################################################################

    def test_cd0210_missing_space_after_equal_alphanumeric(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable =value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0210", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0210"][0]
        self.assertIn("should be a space after equal sign", issue[1])

    def test_cd0210_missing_space_after_equal_before_paren(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable =(value)\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0210", [i[0] for i in issues])

    def test_cd0210_missing_space_after_equal_before_string(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable =\"value\"\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0210", [i[0] for i in issues])

    def test_cd0210_no_issue_with_space_after_equal(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0210", [i[0] for i in issues])

    def test_cd0210_no_issue_with_four_equals(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "if a ====b\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0210", [i[0] for i in issues])

    ####################################################################################################
    # CD0301: Tab usage
    ####################################################################################################

    def test_cd0301_tab_character(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "\tindented code\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0301", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0301"][0]
        self.assertIn("Don't use tabs", issue[1])
        self.assertIn("4 spaces", issue[1])

    def test_cd0301_no_issue_with_spaces(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "    indented code\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0301", [i[0] for i in issues])

    ####################################################################################################
    # CD0302: Incorrect indentation size
    ####################################################################################################

    def test_cd0302_incorrect_indentation_size(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "   indented code\n"  # 3 spaces instead of 4
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0302", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0302"][0]
        self.assertIn("Use 4 spaces per indentation level", issue[1])

    def test_cd0302_correct_indentation_size(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "    indented code\n"  # 4 spaces
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0302", [i[0] for i in issues])

    def test_cd0302_correct_double_indentation(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "        double indented\n"  # 8 spaces
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0302", [i[0] for i in issues])

    ####################################################################################################
    # CD0303: Too many indentation levels at once
    ####################################################################################################

    def test_cd0303_too_many_indentation_levels(self):
        # ARRANGE
        prev_line = "unindented\n"
        curr_line = "        double indent jump\n"  # Jump from 0 to 8 spaces
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0303", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0303"][0]
        self.assertIn("Don't indent for more than one level", issue[1])

    def test_cd0303_single_indentation_level_ok(self):
        # ARRANGE
        prev_line = "unindented\n"
        curr_line = "    single indent\n"  # Jump from 0 to 4 spaces
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0303", [i[0] for i in issues])

    def test_cd0303_not_triggered_by_empty_line(self):
        # ARRANGE
        prev_line = "\n"
        curr_line = "        indented\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0303", [i[0] for i in issues])

    ####################################################################################################
    # CD0401: Line too long
    ####################################################################################################

    def test_cd0401_line_too_long(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "x" * 121 + "\n"  # 121 characters, exceeds 120 limit
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0401", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0401"][0]
        self.assertIn("not be longer than 120 characters", issue[1])

    def test_cd0401_line_at_max_length_ok(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "x" * 120 + "\n"  # Exactly 120 characters
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0401", [i[0] for i in issues])

    def test_cd0401_custom_max_line_length(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "x" * 81 + "\n"  # 81 characters
        next_line = "more code\n"
        rules = {**self.default_rules, "max_line_length": 80}

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line, rules)

        # ASSERT
        self.assertIn("CD0401", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0401"][0]
        self.assertIn("not be longer than 80 characters", issue[1])

    ####################################################################################################
    # CD0402: Section header incorrect length
    ####################################################################################################

    def test_cd0402_section_header_wrong_length_too_short(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "#" * 50 + "\n"  # 50 characters, should be 100
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0402", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0402"][0]
        self.assertIn("should be 100 characters long", issue[1])

    def test_cd0402_section_header_wrong_length_too_long(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "/" * 101 + "\n"  # 101 characters, should be 100
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0402", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0402"][0]
        self.assertIn("should be 100 characters long", issue[1])

    def test_cd0402_section_header_correct_length(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "-" * 100 + "\n"  # Exactly 100 characters
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0402", [i[0] for i in issues])

    def test_cd0402_not_triggered_for_non_header(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "# This is just a comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0402", [i[0] for i in issues])

    ####################################################################################################
    # CD0501: Missing space after comment characters
    ####################################################################################################

    def test_cd0501_missing_space_after_comment(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "#This is a comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0501", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0501"][0]
        self.assertIn("space between comment syntax characters and comment text", issue[1])

    def test_cd0501_space_after_comment_ok(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "# This is a comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0501", [i[0] for i in issues])

    def test_cd0501_inline_comment_missing_space(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value #comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0501", [i[0] for i in issues])

    def test_cd0501_not_triggered_for_empty_comment(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "#\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0501", [i[0] for i in issues])

    def test_cd0501_not_triggered_for_section_header(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "#" * 100 + "\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0501", [i[0] for i in issues])

    ####################################################################################################
    # CD0502: Missing space before inline comment
    ####################################################################################################

    def test_cd0502_missing_space_before_inline_comment(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value# comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertIn("CD0502", [i[0] for i in issues])
        issue = [i for i in issues if i[0] == "CD0502"][0]
        self.assertIn("space before comment syntax characters", issue[1])

    def test_cd0502_space_before_inline_comment_ok(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value # comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0502", [i[0] for i in issues])

    def test_cd0502_not_triggered_for_line_comment(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "# This is a line comment\n"
        next_line = "more code\n"

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line)

        # ASSERT
        self.assertNotIn("CD0502", [i[0] for i in issues])

    ####################################################################################################
    # Test Helper Functions
    ####################################################################################################

    def test_is_line_empty(self):
        # ARRANGE & ACT & ASSERT
        self.assertTrue(is_line_empty("\n"))
        self.assertTrue(is_line_empty("  \n"))
        self.assertTrue(is_line_empty("\t\n"))
        self.assertTrue(is_line_empty("   \t  \n"))
        self.assertFalse(is_line_empty("code\n"))
        self.assertFalse(is_line_empty("  code  \n"))

    def test_line_indent(self):
        # ARRANGE & ACT & ASSERT
        self.assertEqual(line_indent("code"), 0)
        self.assertEqual(line_indent(" code"), 1)
        self.assertEqual(line_indent("    code"), 4)
        self.assertEqual(line_indent("        code"), 8)
        self.assertEqual(line_indent("\n"), 0)

    def test_is_line_comment(self):
        # ARRANGE & ACT & ASSERT
        self.assertTrue(is_line_comment("# comment", "#"))
        self.assertTrue(is_line_comment("  # comment", "#"))
        self.assertTrue(is_line_comment("// comment", "//"))
        self.assertFalse(is_line_comment("code # comment", "#"))
        self.assertFalse(is_line_comment("code", "#"))
        self.assertFalse(is_line_comment("# comment", None))

    def test_is_section_header(self):
        # ARRANGE & ACT & ASSERT
        self.assertTrue(is_section_header("#" * 50, "#"))
        self.assertTrue(is_section_header("/" * 50, "//"))
        self.assertTrue(is_section_header("-" * 50, "#"))
        self.assertTrue(is_section_header("  ###  ", "#"))
        self.assertFalse(is_section_header("# comment", "#"))
        self.assertFalse(is_section_header("#", "#"))
        self.assertFalse(is_section_header("code", "#"))

    ####################################################################################################
    # Test CodeDust Control Comments
    ####################################################################################################

    def test_codedust_skip_line(self):
        # ARRANGE
        file_content = """line1
line2  # CodeDust: SKIP
line3
"""

        # ACT
        with patch("builtins.open", mock_open(read_data=file_content)):
            issues = list(inspect_file("test.py", self.default_rules))

        # ASSERT
        # Line 2 has trailing space but should be skipped
        issue_lines = [i[0] for i in issues]
        self.assertNotIn(2, issue_lines)

    def test_codedust_off_on(self):
        # ARRANGE
        file_content = "line1\n# CodeDust: OFF\nline2  \nline3  \n# CodeDust: ON\nline4  \n"

        # ACT
        with patch("builtins.open", mock_open(read_data=file_content)):
            issues = list(inspect_file("test.py", self.default_rules))

        # ASSERT
        # Lines 3-4 have trailing spaces but are in OFF section
        # Line 6 has trailing space and should be caught
        issue_lines = [i[0] for i in issues]
        self.assertNotIn(3, issue_lines)
        self.assertNotIn(4, issue_lines)
        self.assertIn(6, issue_lines)

    def test_codedust_not_reenabled_warning(self):
        # ARRANGE
        file_content = """line1
# CodeDust: OFF
line2
line3
"""

        # ACT
        with patch("builtins.open", mock_open(read_data=file_content)):
            issues = list(inspect_file("test.py", self.default_rules))

        # ASSERT
        # Should get a warning that CodeDust was not re-enabled
        self.assertTrue(any("should be re-enabled afterwards" in str(i) for i in issues))
        issue_with_warning = [i for i in issues if "should be re-enabled afterwards" in str(i)][0]
        self.assertEqual(issue_with_warning[0], 2)  # Line where OFF was declared

    ####################################################################################################
    # Test with different line comment configurations
    ####################################################################################################

    def test_javascript_style_comments(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value //comment\n"
        next_line = "more code\n"
        rules = {**self.default_rules, "line_comment": "//"}

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line, rules)

        # ASSERT
        self.assertIn("CD0501", [i[0] for i in issues])  # Missing space after //

    def test_no_line_comment_configured(self):
        # ARRANGE
        prev_line = "code\n"
        curr_line = "variable = value # comment\n"
        next_line = "more code\n"
        rules = {**self.default_rules, "line_comment": None}

        # ACT
        issues = self.get_issues(prev_line, curr_line, next_line, rules)

        # ASSERT
        # Should not check comment-related rules
        self.assertNotIn("CD0501", [i[0] for i in issues])
        self.assertNotIn("CD0502", [i[0] for i in issues])


if __name__ == "__main__":
    unittest.main()
