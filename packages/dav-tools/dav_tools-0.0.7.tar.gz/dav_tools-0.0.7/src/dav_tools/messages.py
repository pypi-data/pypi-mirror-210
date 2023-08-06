import sys as _sys

from .text_color import TextFormat
from .text_color import print_colored_text as _print_colored_text
from .text_color import input_colored as _input_colored
from .text_color import clear_line as _clear_line


# generic and customizable message
def message(*text: str | object, text_min_len: list[int] = [], default_text_options=[], additional_text_options=[[]], icon=None, icon_options=[], blink=False, end='\n', file=_sys.stderr):
    _clear_line()

    # icon
    if icon is not None:
        _print_colored_text('[', *icon_options, TextFormat.Style.BOLD, end='', file=file)
        
        if blink:
            _print_colored_text(icon, *icon_options, TextFormat.Style.BOLD, TextFormat.Style.BLINK, end='', file=file)
        else:
            _print_colored_text(icon, *icon_options, TextFormat.Style.BOLD, end='', file=file)
        
        _print_colored_text(']', *icon_options, TextFormat.Style.BOLD, end='', file=file)
        _print_colored_text(' ', end='', file=file)
    
    # text
    for i in range(len(text)):
        line_text = str(text[i])
        line_options = default_text_options + additional_text_options[i] if i < len(additional_text_options) else default_text_options
        line_end = ' ' if i < len(text) - 1 else ''

        _print_colored_text(line_text, *line_options, end=line_end, file=file)

        # padding
        if i < len(text_min_len):
            line_padding = text_min_len[i] - len(line_text)
            if line_padding > 0:
               _print_colored_text(' ' * line_padding, end='', file=file)
        

    # line end and flushing
    _print_colored_text(end=end, file=file, flush=True)
    
# message indicating an information
def info(*text: str | object, text_min_len: list[int] = [], text_options=[[]], blink=False) -> None:
    message(*text,
            icon='*',
            icon_options=[
                TextFormat.Color.BLUE
            ],
            text_min_len=text_min_len,
            additional_text_options=text_options,
            blink=blink)

# messages indicating an action which is still happening
def progress(*text: str | object, text_min_len: list[int] = [], text_options=[[]]) -> None:
    message(*text,
            icon=' ',
            end='\r',
            text_min_len=text_min_len,
            default_text_options=[
                TextFormat.Color.DARKGRAY,
                TextFormat.Style.ITALIC
            ],
            additional_text_options=text_options
    )

# message indicating an error
def error(*text: str | object, text_min_len: list[int] = [], text_options=[[]], blink=False) -> None:
    message(*text, 
            icon='-', 
            blink=blink,
            icon_options=[
                TextFormat.Color.RED
            ],
            text_min_len=text_min_len,
            default_text_options=[
                TextFormat.Color.RED
            ],
            additional_text_options=text_options
    )

# message indicating a critical error. The program terminates after showing this message
def critical_error(*text: str | object, text_min_len: list[int] = [], blink=False, exit_code=1) -> None:
    message(*text, 
            icon='x', 
            blink=blink,
            icon_options=[
                TextFormat.Color.RED
            ],
            text_min_len=text_min_len,
            default_text_options=[
                TextFormat.Color.RED
            ]
    )

    _sys.exit(exit_code)

# message indicating a warning
def warning(*text: str | object, text_min_len: list[int] = [], text_options=[[]], blink=False) -> None:
    message(*text, 
            icon='!', 
            blink=blink,
            icon_options=[
                TextFormat.Color.YELLOW
            ],
            text_min_len=text_min_len,
            default_text_options=[
                TextFormat.Color.YELLOW
            ]
    )

# message indicating a successfully completed action
def success(*text: str | object, text_min_len: list[int] = [], text_options=[[]], blink=False) -> None:
    message(*text, 
            icon='+', 
            blink=blink,
            icon_options=[
                TextFormat.Color.GREEN
            ],
            text_min_len=text_min_len,
            default_text_options=[TextFormat.Color.GREEN],
            additional_text_options=text_options
    )

# prints a question and returns the answer
def ask(question: str, end=': ') -> str:
    message(f'{question}{end}',
            icon='?',
            icon_options=[
                TextFormat.Color.PURPLE
            ],
            end='')
    
    return _input_colored(
        TextFormat.Style.ITALIC,
    )

# prints a question asking the user if they want to continue executing the program
# 	a positive answer makes the program continues its normal execution
# 	a negative answer terminates the program
# optionally supports a custom question
def ask_continue(text: str=None):
    if text is not None:
        message = f'{text}. Continue? (y/N)'
    else:
        message = 'Continue? (y/N)'

    while True:
        ans = ask(message, end=' ')

        if ans.lower() == 'y':
            break
        if ans.lower() == 'n' or len(ans) == 0:
            _sys.exit()