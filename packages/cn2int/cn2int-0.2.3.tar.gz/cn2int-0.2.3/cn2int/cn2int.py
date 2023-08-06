#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""阿拉伯数字、罗马数字、中文数字字符串 和 整数的相互转换.

Author: suhecheng
Home: https://github/citysu/cn2int
"""

import re


__version__ = "0.2.3"


__all__ = [
    "int2roman", "roman2int",
    "int2chinese", "float2chinese", "chinese2int", "chinese2float"
    "convert2int"
]


re_dot = re.compile(r"[点點]")


class Table:
    roman2int = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    int2roman =  [["", "I", "II", "III", "IV", "V", "VI", "VII","VIII", "IX"],
                  ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"],
                  ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"],
                  ["", "M", "MM", "MMM"]]

    lower_enumeration = "〇一二三四五六七八九负"
    lower_traditional = "零一二三四五六七八九负"
    lower_uint = ["", "十", "百", "千"]
    lower_delimiter = ["", "万", "亿"]

    upper_enumeration = "零壹贰叁肆伍陆柒捌玖負"
    upper_traditional = "零壹贰叁肆伍陆柒捌玖負"
    upper_unit = ["", "拾", "佰", "仟"]
    upper_delimiter = ["", "萬", "億"]

    chinese2int = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
                   "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
                   "十": 10, "百": 100, "千": 1000, "万": 10000,
                   "亿": 100000000,
                   "零": 0, "壹": 1, "贰": 2, "叁": 3, "肆": 4,
                   "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9,
                   "拾": 10, "佰": 100, "仟": 1000, "萬": 10000,
                   "億": 100000000,
                   "０": 0, "１": 1, "２": 2, "３": 3, "４": 4,
                   "５": 5, "６": 6, "７": 7, "８": 8, "９": 9,
                   "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
                   "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
                   "两": 2,
                   "正": -10, "负": -1, "負": -1, "点": -100, "點": -100}
    levels = [10**i for i in range(13)]


# 罗马数字


def int2roman(number):
    """整数 => 罗马数字.

    参数:
        number (int): 正整数. 取值范围: (0, 4000)

    返回:
        string: 罗马数字. 如果返回None, 表示超出转换范围.
    """
    if number <= 0 or number >= 4000:
        return None
    
    n, s = number, ""
    i = 0

    while n > 0:
        p = n % 10
        n //= 10
        s = Table.int2roman[i][p] + s
        i += 1
    return s


def roman2int(s):
    """罗马数字 => 整数
    
    参数:
        s (string): 罗马数字, 忽略大小写. 符合正则模式: "[IVXLCDM]+".
    
    返回:
        int: 正整数. 取值范围: (0, 4000).
    """
    number, s = 0, s.upper()
    length = len(s)

    for i in range(length - 1):
        p = Table.roman2int[s[i]]
        p_next = Table.roman2int[s[i+1]]
        number += -p if p < p_next else p
    number += Table.roman2int[s[length-1]]
    if s != int2roman(number):
        raise ValueError("invalid Roman numerals")
    return number


# 中文数字


def chinese2int_enumeration(s):
    """中文数字(枚举表示) => 非负整数

    参数:
        s (string): 中文数字. 符合正则模式: "[〇一二三四五六七八九十百千万亿
            零壹贰叁肆伍陆柒捌玖拾佰仟萬億两]+"

    返回:
        int: 整数. 取值范围: [0, 1e12).
    """
    number = 0
    length = len(s)
    i = 0
    m = 1

    while length > 0:
        length -= 1
        p = Table.chinese2int[s[length]]

        # 枚举表示 下不能出现大于9的单个数字.
        if p > 9:
            raise ValueError("invalid Chinese numerals")

        number += p * m

        # 范围限制
        if i == 11 and len(s[:length].lstrip("零〇")) > 0:
            raise OverflowError("the value is out of the supported range")
        m *= 10
        i += 1

    return number


def chinese2int_traditional(s):
    """中文数字(传统表示) => 非负整数

    参数:
        s (string): 中文数字. 符合正则模式: "[〇一二三四五六七八九十百千万亿
            零壹贰叁肆伍陆柒捌玖拾佰仟萬億两]+"

    返回:
        int: 整数. 取值范围: [0, 1e12).
    """
    number = 0
    length = len(s)

    # 以"万亿萬億"作为分割符, 得到的每段中文数字子字符串为"X千X百X十X "的模式, 该子串对应
    # 的整数为small.
    small = 0

    # 中文数字子字符串按每两个字符进行分组"(X千)(X百)(X十)(X一)". 组内模式为(a, b),
    # a为数字(0-9), b为权值(一十百千).
    a, b = 0, 1

    # tiny是一个临时值, 当tiny = a * b时, 它始终比旧的small多一位数字. 该现象可确保
    # "千百十"出现的顺序正确.
    tiny = 0

    # 两个flag分别对应a, b. 逆序遍历中文数字字符串时, b, a应交替出现. 用flag判断是否
    # 连续出现a或连续出现b. 连续的a或b, 意味着中文数字字符串格式非法. 例如"三百二二",
    # "三千百".
    flag_pair_a, flag_pair_b = False, False

    # 表示中文数字字符串中, 分隔符"亿万一"对应的整数.
    delimiter = 1

    # use_simple_zero_tail: 计算出省略的单位.
    p = 0
    if length > 1:
        p = Table.chinese2int[s[length - 2]]
    if p > 10:
        a = Table.chinese2int[s[length - 1]]
        # 排除 "一百万", "二千亿"这种情况
        if a < 10:
            b = p // 10
            small += a * b
            length -= 1

    while length > 0:
        length -= 1
        p = Table.chinese2int[s[length]]

        if p == 0:
            continue

        if p < 10:
            if flag_pair_a is False:
                a = p
                tiny = a * b
                if tiny > small:
                    small += tiny
                else:
                    # "千百十"顺序出错, e.g. 五百六千
                    raise ValueError("invalid Chinese numerals")
                flag_pair_a = True
            else:
                # 出现连续的a(数字).
                raise ValueError("invalid Chinese numerals")
            flag_pair_b = False
        else:
            if p == 10000 or p == 100000000:
                if flag_pair_b is False:
                    number += small * delimiter
                    small = 0
                    a, b = 0, 1

                    # 万万为亿. e,g 六万万.
                    if p == 10000 and Table.chinese2int[s[length - 1]] == 10000:
                        p = 100000000
                        length -= 1

                    # 新的delimiter始终大于旧的delimiter, 确保"亿"在"万"前.
                    if p > delimiter:
                        delimiter = p
                    else:
                        if delimiter == 100000000:
                            # e.g. 三万亿, 六亿亿, 六千万五亿
                            raise OverflowError("the value is out of the supported range")
                        # 此时必定: p=10000, delimiter=10000. 针对"四万五千万"的情形.
                        delimiter = 100000000
                else:
                    # 出现万千, 万百, 万十 .etc.
                    raise ValueError("invalid Chinese numerals")    
            else:
                if flag_pair_b is False:
                    if p <= b:
                        # e.g 七千一千零一十万
                        raise ValueError("invalid Chinese numerals")
                    b = p
                    flag_pair_b = True
                else:
                    # 出现连续的b(权值).
                    raise ValueError("invalid Chinese numerals")
            flag_pair_a = False

    # use_simple_ten: "十"开头的中文数字字符串, 逆序遍历到开头的"十"
    # 后, 会终止循环, 导致"十"无法参与到small的计算中, 所以需要修正下.
    if p == 10:
        small += 10

    number += small * delimiter
    return number


def chinese2int(s):
    """中文数字 => 整数.

    参数:
        s (string): 中文数字. 符合正则模式: "[正负負]?[〇一二三四五六七八九十百千万亿
            零壹贰叁肆伍陆柒捌玖拾佰仟萬億两]+"

    返回:
        int: 整数. 取值范围: (-1e12, 1e12).
    """
    number = 0
    sign = 1

    if len(s) >= 2:
        a, b = Table.chinese2int[s[0]], Table.chinese2int[s[1]]
        # 第一个字符不能是"百千万亿佰仟萬億"
        if a > 10:
            raise ValueError("invalid Chinese numerals")
        if a == -10:
            s = s[1:]
        if a == -1:
            s = s[1:]
            sign = -1
        if max(a, b) <= 9:
            try:
                number = chinese2int_enumeration(s)
            except ValueError:
                # "零零零三百六十一"会被错误的判定为枚举表示. (s.lstrip("零〇")
                # 不可行, e.g. "零三零百六十" => "三零百六十")
                number = chinese2int_traditional(s)
        else:
            number = chinese2int_traditional(s)
        number *= sign
    else:
        number = Table.chinese2int[s]
    return number


def chinese2float(s):
    """中文数字 => 浮点数
    
    参数:
        s (string): 中文数字. 符合正则模式: "[正负負]?[〇一二三四五六七八九十百千万亿
            零壹贰叁肆伍陆柒捌玖拾佰仟萬億两点點]+"

    返回:
        float: 浮点数. 取值范围: (-1e12, 1e12).
    """
    p = Table.chinese2int[s[0]]
    signed = 1
    if p == -10:
        s = s[1:]
    if p == -1:
        s = s[1:]
        signed = -1

    number = 0
    tail = 1
    s_original = s

    # "六点三万人", "五点八亿斤"
    p = Table.chinese2int.get(s[-1])
    if p and p > 1000:
        tail = p
        s = s[:-1]

    parts = re_dot.split(s)
    count = len(parts)

    if count == 1:
        number = chinese2int(s_original) * 1.0
    elif count == 2:
        a_length = len(parts[0])
        b_length = len(parts[1])
        # 整数部分
        if a_length == 0:
            raise ValueError("invalid Chinese numerals")
        else:
            a = chinese2int_traditional(parts[0])
        # 小数部分
        if b_length == 0:
            raise ValueError("invalid Chinese numerals")
        else:
            b = chinese2int_enumeration(parts[1])
        number = a + b / Table.levels[b_length]
        number *= tail
    else:
        raise ValueError("invalid Chinese numerals")

    number *= signed
    return number


def chinese_fill_zero(s, small):
    if small == 0:
        if s != "" and s[0] != "零":
            s = "零" + s
    else:
        if small < 1000:
            s = "零" + s
    return s


def chinese_simple_ten(s, small):
    if small < 20 and small >= 10:
        s = s.lstrip("一壹")
    return s


def chinese_simple_zero_tail(s, lower):
    if len(s) >= 3 and s[-3] != "零":
        s = s.rstrip("十百千拾佰仟")
    if s.endswith("两"):
        s = s[:-1] + "二" if lower else "贰"
    return s


def small2chinese(number, delimiter, digits, units, use_liang):
    n, s = number, ""
    i = 0

    while n > 0:
        p = n % 10
        n //= 10
        if p == 0:
            if s != "" and s[0] != "零":
                s = "零" + s
        else:
            if use_liang and ((p == 2 and i > 1) or (number == 2 and delimiter != "")):
                s = "两" + units[i] + s
            else:
                s = digits[p] + units[i] + s
        i += 1
    return s


def int2chinese(number, lower=True, enumeration=False,
                use_liang=False,
                use_simple_ten=False,
                use_simple_zero_tail=False,
                use_upper_zero=False,
                width=0):
    """整数 => 中文数字.
 
    参数:
        number (int): 整数. 取值范围: (-1e12, 1e12)
        lower (bool): 是否使用小写中文数字. 默认Ture.
        enumeration (bool): 是否使用枚举表示. 枚举表示: 第一二三章,
            传统表示: 第一百二十三章. 默认False.
        use_upper_zero (bool): 枚举表示时, 是否用"零"替代"〇", 默认False.
        width (int): 中文数字的最小字符数, 不足宽度的左侧补零.

        (以下参数只在enumeration=False时生效)

        use_liang (bool): 是否用"两"替代、并尽可能多地替代"二". 默认False.
        use_simple_ten (bool): 以"一十"开头的的中文数字, 是否省略"一". 默认False.
        use_simple_zero_tail (bool): 整数以`xx000, xx00, xx0`结尾时, 是否省略
            中文数字末尾的"十百千". 其中`x`是非零数字.

    返回:
        string: 中文数字. 如果返回None, 表示超出转换范围.
    """
    if number <= -1e12 or number >= 1e12:
        return None

    n, s = number, ""
    sign = ""
    i = 0

    if enumeration:
        if lower:
            if use_upper_zero:
                digits = Table.lower_traditional
            else:
                digits = Table.lower_enumeration
        else:
            digits = Table.upper_enumeration
        if n < 0:
            sign = digits[-1]
            n = -n
        if n == 0:
            s = digits[0]
        while n > 0:
            p = n % 10
            n //= 10
            s = digits[p] + s
            i += 1
        if len(s) < width:
            s = digits[0] * (width - len(s)) + s
    else:
        if lower:
            digits = Table.lower_traditional
            units = Table.lower_uint
            delimiters = Table.lower_delimiter
        else:
            digits = Table.upper_traditional
            units = Table.upper_unit
            delimiters = Table.upper_delimiter
        if n < 0:
            sign = digits[-1]
            n = -n
        if n == 0:
            s = digits[0]
        while n > 0:
            p = n % 10000
            n //= 10000
            delimiter = delimiters[0] if p == 0 else delimiters[i]
            s_small = small2chinese(p, delimiter, digits, units, use_liang)
            s = s_small + delimiter + s
            if n != 0:
                s = chinese_fill_zero(s, p)
            i += 1
        if use_simple_ten:
            s = chinese_simple_ten(s, p)
        if use_simple_zero_tail:
            s = chinese_simple_zero_tail(s, lower)
        if len(s) < width:
            s = digits[0] * (width - len(s)) + s
    s = sign + s
    return s


def float2chinese(number, lower=True, precision=6,
                  use_liang=False,
                  use_simple_ten=False,
                  use_simple_zero_tail=False):
    """浮点数 => 中文数字.

    参数:
        number (float): 浮点数. 取值范围: (-1e12, 1e12)
        lower (bool): 是否使用小写中文数字. 默认Ture.

        precision (int): 浮点数精度/小数点后的位数. 取值范围: [0, 12].

        use_liang (bool): 是否用"两"替代、并尽可能多地替代"二". 默认False.
        use_simple_ten (bool): 以"一十"开头的的中文数字, 是否省略"一". 默认False.
        use_simple_zero_tail (bool): 整数部分以`xx000, xx00, xx0`结尾时, 是否省略
            中文数字整数部分末尾的"十百千". 其中`x`是非零数字.

    返回:
        string: 中文数字. 如果返回None, 表示超出转换范围.
    """
    if number <= -1e12 or number >= 1e12:
        return None
    precision = max(min(precision, 12), 0)
    level = Table.levels[precision]

    n, s = number, ""
    sign = 1

    if n < 0:
        n = -n
        sign = -1

    a = int(n)
    n -= a
    n *= level
    b = int(n)
    n -= b
    n *= 10
    if (n - int(n)) * 10 > 5:
        n += 1
    if n >= 5:
        b += 1
        if int(b / level) == 1:
            a += 1
            b = 0
    a *= sign

    s_a = int2chinese(a, lower, False,
                      use_liang=use_liang,
                      use_simple_ten=use_simple_ten,
                      use_simple_zero_tail=use_simple_zero_tail)
    s_b = int2chinese(b, lower, True,
                      use_upper_zero=True,
                      width=precision)

    if lower:
        dot = "点"
    else:
        dot = "點"
    
    s = s_a + dot + s_b
    return s


# 数字


def convert2int(s):
    """数字 => 整数

    参数:
        s (string): 数字字符串. 必须是: 阿拉伯数字, 罗马数字, 或中文数字中的
            一种. 不支持、不检测如"12万"这样的数字.
    返回:
        int: 整数.
    """
    number = 0
    code = ord(s[0])
    # "0-9": [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    # "+-": [43, 45]
    if code <= 57:
        number = int(s)
    # "IVXLCDM": [73, 86, 88, 76, 67, 68, 77]
    elif code <= 88:
        number = roman2int(s)
    # "〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億":
    # [12295, 19968, 20108, 19977, 22235, 20116, 20845, 19971, 20843,
    #  20061, 21313, 30334, 21315, 19975, 20159, 38646, 22777, 36144,
    #  21441, 32902, 20237, 38470, 26578, 25420, 29590, 25342, 20336,
    #  20191, 33836, 20740]
    # "正负負":
    # [27491, 36127, 36000]
    else:
        number = chinese2int(s)
    return number
