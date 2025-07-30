from src.pocketwatch import Pocketwatch
from src.pocketwatch.decorators import stopwatch

def basic_test():
    pw=Pocketwatch(log_mode='both')
    pw.mark('marked')
    pw.end()

def ding_test():
    pw=Pocketwatch(sound=True,sound_after=0,log_mode='both')
    pw.end()

def decorator_test():
    @stopwatch(log_mode='both')
    def fxn():
        print('decorator fxn')

    fxn()

def unexpected_test():
    pwx=Pocketwatch()

if __name__ == "__main__":
    basic_test()
    ding_test()
    decorator_test()
    unexpected_test()