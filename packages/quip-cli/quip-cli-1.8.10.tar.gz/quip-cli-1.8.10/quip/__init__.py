from colorama import Fore, Style, init
init()

__version__ = "1.8.10"

def cprint(text, color, end='\n', style='Normal'):
    if len(str(text).strip()) == 0: return
    fore = getattr(Fore, color.upper())
    style = getattr(Style, style.upper())
    print('{0}{1}{2}{3}'.format(fore, style, text, Style.RESET_ALL), end=end)

def color_text(text, color, style='Normal'):
    fore = getattr(Fore, color.upper())
    style = getattr(Style, style.upper())
    return '{0}{1}{2}{3}'.format(fore, style, text, Style.RESET_ALL)

def yes_or_no(question, default=None, color=None):
    if default == True:
        options = "(Y/n)"
    elif default == False:
        options = "(y/N)"
    else:
        options = "(y/n)"
        default = None

    if color is not None:
        prompt = color_text(question + options + ": ", color)
    else:
        prompt = question + options + ": "
    while True:
        answer = input(prompt).lower().strip()
        
        if len(answer) == 0 and default is not None:
            return default
        elif answer[0] in  ["y", "yes"]:
            return True
        elif answer[0] in  ["n", "no"]:
            return False

def choose_one(values, title=None, default=None, sort=True):
    default_index = 1
    answer = None
    values = sorted(values, key=lambda d: d[0])

    if title is not None:
        cprint(title, "magenta")
        cprint("=" * len(title), "magenta")
    len_values = len(values)
    for index, value in enumerate(values, start=1):
        if default is not None and value[0] == default:
            print(f"({index}) {value[0]} [default]")
            default_index = index
        else:
            print(f"({index}) {value[0]}")

    ask = True
    while ask:
        if default is None:
            message = f"Choose one (1-{len_values}) : "
        else:
            message = f"Choose one (1-{len_values}) [{default_index}]: "
        
        answer = input(message).lower().strip()
        if len(answer) == 0 and default is not None:
            answer = default_index
        else:
            answer = int(answer)
        if answer < 1 or answer > len_values:
            cprint(f"answer must be between 1 and {len_values}", "red")
        else:
            ask = False
    
    return values[answer-1]