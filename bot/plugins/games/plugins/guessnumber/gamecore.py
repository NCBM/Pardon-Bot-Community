#!/usr/bin/env python3
from dataclasses import dataclass
from random import randint
from typing import Optional, Union


@dataclass
class GStat:
    same: int
    inbit: int

    def __str__(self):
        return "%dA%dB" % (self.same, self.inbit)


class GNum:
    def __init__(self, source: Union[int, list[int]]):
        if isinstance(source, list):
            self._bits = source
        else:
            self._bits = GNum._num2GNum(source)._bits
        if self.is_valid():
            return
        raise ValueError("Invalid number.")

    def __repr__(self):
        return "GNum(%d%d%d%d)" % tuple(self._bits)

    def __int__(self):
        return int("%d%d%d%d" % tuple(self._bits))

    @staticmethod
    def _split_digit_int(num: int) -> list[int]:
        if num < 10:
            return [num]
        bits = list[int]()
        base = 1
        while num % base != num:
            bits.insert(0, num // base % 10)
            base *= 10
        return bits

    @staticmethod
    def _num2GNum(num: int):
        if 1023 <= num <= 9876:
            return GNum(GNum._split_digit_int(num))
        raise ValueError("Invalid number.")

    def is_valid(self):
        return self._bits[0] and len(set(self._bits)) == 4

    def _test_a(self, num: "GNum"):
        count = 0
        for i in range(4):
            if self._bits[i] == num._bits[i]:
                count += 1
        return count

    def _pre_test_b(self, num: "GNum"):
        count = 0
        for ch in num._bits:
            if ch in self._bits:
                count += 1
        return count

    def test(self, num: "GNum"):
        if not num.is_valid():
            raise AttributeError("Invalid GNum %s" % GNum)
        a = self._test_a(num)
        pb = self._pre_test_b(num)
        return GStat(a, pb - a)


def gen_num():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    bits = [0, 0, 0, 0]
    bits[0] = nums.pop(randint(0, 8))
    bits[1] = nums.pop(randint(0, 8))
    bits[2] = nums.pop(randint(0, 7))
    bits[3] = nums.pop(randint(0, 6))
    num = GNum(bits)
    return num


def input_s(prompt: Optional[str] = None) -> str:
    if prompt is None:
        prompt = ""
    try:
        return input(prompt)
    except EOFError:
        exit(0)
    except KeyboardInterrupt:
        exit(130)


if __name__ == "__main__":
    print(
        "Would you like to generate a random number or specify a number? "
        "(R/s)", end=" "
    )
    while True:
        cmd = input_s()
        if cmd.capitalize() == "R" or not cmd:
            base = gen_num()
            print("A random number is generated. Now try to guess it!")
            break
        elif cmd.capitalize() == "S":
            input_d = input_s("Please input a number (1023-9876): ")
            base = GNum(int(input_d))
            if base.is_valid():
                break
            else:
                print("Invalid number.")
    while True:
        ins = input_s(">>> ")
        try:
            inn = GNum(int(ins))
            stat = base.test(inn)
            print(str(stat))
            if stat.same == 4:
                print("Congratulation!")
                exit(0)
        except KeyboardInterrupt:
            exit(130)
        except (TypeError, AttributeError, ValueError):
            print("Invalid input.")
