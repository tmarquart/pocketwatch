import time
from fileinput import filename

from src.pocketwatch import Pocketwatch

# --- Dummy workload
def load_data():
    time.sleep(0.2)
    return list(range(10000))

def transform_data(data):
    time.sleep(0.3)
    return [x * x for x in data if x % 2 == 0]

def summarize(data):
    time.sleep(0.2)
    return sum(data) / len(data)

def long_function():
    data = load_data()
    result = transform_data(data)
    avg = summarize(result)
    print(f"Average: {avg}")

def start_end_cprofile():
    filename="std_profile_output.prof"
    pw=Pocketwatch("Profiled job", profile=True, profile_output_path=filename)
    long_function()
    pw.end()
    print(f"terminal:  snakeviz tests/manual/{filename}")

# --- Main profiling block
def with_cprofile():
    filename="with_profile_output.prof"
    with Pocketwatch("Profiled job", profile=True, profile_output_path=filename):
        long_function()
    print(f"terminal:  snakeviz tests/manual/{filename}")

if __name__ == "__main__":
    #with_cprofile()
    start_end_cprofile()
