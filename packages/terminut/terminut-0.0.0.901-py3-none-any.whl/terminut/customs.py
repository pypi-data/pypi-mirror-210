from colorama import Fore, Style
from datetime import datetime
from time     import time
from re       import sub
from colorsys import hsv_to_rgb
from typing   import Dict
from shutil   import get_terminal_size

from .console import Settings


class Console:
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




class BetaConsole:
    def __init__(self, speed: int = 2, showMS: int = 4):
        self.colHue = 120
        self.speed = speed
        self.direction = self.speed
        self.showMS = showMS
        self.extraSpace = 0
        self.incrementing = True

    def getTimestamp(self, type: int = 1) -> str:
        """
        Get a timestamp with a colored representation based on the given type.

        Args:
            type (int): The color type. Default is 1 (RAINBOW).

        Returns:
            str: The colored timestamp string.

        Raises:
            ValueError: If the type is not in the valid range (1-4).
            
        Types:
            1: "RAINBOW"\n
            2: "GREEN_TO_BLUE"\n
            3: "RED_TO_YELLOW"\n
            4: "BLUE_TO_PURPLE"\n
        """

        types: Dict[int, str] = {
            1: "RAINBOW",
            2: "GREEN_TO_BLUE",
            3: "RED_TO_YELLOW",
            4: "BLUE_TO_PURPLE"
        }
        if type not in types:
            raise ValueError("Types must be in range (1,4).")

        if type == 1:  # RAINBOW
            first_Color = 360
            second_Color = 0
        elif type == 2:  # GREEN_TO_BLUE
            first_Color = 240
            second_Color = 120
        elif type == 3:  # RED_TO_YELLOW
            first_Color = 60
            second_Color = 0
        elif type == 4:  # BLUE_TO_PURPLE
            first_Color = 300
            second_Color = 240
        
        rgb = hsv_to_rgb(self.colHue / 360, 1, 1)
        red = int(rgb[0] * 255)
        green = int(rgb[1] * 255)
        blue = int(rgb[2] * 255)

        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-self.showMS]
        timestamp = f"\033[38;2;{red};{green};{blue}m{current_time}\033[0m"

        self.colHue += self.direction
        if self.colHue >= first_Color:
            self.direction = -self.speed
        elif self.colHue <= second_Color:
            self.direction = self.speed

        return timestamp

    def alphaPrint(self, type, text, increment:bool=False):
        if increment:
            if self.extraSpace == 0: self.incrementing = True
            elif self.extraSpace == 10: self.incrementing = False
            if self.incrementing: self.extraSpace += 1
            else: self.extraSpace -= 1

        console_width = get_terminal_size().columns

        other_len = 28 # avg of # len(text.split("\x1b[0m] ")[0])
        text_length = len(text.split("\x1b[0m] ")[1]) # keeps changing cuz of colors
        type_length = len(type)
        
        spaces = max(0, console_width - (text_length - type_length + other_len + self.extraSpace))
        
        if "err" in type.lower():
            form_color = Fore.RED
        elif "inf" in type.lower():
            form_color = Fore.LIGHTCYAN_EX
        else:
            form_color = Fore.GREEN
        formatted_info = type.replace("[", f"{Settings.c_SECO}[{form_color}").replace("]", f"{Settings.c_SECO}]{Style.RESET_ALL}")


        output = f"{text}{' ' * spaces}{formatted_info}"

        print(output)
        return