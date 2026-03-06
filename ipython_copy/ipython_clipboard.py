import sys
from argparse import ArgumentTypeError
from ast import literal_eval
from keyword import iskeyword
from pickle import PickleError, PicklingError, UnpicklingError
from pickle import dumps as p_dumps
from pickle import loads as p_loads
from re import compile

import IPython.core.magic_arguments as magic_args
from IPython.core.magic import Magics, line_cell_magic, line_magic, magics_class
from pyperclip import copy as pycopy
from pyperclip import paste as pypaste

ipy_line = compile(r"^_i?(.*)$")  # matches _ _i _N _iN (where N is a positive integer)


def valid_identifier(s: str) -> str:
    """Validates `s`, raising an error if it is not a valid identifier or if it is a python keyword (eg. def, with)"""
    if not s.isidentifier() or iskeyword(s):
        raise ArgumentTypeError(f"{s} is not a valid identifier.")
    return s


def valid_line_num(s: str) -> str:
    """Validates `s`, raising an error if it is not an ipython cache variable (ie. _ __ _i _ii _5 _i5)
    Or a valid line number (ie. a positive integer)"""
    if s in {"_", "__", "___", "_i", "_ii", "_iii"} or s.isdigit():
        return s

    if (match := ipy_line.match(s)) and match.group(1).isdigit():
        return s

    raise ArgumentTypeError(
        f"{s!r} is not a valid line number or ipython cache variable (eg. _, __, _i, _ii)"
    )


@magics_class
class IPythonClipboard(Magics):
    @line_cell_magic
    def clip(self, line: str = "", cell: str | None = None) -> None:
        """
        Copies text, variables, or IPython history to the clipboard.

        Usage:
          %clip              # Copies the last output '_'
          %clip 7            # Copies the output from line 7 ('_7')
          %clip my_var       # Copies the string representation of 'my_var'
          %clip hello world  # Copies the literal text "hello world"

          %%clip             # Cell magic: copies the entire cell contents
          multi-line
          text
        """
        # 1. Handle Cell Magic
        if cell is not None:
            content = f"{line}\n{cell}" if line else cell
            pycopy(content)
            print("Copied cell contents to clipboard.")
            return

        line = line.strip()

        # 2. Handle default (no args)
        if not line:
            content = str(self.shell.user_ns.get("_", ""))
            pycopy(content)
            print("Copied last output ('_') to clipboard.")
            return

        # 3. Handle line number (e.g., "7" -> "_7")
        if line.isdigit():
            history_var = f"_{line}"
            if history_var in self.shell.user_ns:
                content = str(self.shell.user_ns[history_var])
                pycopy(content)
                print(f"Copied output of line {line} to clipboard.")
                return

        # 4. Handle known variables or explicit history (e.g., "my_var", "_i5")
        if line in self.shell.user_ns:
            content = str(self.shell.user_ns[line])
            pycopy(content)
            print(f"Copied variable '{line}' to clipboard.")
            return

        # 5. Fallback: Literal text
        pycopy(line)
        print("Copied literal text to clipboard.")

    @line_magic
    @magic_args.magic_arguments()
    @magic_args.argument(
        "--output",
        "-o",
        type=valid_identifier,
        nargs=1,
        help="The variable to store the output to.",
    )
    @magic_args.argument(
        "var", type=valid_identifier, nargs="?", help="The variable to pickle."
    )
    def pickle(self, line: str = "") -> None:
        """
        Pickles a variable and copies it to the clipboard or un-pickles clipboard contents and prints or stores it.

        `%pickle` unpickle clipboard and print
        `%pickle v` pickle variable `v` and store in clipboard
        `%pickle _` pickle last line's output and store in clipboard
        `%pickle -o my_var` unpickle clipboard contents and store in `my_var`
        """
        args = magic_args.parse_argstring(self.pickle, line)

        if args.output and args.var:
            msg = (
                "Incorrect usage: you can either pickle a variable or unpickle, but not both at the same time.\n"
                f"\n`%pickle {args.var}` to pickle `{args.var}` to your clipboard"
                f"\n`%pickle -o {args.output[0]}` to unpickle from clipboard to `{args.output[0]}`"
                f"\n`%pickle` to unpickle from clipboard and print"
            )
            print(msg, file=sys.stderr)
            return

        if not line or args.output:  # unpickle from clipboard
            content: str = pypaste()

            # Simple heuristic for bytes-like string representation
            if not (content.startswith(("b'", 'b"')) and content[-1] in {"'", '"'}):
                print(
                    "Your clipboard doesn't have a bytes-like string (e.g., b'\\x80\\x03...').",
                    file=sys.stderr,
                )
                return

            if not content:
                print("Your clipboard is empty.", file=sys.stderr)
                return

            try:
                unpickled = p_loads(literal_eval(content))
            except (KeyError, UnpicklingError, PickleError, ValueError, SyntaxError):
                print(
                    "Your clipboard contents could not be unpickled because the data is not valid.",
                    file=sys.stderr,
                )
            else:
                if args.output:
                    self.shell.user_ns[args.output[0]] = unpickled
                    print(f"Unpickled clipboard into '{args.output[0]}'.")
                else:
                    sys.stdout.write(str(unpickled) + "\n")

        else:  # pickle a variable
            val = self.shell.user_ns.get(args.var)
            if val is None and args.var not in self.shell.user_ns:
                print(f"Variable '{args.var}' not found.", file=sys.stderr)
                return

            try:
                pickled_data = str(p_dumps(val))
            except (RuntimeError, PicklingError):
                print(
                    f"The object '{args.var}' could not be pickled. "
                    "It may be highly recursive or unpicklable.\n"
                    "See: https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled",
                    file=sys.stderr,
                )
            else:
                pycopy(pickled_data)
                print(f"Pickled '{args.var}' to clipboard.")


def load_ipython_extension(ipython) -> None:
    ipython.register_magics(IPythonClipboard)
