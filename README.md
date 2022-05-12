# CodeDust

CodeDust inspects the code, on textual level, and detects the cases of bad code hygiene, like excessive empty lines, inconsistent indentation, space characters at the end of the lines, etc.


## Usage

Examples:

```bash
python3 codedust.py --help

python3 codedust.py \
    --extension py \
    --extension js \
    --extension java \
    --path /some/dir \
    --path /some/other/dir \
    --ignore '/node_modules/' \
    --config codedust.cfg

python3 codedust.py -e py -e js -p /some/dir -p /some/other/dir
```

Config file can be used to adjust the rules that are applied for each file type (extension) during the inspection. Config file contains one `default` section, specifying common values, and one section per file type (extension), specifying overrides applying to those files.

```ini
[default]
indent_size = 4
max_line_length = 120
section_header_length = 100

[js]
indent_size = 2

[py]
max_line_length = 80
```

A [sample config file](codedust.cfg) is part of this repository.
