import time, sys

def sprint(typetext):
    for char in typetext:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.1)
    print("\n")

def cprint(typetext, ms):
    for char in typetext:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(ms / 1000)
    print("\n")

def NoNsprint(typetext):
    for char in typetext:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.1)

def NoNcprint(typetext, ms):
    for char in typetext:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(ms / 1000)