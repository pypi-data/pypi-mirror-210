# cn2int: Chinese Numerals To Int/Float

- Conversion bettwen Chinese numerals and integer/float.
- Conversion bettwen Roman numerals and integer.

cn2int does the format checking during conversion, it can raise `ValueError`, `OverflowError` and `KeyError`. Before doing conversion, you should ensure the following patterns are met.

- `roman2int`: "[IVXLCDM]+"
- `chinese2int`: "[正负負]?[〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億两]+"
- `chinese2float`: "[正负負]?[〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億两点點]+"

## Usage

```python
import cn2int as c2i

# chinese/roman/arab => integer
c2i.convert2int("两亿零六千五")

# chinese => integer
c2i.chinese2int("二十三亿零六百三十万零七十八")

# chinese => float
c2i.chinese2float("二千三百零六万三千点七八")

# integer => chinese
c2i.int2chinese(2306300078)

# float => chinese
c2i.float2chinese(23063000.78)

# rooman => integer
c2i.roman2int("XVI")

# integer => rooman
c2i.int2roman(16)

# performance
c2i.performance()
```
