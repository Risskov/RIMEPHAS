import datetime as dt

def logging(file, string):
    with open(f"testing/{file}", "a+") as logfile:
        timestamp = dt.datetime.now()
        logfile.write(f"{timestamp}: {string}\n")
