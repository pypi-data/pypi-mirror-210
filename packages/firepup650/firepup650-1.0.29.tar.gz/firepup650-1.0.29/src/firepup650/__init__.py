"""Firepup650's PYPI Package"""
import os, sys, termios, tty, time, sqlite3, ast, pydoc
import random as r
import fkeycapture as fkey
import fpsql as fql
from warnings import warn as ww
from typing import TypeVar, Type, Optional, List, Any
from collections.abc import Iterable


def alias(Function):
    def decorator(f):
        f.__doc__ = (
            "This method is an alias of the following method:\n\n"
            + pydoc.text.document(Function)
        )
        return f

    return decorator


__VERSION__ = "1.0.28"
__NEW__ = "Updates `Color` to flush print by default."
__LICENSE__ = "MIT"


def flushPrint(text: str = ""):
    """# Function: flushPrint
      Prints and flushes the specified `text`.
    # Inputs:
      text: str - The text to print, defaults to ""

    # Returns:
      None

    # Raises:
      None"""
    print(text, end="", flush=True)


flush_print = flushPrint


def clear(ascii: bool = False) -> None:
    """# Function: clear
      Clears the screen
    # Inputs:
      ascii: bool - Controls whether or not we clear with ascii, defaults to False

    # Returns:
      None

    # Raises:
      None"""
    if not ascii:
        os.system("clear")
    else:
        flushPrint("\033[H")


@alias(os.system)
def cmd(command: str) -> int:
    """# Function: cmd
      Runs bash commands
    # Inputs:
      command: str - The command to run

    # Returns:
      int - Status code returned by the command

    # Raises:
      None"""
    status = os.system(command)
    return status


def randint(low: int = 0, high: int = 10) -> int:
    """# Funcion: randint
      A safe randint function
    # Inputs:
      low: int - The bottom number, defaults to 0
      high: int - The top number, defaults to 10

    # Returns:
      int - A number between high and low

    # Raises:
      None"""
    try:
        out = r.randint(low, high)
    except:
        out = r.randint(high, low)
    return out


@alias(sys.exit)
def e(code: object = 0) -> None:
    """# Function: e
      Exits with the provided code
    # Inputs:
      code: object - The status code to exit with, defaults to 0

    # Returns:
      None

    # Raises:
      None"""
    sys.exit(code)


def gp(
    keycount: int = 1, chars: list = ["1", "2"], bytes: bool = False
) -> str or bytes:
    """# Function: gp
      Get keys and print them.
    # Inputs:
      keycount: int - Number of keys to get, defaults to 1
      chars: list - List of keys to accept, defaults to ["1", "2"]
      bytes: bool - Wether to return the kyes as bytes, defaults to False

    # Returns:
      str or bytes - Keys pressed

    # Raises:
      None"""
    got = 0
    keys = ""
    while got < keycount:
        key = fkey.getchars(1, chars)
        keys = f"{keys}{key}"
        flushPrint(key)
        got += 1
    print()
    if not bytes:
        return keys
    else:
        return keys.encode()


def gh(
    keycount: int = 1, chars: list = ["1", "2"], char: str = "*", bytes: bool = False
) -> str or bytes:
    """# Function: gh
      Get keys and print `char` in their place.
    # Inputs:
      keycount: int - Number of keys to get, defaults to 1
      chars: list - List of keys to accept, defaults to ["1", "2"]
      char: str - Character to use to obfuscate the keys, defaults to *
      bytes: bool - Wether to return the kyes as bytes, defaults to False

    # Returns:
      str or bytes - Keys pressed

    # Raises:
      None"""
    got = 0
    keys = ""
    while got < keycount:
        key = fkey.getchars(1, chars)
        keys = f"{keys}{key}"
        flushPrint("*")
        got += 1
    print()
    if not bytes:
        return keys
    else:
        return keys.encode()


def printt(text: str, delay: float = 0.1, newline: bool = True) -> None:
    """# Function: printt
      Print out animated text!
    # Inputs:
      text: str - Text to print (could technicaly be a list)
      delay: float - How long to delay between characters, defaults to 0.1
      newline: bool - Wether or not to add a newline at the end of the text, defaults to True

    # Returns:
      None

    # Raises:
      None"""
    # Store the current terminal settings
    original_terminal_settings = termios.tcgetattr(sys.stdin)
    # Change terminal settings to prevent any interruptions
    tty.setcbreak(sys.stdin)
    for char in text:
        flushPrint(char)
        time.sleep(delay)
    if newline:
        print()
    # Restore the original terminal settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_terminal_settings)


@alias(time.sleep)
def sleep(seconds: float = 0.5) -> None:
    """# Function: sleep
      Calls `time.sleep(seconds)`
    # Inputs:
      seconds: float - How long to sleep for, defaults to 0.5

    # Returns:
      None

    # Raises:
      None"""
    time.sleep(seconds)


@alias(r.seed)
def rseed(seed: Any = None, version: int = 2) -> None:
    """# Function: rseed
      reseed the random number generator
    # Inputs:
      seed: Any - The seed, defaults to None
      version: int - Version of the seed (1 or 2), defaults to 2

    # Returns:
      None

    # Raises:
      None"""
    r.seed(seed, version)


setattr(Iterable, "__class_getitem__", lambda x: None)
T = TypeVar("T")


def robj(iterable: Iterable[T]) -> T:
    """# Function: robj
      Returns a random object from the provided iterable
    # Input:
      iterable: Iterable[T] - Any valid Iterable

    # Returns:
      T - A random object of type `T` from the provided iterable

    # Raises:
      None"""
    return r.choice(iterable)


def Color(
    r: int = 0, g: int = 0, b: int = 0, bcolor: bool = False, flush: bool = True
) -> None or str:
    """# Function: Color
      Set the text to a specific color.
    # Inputs:
      r: int - The red value, range of 0-255, defaults to 0
      g: int - The green value, range of 0-255, defaults to 0
      b: int - The blue value, range of 0-255, defaults to 0
      bcolor: bool - Wether to return the color as a str, defaults to False
      fulsh: bool - Wether to flushPrint the color, defaults to True

    # Returns:
      None or str - The color code if `bcolor` is True. Otherwise, returns nothing

    # Raises:
      None"""
    if r < 0:
        r = 0
    if r > 255:
        r = 255
    if g < 0:
        g = 0
    if g > 255:
        g = 255
    if b < 0:
        b = 0
    if b > 255:
        b = 255
    if bcolor == True:
        return f"\033[38;2;{r};{g};{b}m"
    elif flush:
        flushPrint("\003[0m")
        flushPrint(f"\033[38;2;{r};{g};{b}m")
    else:
        print("\003[0m")
        print(f"\033[38;2;{r};{g};{b}m")


class bcolors:
    """
    This class contains various pre-defined color codes.
    """

    INVERSE = "\033[8m"

    def fINVERSE() -> None:
        """INVERTs foreground and background colors"""
        print("\033[8m", end="")

    RESET = "\033[0m"
    RWHITE = f"\033[0m{Color(255,255,255,bcolor=True)}"
    WHITE = f"{Color(255,255,255,bcolor=True)}"
    FAILINVERSE = f"{Color(255,bcolor=True)}\033[49m\033[7m"

    def fWHITE() -> None:
        """Sets the text color to WHITE"""
        print(f"{Color(255,255,255,bcolor=True)}", end="")

    def fRWHITE() -> None:
        """RESETs the text color, then sets it to WHITE"""
        print(f"\033[0m{Color(255,255,255,bcolor=True)}", end="")

    def fFAILINVERSE() -> None:
        """Sets the text color RED, then inverses it."""
        print(f"{Color(255,bcolor=True)}\033[49m\033[7m", end="")

    def fRESET() -> None:
        """RESETs the formatting"""
        print("\033[0m", end="")

    BROWN = f"{Color(205,127,50,bcolor=True)}"

    def fBROWN() -> None:
        """Sets the text color to BROWN"""
        print(f"{Color(205,127,50,bcolor=True)}", end="")

    WARNING = f"{Color(236,232,26,bcolor=True)}"

    def fWARNING() -> None:
        """Sets the text color to YELLOW"""
        print(f"{Color(236,232,26,bcolor=True)}", end="")

    FAIL = f"{Color(255,bcolor=True)}"

    def fFAIL() -> None:
        """Sets the text color to RED"""
        print(f"{Color(255,bcolor=True)}", end="")

    OK = f"{Color(g=255,bcolor=True)}"

    def fOK() -> None:
        """Sets the text color to GREEN"""
        print(f"{Color(g=255,bcolor=True)}", end="")

    CYAN = f"{Color(g=255,b=255,bcolor=True)}"

    def fCYAN() -> None:
        """Sets the text color to CYAN"""
        print(f"{Color(g=255,b=255,bcolor=True)}", end="")

    WOOD = f"{Color(120,81,45,bcolor=True)}\033[46m\033[7m"

    def fWOOD() -> None:
        """Sets the text color to CYAN, and the background to a WOODen color"""
        print(f"{Color(120,81,45,bcolor=True)}\033[46m\033[7m", end="")

    REPLIT = f"{Color(161, 138, 26, True)}"

    def fREPLIT() -> None:
        """Sets the text color to 161,138,26 in RGB"""
        print(f"{Color(162, 138, 26, True)}")

    GREEN = OK
    fGREEN = fOK
    YELLOW = WARNING
    fYELLOW = fWARNING
    RED = FAIL
    fRED = fFAIL

    class bold:
        """
        Contains bold versions of the other color codes
        """

        BROWN = f"\033[1m{Color(205,127,50,bcolor=True)}"

        def fBROWN() -> None:
            """Sets the text color to BROWN"""
            print(f"\033[1m{Color(205,127,50,bcolor=True)}", end="")

        WARNING = f"\033[1m{Color(236,232,26,bcolor=True)}"

        def fWARNING() -> None:
            """Sets the text color to YELLOW"""
            print(f"\033[1m{Color(236,232,26,bcolor=True)}", end="")

        FAIL = f"\033[1m{Color(255,bcolor=True)}"

        def fFAIL() -> None:
            """Sets the text color to RED"""
            print(f"\033[1m{Color(255,bcolor=True)}", end="")

        OK = f"\033[1m{Color(g=255,bcolor=True)}"

        def fOK() -> None:
            """Sets the text color to GREEN"""
            print(f"\033[1m{Color(g=255,bcolor=True)}", end="")

        CYAN = f"\033[1m{Color(g=255,b=255,bcolor=True)}"

        def fCYAN() -> None:
            """Sets the text color to CYAN"""
            print(f"\033[1m{Color(g=255,b=255,bcolor=True)}", end="")

        WOOD = f"\033[1m{Color(120,81,45,bcolor=True)}\033[46m\033[7m"

        def fWOOD() -> None:
            """Sets the text color to CYAN, and the background to a WOODen color"""
            print(f"\033[1m{Color(120,81,45,bcolor=True)}\033[46m\033[7m", end="")

        WHITE = f"\033[1m{Color(255,255,255,bcolor=True)}"

        def fWHITE() -> None:
            """Sets the text color to WHITE"""
            print(f"\033[1m{Color(255,255,255,bcolor=True)}", end="")

        RWHITE = f"\033[0m\033[1m{Color(255,255,255,bcolor=True)}"

        def fRWHITE() -> None:
            """RESETs the text color, then sets it to WHITE"""
            print(f"\033[0m\033[1m{Color(255,255,255,bcolor=True)}", end="")

        REPLIT = f"\033[1m{Color(161, 138, 26, True)}"

        def fREPLIT() -> None:
            """Sets the text color to 161,138,26 in RGB"""
            print(f"\033[1m{Color(162, 138, 26, True)}")

        GREEN = OK
        fGREEN = fOK
        YELLOW = WARNING
        fYELLOW = fWARNING
        RED = FAIL
        fRED = fFAIL


replitCursor = f"{bcolors.REPLIT}{bcolors.RESET}"
replit_cursor = replitCursor

Oinput = input
cast = TypeVar("cast")


def input(prompt: str = "", cast: Type = str, badCastMessage: str = "") -> cast:
    """# Function: input
      Displays your `prompt`, supports casting by default, with handling!
    # Inputs:
      prompt: str - The prompt, defaults to ""
      cast: Type - The Type to cast the input to, defaults to str
      badCastMessage: str - The message to dispaly upon reciving input that can't be casted to `cast`, can be set to `"None"` to not have one, defaults to f"That is not a vaild {cast.__name__}, please try again."

    # Returns:
      cast - The user's input, casted to `cast`

    # Raises:
      None"""
    if not badCastMessage:
        badCastMessage = f"That is not a vaild {cast.__name__}, please try again."
    ret = ""
    while ret == "":
        try:
            ret = cast(Oinput(prompt))
            break
        except ValueError:
            if badCastMessage != "None":
                print(badCastMessage)
    return ret


def replitInput(prompt: str = "", cast: Type = str, badCastMessage: str = "") -> cast:
    """# Function: replitInput
      Displays your `prompt` with the replit cursor on the next line, supports casting by default, with handling!
    # Inputs:
      prompt: str - The prompt, defaults to ""
      cast: Type - The Type to cast the input to, defaults to str
      badCastMessage: str - The message to dispaly upon reciving input that can't be casted to `cast`, can be set to "No message" to not have one, defaults to f"That is not a vaild {cast.__name__}, please try again."

    # Returns:
      cast - The user's input, casted to `cast`

    # Raises:
      None"""
    if prompt:
        print(prompt)
    return input(f"{replitCursor} ", cast, badCastMessage)


replit_input = replitInput


def cprint(text: str = "") -> None:
    """# Function: cprint
      Displays your `text` in a random color (from bcolors).
    # Inputs:
      text: str - The text to color, defaults to ""

    # Returns:
      None

    # Raises:
      None"""
    colordict = {
        "GREEN": bcolors.GREEN,
        "RED": bcolors.RED,
        "YELLOW": bcolors.YELLOW,
        "CYAN": bcolors.CYAN,
        "REPLIT": bcolors.REPLIT,
        "BROWN": bcolors.BROWN,
        "WHITE": bcolors.WHITE,
    }
    colornames = ["GREEN", "RED", "YELLOW", "CYAN", "REPLIT", "BROWN", "WHITE"]
    color = colordict[robj(colornames)]
    print(f"{color}{text}")


class ProgramWarnings(UserWarning):
    """Warnings Raised for user defined Warnings in `console.warn` by default."""


class AssertationWarning(UserWarning):
    """Warnings Raised for assertion errors in `console.assert_()`."""


class console:
    """Limited Functionality version of JavaScript's console functions"""

    __counters__ = {"default": 0}
    __warnings__ = []

    @alias(print)
    def log(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    @alias(print)
    def info(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    @alias(print)
    def debug(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    def warn(warning: any, class_: Optional[Type[Warning]] = ProgramWarnings) -> None:
        """# Function: console.warn
          Issue a warning
        # Inputs:
          warning: any - The variable to use as a warning
          class_: class - The class to raise the warning from, defaults to ProgramWarnings

        # Returns:
          None

        # Raises:
          None"""
        ind = 1
        while warning in console.__warnings__:
            warning = f"{warning}({ind})"
            ind += 1
        console.__warnings__.append(warning)
        ww(warning, class_, 2)

    def error(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stderr, flush=False)

        Prints the values to sys.stderr.
        Optional keyword arguments:
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(bcolors.FAIL, *args, bcolors.RESET, file=sys.stderr, **kwargs)

    def assert_(condition: bool, message: str = "Assertion Failed") -> None:
        """# Function: console.assert_
          Makes an assertion check
        # Inputs:
          condition: bool - The condition to run an assert check on
          message: str - The message to raise if the assertion is False, defaults to "Assertion Failed"

        # Returns:
          None

        # Raises:
          None"""
        if not condition:
            console.warn(message, AssertationWarning)

    def count(label: str = "default") -> None:
        """# Function: console.count
          Increment a counter by one
        # Inputs:
          label: str - The counter to increment, defaults to "default"

        # Returns:
          None

        # Raises:
          None"""
        if console.__counters__[label]:
            console.__counters__[label] += 1
        else:
            console.__counters__[label] = 1
        print(f"{label}: {console.__counters__[label]}")

    def countReset(label: str = "default") -> None:
        """# Function: console.countReset
          Reset a counter to 0
        # Inputs:
          label: str - The counter to reset, defaults to "default"

        # Returns:
          None

        # Raises:
          None"""
        console.__counters__[label] = 0

    @alias(clear)
    def clear(ascii: bool = False) -> None:
        """# Function: console.clear
          Clears the screen
        # Inputs:
          ascii: bool - Wether to use ASCII to clear the screen, defaults to False

        # Returns:
          None

        # Raises:
          None"""
        clear(ascii)


sql = fql.sql


def removePrefix(text: str, prefix: str) -> str:
    """# Function: removePrefix
    If `prefix` is at the beginning of `text`, return `text` without `prefix`, otherwise return `text`
    # Inputs:
      text: str - The text to remove the prefix from
      prefix: str - The prefix to remove from the text

    # Returns:
      str - `text` without `prefix`

    # Raises:
      None"""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


remove_prefix = removePrefix


def removeSuffix(text: str, suffix: str) -> str:
    """# Function: removeSuffix
    If `suffix` is at the end of `text`, return `text` without `suffix`, otherwise return `text`
    # Inputs:
      text: str - The text to remove the suffix from
      suffix: str - The suffix to remove from the text

    # Returns:
      str - `text` without `suffix`

    # Raises:
      None"""
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


remove_suffix = removeSuffix
