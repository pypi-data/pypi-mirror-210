#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from timeit import default_timer

import cn2int as c2i


def performance_int2chinese(number):
    last = default_timer()
    for i in range(int(1e5)):
        s = c2i.int2chinese(number,
                            lower=True,
                            enumeration=False,
                            use_liang=False,
                            use_simple_ten=False,
                            use_simple_zero_tail=False,
                            width=0)
    rate = int(1e5 / (default_timer() - last) / 1e3)
    print("%-16s: %4d k/s" % ("int2chinese", rate))


def performance_chinese2int(s):
    last = default_timer()
    for i in range(int(1e5)):
        number = c2i.chinese2int(s)
    rate = int(1e5 / (default_timer() - last) / 1e3)
    print("%-16s: %4d k/s" % ("chinese2int", rate))


def performance_chinese2float(s):
    last = default_timer()
    for i in range(int(1e5)):
        number = c2i.chinese2float(s)
    rate = int(1e5 / (default_timer() - last) / 1e3)
    print("%-16s: %4d k/s" % ("chinese2float", rate))


def performance():
    performance_int2chinese(218123456789)
    performance_chinese2int("二千一百八十一亿二千三百四十五万六千七百八十九")
    performance_chinese2float("四千五百六十七万八千九百八十二点七六五四三二")


if __name__ == "__main__":
    performance()
