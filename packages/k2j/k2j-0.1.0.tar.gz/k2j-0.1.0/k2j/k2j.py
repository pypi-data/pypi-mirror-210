from dataclasses import dataclass
from functools import partial
from typing import Callable, List, Tuple, Union

from fugashi import UnidicNode, Tagger


@dataclass
class Rule:
    pattern: List[Union[Tuple[str, str], List[Tuple[str, str]]]]
    convert: Callable[[UnidicNode], str]

    @property
    def n_nodes(self) -> int:
        return len(self.pattern)


def transform_past_tense_godan(base: str) -> str:
    '''音便を変化させる
    '''
    tail = base[-1]
    # イ音便
    if base == '行く':
        return '行った'
    elif tail in ['く', 'ぐ']:
        return base[:-1] + 'いた'
    # 撥音便
    elif tail in ['ぬ', 'ぶ', 'む']:
        return base[:-1] + 'んだ'
    # 促音便
    elif tail in ['つ', 'る', 'う']:
        return base[:-1] + 'った'
    else:
        return base + 'た'


# 「自然な読み上げ音声出力のための書き言葉から話し言葉へのテキスト変換」を参考に規則を構築
# http://slp.itc.nagoya-u.ac.jp/web/papers/2007/hayashi_SLP66.pdf
rules = [
    # --- 5単語 ---
    # 14
    Rule(
        [[('orth', 'あり'), ('pos1', '動詞')], [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')], ('orth', 'でし'), ('orth', 'た')],
        lambda _: 'なかった'
    ),
    # 4
    Rule(
        [[('pos1', '動詞'), ('cForm', '連用形-一般')], [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')], ('orth', 'でし'), ('orth', 'た')],
        lambda nodes: nodes[0].surface + 'なかった'
    ),
    # 4'
    Rule(
        [('cType', '助動詞-レル'), [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')], ('orth', 'でし'), ('orth', 'た')],
        lambda nodes: nodes[0].surface + 'なかった'
    ),
    # --- 4単語 ---
    # 9
    Rule(
        [[('orth', 'の'), ('pos2', '準体助詞')], [('orth', 'でし'), ('cType', '助動詞-デス')], [('orth', 'た'), ('cType', '助動詞-タ')]],
        lambda _: 'のであった'
    ),
    # --- 3単語 ---
    # 7 (13): 3より先に書かないといけない
    Rule(
        [[('orth', 'あり'), ('pos1', '動詞')], [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')]],
        lambda _: 'ない'
    ),
    # 3
    Rule(
        [[('pos1', '動詞'), ('cForm', '連用形-一般')], [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')]],
        lambda nodes: nodes[0].surface + 'ない'
    ),
    # 3'
    Rule(
        [('cType', '助動詞-レル'), [('orth', 'ませ'), ('cType', '助動詞-マス')], [('orth', 'ん'), ('cType', '助動詞-ヌ')]],
        lambda nodes: nodes[0].surface + 'ない'
    ),
    # 2
    Rule(
        [('pos1', '動詞'), [('orth', 'まし'), ('cType', '助動詞-マス')], ('orth', 'た')],
        lambda nodes: transform_past_tense_godan(nodes[0].feature.orthBase) if nodes[0].feature.cType.startswith('五段') else nodes[0].surface + 'た'
    ),
    # 2'
    Rule(
        [('cType', '助動詞-レル'), [('orth', 'まし'), ('cType', '助動詞-マス')], ('orth', 'た')],
        lambda nodes: nodes[0].surface + 'た'
    ),
    Rule(
        [[('pos1', '形容詞')], [('orth', 'た'), ('cType', '助動詞-タ')], [('orth', 'です'), ('cType', '助動詞-デス')]],
        lambda nodes: nodes[0].surface + 'た'
    ),
    # --- 2単語 ---
    Rule(
        [('pos1', '形容詞'), [('orth', 'です'), ('cType', '助動詞-デス')]],
        lambda nodes: nodes[0].surface
    ),
    # 1
    Rule(
        [('pos1', '動詞'), [('orth', 'ます'), ('cType', '助動詞-マス')]],
        lambda nodes: nodes[0].feature.orthBase
    ),
    # 1'
    Rule(
        [('cType', '助動詞-レル'), [('orth', 'ます'), ('cType', '助動詞-マス')]],
        lambda nodes: nodes[0].feature.orth + 'る'
    ),
    # 6
    Rule(
        [[('orth', 'でし'), ('cType', '助動詞-デス')], [('orth', 'た'), ('cType', '助動詞-タ')]],
        lambda _: 'だった'
    ),
    # 11
    Rule(
        [[('orth', 'ない'), ('pos1', '形容詞')], [('orth', 'でしょう'), ('cType', '助動詞-デス')]],
        lambda _: 'ないだろう'
    ),
    # 12
    Rule(
        [[('orth', 'です'), ('cType', '助動詞-デス')], [('orth', 'が'), ('pos2', '接続助詞')]],
        lambda _: 'だが'
    ),
    # --- 1単語 ---
    # ８ (5)
    Rule(
        [[('cType', '助動詞-デス'), ('cForm', '終止形-一般')]],
        lambda _: 'である'
    ),
    # 10
    Rule(
        [[('orth', 'でしょう'), ('cType', '助動詞-デス')]],
        lambda _: 'であろう'
    ),
]


def build_next_node(nodes: List[UnidicNode]):
    def next_node(node: UnidicNode) -> UnidicNode:
        index = nodes.index(node)
        return nodes[index + 1] if index < len(nodes) - 1 else None
    return next_node


def match(node: UnidicNode, rule: Rule, next_node: Callable) -> bool:
    target_nodes = [node]
    _node = node

    # patten の検証に必要なノードを取得する
    for _ in range(rule.n_nodes - 1):
        _node = next_node(_node)

        # pattern のノード数に満たない場合は比較の必要がない
        if _node is None:
            return False

        target_nodes.append(_node)

    # 比較検証する
    for n, pat in zip(target_nodes, rule.pattern):
        if type(pat) is list:
            for key, value in pat:
                if getattr(n.feature, key) != value:
                    return False
        else:
            key, value = pat
            if getattr(n.feature, key) != value:
                return False

    return True


tagger = Tagger()


def k2j(text: str) -> str:
    nodes = tagger(text)
    next_node = build_next_node(nodes)
    matches_rule = partial(match, next_node=next_node)

    converted_text = ''

    i = 0
    while i < len(nodes):
        node = nodes[i]

        for rule in rules:
            # マッチした場合は、変換後のテキストを使う
            if matches_rule(node, rule):
                # FIXME ここ matches_rule() でも同じことをやっているので冗長
                target_nodes = [node]
                _node = node
                for _ in range(rule.n_nodes):
                    _node = next_node(_node)
                    target_nodes.append(_node)
                # MEMO マッチした単語列の先頭のみ white space を維持する。先頭以外の white space は欠落する
                converted_text += node.white_space + rule.convert(target_nodes)
                i += rule.n_nodes
                break

        # マッチしなかった場合は node の表層系をそのまま使う
        else:
            converted_text += node.white_space + node.surface
            i += 1

    return converted_text
