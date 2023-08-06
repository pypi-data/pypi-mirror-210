import os, typing

AnswerList = type("AnswerList", (), {})

def funkyInput(ask_value: str | int | bool, defaultVal: None | str = None) -> AnswerList:
    """Adds A ```Funky``` Input"""
    val = str(ask_value) if type(ask_value) == int else ask_value
    deval = " ()" if not defaultVal and not defaultVal == False else f" ({defaultVal})"
    os.system('cls')
    asky = input(f"{val}{deval}: ")
    if not defaultVal and not defaultVal == False:
        if asky == "":
            os.system('cls')
            print(f"{val}\x1b[34m{str(deval)}\x1b[39m")
            return ["", type("")]
    else:
        if asky == "":
            os.system('cls')
            print(f"{val}\x1b[34m{str(deval)}\x1b[39m")
            return [defaultVal, type(defaultVal)]
    if not asky == "":
        os.system('cls')
        print(f'{val}\x1b[34m ({asky})\x1b[39m')
        try:
            integered = int(asky)
            return [integered, type(integered)]
        except ValueError:
            return [asky, type(asky)]