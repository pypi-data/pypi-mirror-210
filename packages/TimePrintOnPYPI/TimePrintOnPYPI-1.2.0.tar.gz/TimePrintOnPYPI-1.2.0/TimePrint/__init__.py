import time
import sys
def TP(saniye, metin):
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(int(saniye)/len(metin))
    print("")
def P(metin):
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
    print("Version: 1.2.0")
def timetag(format):
    return time.strftime(format, time.localtime())
