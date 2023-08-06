# cfg_argparser 1.1.5

a config wrapper I made to be easily applied to argparse objects.

## Installation

```bash
# from pypi:
pip install cfg-argparser

# from github:
git clone "https://github.com/zeptofine/cfg-argparser"
cd cfg-argparser
pip install -e .

```

## Example

```python
import argparse

from cfg_argparser import ConfigArgParser


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    return parser

if __name__ == "__main__":
    args = ConfigArgParser(parser(),
                           "config.json",
                           exit_on_change=True).parse_args()
    print(args.file)
```

Wrapping the `ConfigArgParser` around `parser()` adds a few "magic" arguments.
here's what it adds:

```rich
Config options:
  --set KEY VAL        change a default argument's options
  --reset [VALUE ...]  removes a changed option.
  --reset_all          resets every option.
```

Here's what it looks like in practice:

```null
> python example.py
None
> python example.py --file foo.txt
foo.txt
> python example.py --set file foo.txt
> python example.py
foo.txt
```

## Compatibilty

This was mainly tested on 3.9 and 3.10, but it should work from 3.6 onwards. i can't test earlier versions for some reason.
