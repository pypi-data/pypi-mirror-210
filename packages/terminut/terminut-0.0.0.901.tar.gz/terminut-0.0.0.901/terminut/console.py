from colorama import Fore, Style
from datetime import datetime
from time     import time
from re       import sub


class Settings:
    initialized = False
    debug = True 
    timestamp = True
    c_MAIN = Fore.LIGHTBLUE_EX
    c_SECO = Fore.LIGHTBLACK_EX


def init(
    debug: bool = True,
    showTimestamp: bool = True,
    colMain = Fore.LIGHTBLUE_EX,
    colSeco = Fore.LIGHTBLACK_EX,
    madeBy = "vast#1337"
):
    Settings.initialized = True
    Settings.debug = debug
    Settings.timestamp = showTimestamp
    Settings.c_MAIN = colMain
    Settings.c_SECO = colSeco


@staticmethod
def printf(content: str, mainCol=None, showTimestamp=None):
    """
    Print the content with optional colored text and timestamp.

    Args:
        content (str): The content to print.
         mainCol (str, optional): The main color of the prefix. Default is Settings.MAINCOLOR (LIGHTBLUE).
        showTimestamp (bool, optional): Whether to show the timestamp. Default is True (show timestamp).
    """
    if showTimestamp is None: showTimestamp = Settings.timestamp
    if mainCol is None: mainCol = Settings.c_MAIN
    if type(content) != str: return print(content)
    if (
        ("(!)" in content)
        or ("(-)" in content)
        or ("(~)" in content) 
        or ("debug" in content.lower())
        ) and (Settings.debug == False): return
    
    timestamp = f'{Settings.c_SECO}{datetime.fromtimestamp(time()).strftime("%H:%M:%S")}{Fore.RESET} ' if (showTimestamp) else ''
    
    content   = sub(r'\[(.*?)]', rf'{Settings.c_SECO}[{mainCol}\1{Settings.c_SECO}]{Fore.RESET}', content)
    content   = content\
        .replace("|", f"{Settings.c_SECO}|{mainCol}")\
        .replace("->", f"{Settings.c_SECO}->{mainCol}")\
        .replace("(+)", f"{Settings.c_SECO}({Fore.GREEN}+{Settings.c_SECO}){mainCol}")\
        .replace("($)", f"{Settings.c_SECO}({Fore.GREEN}${Settings.c_SECO}){mainCol}")\
        .replace("(-)", f"{Settings.c_SECO}({Fore.RED}-{Settings.c_SECO}){mainCol}")\
        .replace("(!)", f"{Settings.c_SECO}({Fore.RED}!{Settings.c_SECO}){mainCol}")\
        .replace("(~)", f"{Settings.c_SECO}({Fore.YELLOW}~{Settings.c_SECO}){mainCol}")\
        .replace("(#)", f"{Settings.c_SECO}({Fore.BLUE}#{Settings.c_SECO}){mainCol}")\
        .replace("(*)", f"{Settings.c_SECO}({Fore.CYAN}*{Settings.c_SECO}){mainCol}")
    
        # .replace("(", f"{Settings.c_SECO}({Fore.RESET}").replace(")", f"{Settings.c_SECO}){Fore.RESET}")
        # .replace("[", f"{Settings.c_SECO}[{mainCol}")\
        
    return print(timestamp + content, end=f"{Fore.RESET}\n")
    
    
@staticmethod
def inputf(content: str):
    if "(?)" not in content: x = f"{Settings.c_SECO}({Settings.c_MAIN}?{Settings.c_SECO}){Fore.RESET} "
    else: x = ""
    content = x + content\
        .replace("(", f"{Settings.c_SECO}({Settings.c_MAIN}").replace(")", f"{Settings.c_SECO}){Settings.c_MAIN}")\
        .replace(">", f"{Settings.c_SECO}>{Fore.RESET}")
    return input(content)