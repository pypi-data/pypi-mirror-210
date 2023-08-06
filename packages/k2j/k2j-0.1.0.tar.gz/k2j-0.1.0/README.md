# k2j

**k**eitai **to** **j**otai.

This is a library for converting Japanese sentences from a polite form (Keitai; 敬体) into a plain one (Jotai; 常体).

## Installation

```sh
pip install git+ssh://git@github.com/Office-asoT/k2j.git
pip install "fugashi[unidic]"   # k2j requires fugashi + unidic.
python -m unidic download
```

## Usage

```python
from k2j import k2j

k2j('今日はいい天気です。')     # => '今日はいい天気である。'
```

## Note

This library is a work in progress, so it may not be able to perform appropriate conversions for all text.

## References

* 林由紀子, 松原茂樹: 自然な読み上げ音声出力のための書き言葉から話し言葉へのテキスト変換, 情報処理学会研究報告音声言語情報処理, Vol.47, pp.49-54 ([PDF](http://slp.itc.nagoya-u.ac.jp/web/papers/2007/hayashi_SLP66.pdf))
