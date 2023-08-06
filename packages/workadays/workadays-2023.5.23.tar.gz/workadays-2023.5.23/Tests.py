# from workadays import workdays_tests as wdt


# wdt.exec_tests()


# Testes de performance

import datetime as dt
from workadays import workdays as wd
import time


def performance_test():
    date = dt.date(2020, 12, 25)
    iterations = 10000

    start_time = time.time()
    dt_zero = wd.workdays(date, 0)
    for i in range(iterations):
        dt_zero = wd.workdays(date, i)
    print(dt_zero)
    end_time = time.time()
    print(f"Execution time for {iterations} iterations of wd.workdays(date, 0): {(end_time - start_time) / 60} minutes")


if __name__ == "__main__":
    performance_test()
