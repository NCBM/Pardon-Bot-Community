import ctypes
import os
import re
import subprocess

QalcExchangeRatesUpdater = ctypes.cdll.LoadLibrary(
    os.path.join("/".join(__name__.split("."))
                 if __name__ != "__main__" else ".",
                 "qalc-update-exchange-rates.so")
)

qalc_update_exchange_rates = QalcExchangeRatesUpdater._Z20update_exchange_ratev


_fchs_conv = [
    [r"小?时", r"h"], [r"(分钟?|mi?n?)", r"min"], [r"秒钟?", r"s"], [r"[天日]", r"d"],
]  # 字符转换映射关系


def time2sec(time: str) -> int:
    """Convert time to second(s)."""
    time_s = time
    for src, dst in _fchs_conv:
        # 逐步替换
        time_s = re.sub(src, dst, time_s)
    proc = subprocess.run(["qalc", "%s to s" % time_s], capture_output=True)
    time_po = proc.stdout.decode()
    time_po = time_po[time_po.rfind("=") + 1:time_po.rfind("s")].strip()
    return int(float(time_po))


def ftouch(fp: str):
    subprocess.run(["touch", fp])


def fgetmtime(fp: str):
    return os.path.getmtime(fp)
