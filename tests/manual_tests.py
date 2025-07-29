import pocketwatch.core as core
from pocketwatch.core import Pocketwatch

def basic_test():
    pw=Pocketwatch()
    pw.mark('marked')
    pw.end()

def ding_test():
    pw=Pocketwatch(sound=True,sound_after=0,sound_file='ding.wav')
    pw.end()

if __name__ == "__main__":
    #basic_test()
    ding_test()