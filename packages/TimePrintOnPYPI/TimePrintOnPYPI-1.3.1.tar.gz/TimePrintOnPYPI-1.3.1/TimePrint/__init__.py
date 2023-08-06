import time
import sys
def TP(saniye: int, metin: str):
    """
    Usage;
    TimePrint.TP(seconds,"text")
    Example TimePrint.TP(1,"Hello") 
    Writes Hello In 1 Seconds

    """
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(int(saniye)/len(metin))
    print("")
def P(metin:str):
    """
    Usage;
    TimePrint.P("text")
    Example TimePrint.P("Hello") writes
    Hello in 0.001 seconds
    You can use this for just
    write effect.
    
    """
    for karakter in metin:
        sys.stdout.write(karakter)
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
    print("Version: 1.3.1")
def timetag(format: str):
    """
    Example Usages;

    "%H:%M" Returns --> 12:56 = (Hours:Minutes)
    "%H:%M:%S" Returns --> 12:56:24 = (Hours:Minutes:Seconds)
    "%d.%m.%y" Returns --> 10.02.2023 = (Day.Month.Year)

    """
    return time.strftime(format, time.localtime())
