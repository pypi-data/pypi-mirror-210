import time
import sys
def TP(seconds: int, text: str):
    """
    Usage;

    TimePrint.TP(seconds,"text")

    Example: TimePrint.TP(1,"Hello")
    Writes Hello In 1 Seconds

    """
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(int(seconds)/len(text))
    print("")
def P(text:str):
    """
    Usage;
    TimePrint.P("text")
    Example TimePrint.P("Hello") writes
    Hello in 0.001 seconds
    You can use this for just
    write effect.
    
    """
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.001)
    print("")    
def info():
    print("      _______ _____ __  __ ______     _____  _____  _____ _   _ _______  ")
    print("     |__   __|_   _|  \/  |  ____|   |  __ \|  __ \|_   _| \ | |__   __| ")
    print("        | |    | | | \  / | |__      | |__) | |__) | | | |  \| |  | |   ")
    print("        | |    | | | |\/| |  __|     |  ___/|  _  /  | | | . ` |  | |   ")
    print("        | |   _| |_| |  | | |____    | |    | | \ \ _| |_| |\  |  | |   ")
    print("        |_|  |_____|_|  |_|______|   |_|    |_|  \_\_____|_| \_|  |_|   ")
    print("\nAuthor: Osman TUNA")
    print("Author Email: osmntn08@gmail.com")
    print("Project Page: https://github.com/SForces/TimePrint")
    print("Version: 1.5.1")
def Timetag(format: str):
    """
    Example Usages;

    "%H:%M" Returns --> 12:56 = (Hours:Minutes)
    "%H:%M:%S" Returns --> 12:56:24 = (Hours:Minutes:Seconds)
    "%d.%m.%y" Returns --> 10.02.2023 = (Day.Month.Year)

    using strftime from time
    """
    return time.strftime(format, time.localtime())
