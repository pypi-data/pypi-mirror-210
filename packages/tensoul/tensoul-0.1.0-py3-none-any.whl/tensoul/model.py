from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple, Union, Protocol, Optional, Sequence, runtime_checkable

from .cfg import cfg
from .constants import TSUMOGIRI, RUNES, JPNAME
from .utils import pad_list


class TileType(IntEnum):
    M = 0
    P = 1
    S = 2
    Z = 3


class Symbol(Protocol):
    def encode_tenhou(self) -> Union[int, str]:
        ...


class ZeroSymbol:
    def encode_tenhou(self) -> int:
        return 0


class Tile(NamedTuple):
    num: int
    type: TileType

    def encode_tenhou(self) -> int:
        """
        tenhou's tile encoding:
           11-19    - 1-9m
           21-29    - 1-9p
           31-39    - 1-9s
           41-47    - 1-7z
           51,52,53 - 0m, 0p, 0s
        """
        if self.num != 0:
            result = 10 * (self.type.value + 1) + self.num
        else:
            # aka
            result = 50 + (self.type.value + 1)

        return result

    @classmethod
    def parse(cls, text: str) -> "Tile":
        assert len(text) == 2
        return Tile(int(text[0]), TileType[text[1].upper()])

    def is_aka(self) -> bool:
        return self.num == 0 and self.type != TileType.Z

    def deaka(self) -> "Tile":
        """
        return normal tile from aka
        """
        if self.type != TileType.Z and self.num == 0:
            return Tile(5, self.type)
        return self


class DiscardSymbol(NamedTuple):
    tile: Tile
    tsumogiri: bool = False
    riichi_delcaration: bool = False

    def encode_tenhou(self) -> Union[str, int]:
        if self.tsumogiri:
            result = TSUMOGIRI
        else:
            result = self.tile.encode_tenhou()

        if self.riichi_delcaration:
            result = f"r{result}"

        return result


class ChiSymbol(NamedTuple):
    """
    a, b: 手里牌
    tile: 喂牌
    """
    a: Tile
    b: Tile
    tile: Tile

    def encode_tenhou(self) -> str:
        return f"c{self.tile.encode_tenhou()}{self.a.encode_tenhou()}{self.b.encode_tenhou()}"


class PonSymbol(NamedTuple):
    """
    a, b: 手里牌
    tile: 喂牌
    """
    a: Tile
    b: Tile
    tile: Tile
    feeder_relative: int

    def encode_tenhou(self) -> str:
        s = ""
        for i in range(3):
            if i == self.feeder_relative:
                s += "p"
            s += str(self[i].encode_tenhou())
        return s


class DaiminkanSymbol(NamedTuple):
    """
    a, b, c: 手里牌
    tile: 喂牌
    """
    a: Tile
    b: Tile
    c: Tile
    tile: Tile
    feeder_relative: int

    def encode_tenhou(self) -> str:
        pos = self.feeder_relative
        if pos == 2:
            pos = 3

        s = ""
        for i in range(4):
            if i == pos:
                s += "m"
            s += str(self[i].encode_tenhou())
        return s


class AnkanSymbol(NamedTuple):
    tile: Tile

    def encode_tenhou(self) -> str:
        t = self.tile.encode_tenhou()
        if self.tile.num == 5 and self.tile.type != TileType.Z:
            return f"{t}{t}{t}a{Tile(5, self.tile.type).encode_tenhou()}"
        else:
            return f"{t}{t}{t}a{t}"


class PeSymbol:
    # NOTE: tenhou doesn't mark its kita based on when they were drawn
    def encode_tenhou(self) -> str:
        return "f44"


class KakanSymbol(NamedTuple):
    """
    a, b, c: 手里牌
    tile: 加杠牌
    """
    a: Tile
    b: Tile
    c: Tile
    tile: Tile
    feeder_relative: int

    def encode_tenhou(self) -> str:
        pos = self.feeder_relative
        if pos == 2:
            pos = 3

        s = ""
        for i in range(4):
            if i == pos:
                s += "k"
            s += str(self[i].encode_tenhou())
        return s


class Round(NamedTuple):
    kyoku: int
    honba: int
    riichi_sticks: int


class KyokuResult(Protocol):
    def dump(self) -> Sequence:
        ...


class SpecialRyukyoku(IntEnum):
    kyushukyuhai = 1
    sufonrenda = 2
    suuchariichi = 3
    suukaikan = 4
    sanchahou = 5

    def dump(self) -> Sequence:
        if self == SpecialRyukyoku.kyushukyuhai:
            return RUNES["kyuushukyuuhai"][JPNAME],
        elif self == SpecialRyukyoku.sufonrenda:
            return RUNES["suufonrenda"][JPNAME],
        elif self == SpecialRyukyoku.suuchariichi:
            return RUNES["suuchariichi"][JPNAME],
        elif self == SpecialRyukyoku.suukaikan:
            return RUNES["suukaikan"][JPNAME],
        elif self == SpecialRyukyoku.sanchahou:
            return RUNES["sanchahou"][JPNAME],
        else:
            return tuple()


class Ryukyoku(NamedTuple):
    delta: list[int]
    nagashimangan: bool

    def dump(self) -> Sequence:
        if self.nagashimangan:
            return RUNES["nagashimangan"][JPNAME], self.delta
        else:
            return RUNES["ryuukyoku"][JPNAME], self.delta


class AgariPointLevel(IntEnum):
    yakuman = 0
    sanbaiman = 1
    baiman = 2
    haneman = 3
    mangan = 4


class AgariPoint(NamedTuple):
    ron: int = 0
    tsumo: int = 0
    tsumo_oya: int = 0
    oya: bool = False

    @property
    def level(self) -> Optional[AgariPointLevel]:
        judgement = 0
        if self.ron == 0:
            if self.oya:
                judgement = (self.tsumo * 9) >> 2
            else:
                judgement = self.tsumo * 2 + self.tsumo_oya
        else:
            if self.oya:
                judgement = (self.ron * 3) >> 2
            else:
                judgement = self.ron

        if judgement >= 32000:
            return AgariPointLevel.yakuman
        elif judgement >= 24000:
            return AgariPointLevel.sanbaiman
        elif judgement >= 16000:
            return AgariPointLevel.baiman
        elif judgement >= 12000:
            return AgariPointLevel.haneman
        elif judgement >= 8000:
            return AgariPointLevel.mangan
        else:
            return None


@dataclass
class Yaku:
    id: int
    val: int


@dataclass
class SingleAgari:
    seat: int
    ldseat: int  # points from (self if tsumo)
    paoseat: int  # who won or if pao: who's responsible

    han: int
    fu: int
    yaku: list[Yaku]
    oya: bool
    tsumo: bool
    yakuman: bool
    point: AgariPoint
    delta: list[int]


@dataclass
class Agari:
    agari: list[SingleAgari]
    uras: list[Tile]

    def dump(self) -> Sequence:
        li = [RUNES["agari"][JPNAME]]

        for agari in self.agari:
            li.append(pad_list(agari.delta, 4, 0))

            res = [agari.seat, agari.ldseat, agari.paoseat]

            if agari.tsumo:
                if agari.oya:
                    point = f"{agari.point.tsumo}{RUNES['points'][JPNAME]}{RUNES['all'][JPNAME]}"
                else:
                    point = f"{agari.point.tsumo}-{agari.point.tsumo_oya}{RUNES['points'][JPNAME]}"
            else:
                point = f"{agari.point.ron}{RUNES['points'][JPNAME]}"

            fuhan = f"{agari.fu}{RUNES['fu'][JPNAME]}{agari.han}{RUNES['han'][JPNAME]}"

            point_level = agari.point.level
            if point_level == AgariPointLevel.yakuman:
                if agari.han >= 13:
                    point = RUNES['kazoeyakuman'][JPNAME] + point
                else:
                    point = RUNES['yakuman'][JPNAME] + point
                fuhan = ""
            elif point_level == AgariPointLevel.sanbaiman:
                point = RUNES['sanbaiman'][JPNAME] + point
                fuhan = ""
            elif point_level == AgariPointLevel.baiman:
                point = RUNES['baiman'][JPNAME] + point
                fuhan = ""
            elif point_level == AgariPointLevel.haneman:
                point = RUNES['haneman'][JPNAME] + point
                fuhan = ""
            elif point_level == AgariPointLevel.mangan:
                if agari.han >= 5 or agari.han >= 4 and agari.fu >= 40 or agari.han >= 3 and agari.fu >= 70:
                    point = RUNES['mangan'][JPNAME] + point
                else:
                    point = RUNES['kiriagemangan'][JPNAME] + point
                fuhan = ""

            point = fuhan + point
            res.append(point)

            for e in agari.yaku:
                name = cfg['fan']['fan']['map_'][str(e.id)]['name_jp']

                if agari.yakuman:
                    res.append(f"{name}({RUNES['yakuman'][JPNAME]})")
                else:
                    res.append(f"{name}({e.val}{RUNES['han'][JPNAME]})")

            li.append(res)

        return li


@dataclass
class Kyoku:
    nplayers: int

    round: Round

    initscores: list[int]

    doras: list[Tile]

    draws: list[list[Symbol]]

    discards: list[list[Symbol]]

    haipais: list[list[Tile]]

    result: Optional[KyokuResult] = None

    def dump(self):
        entry = [self.round, self.initscores, [t.encode_tenhou() for t in self.doras]]

        if isinstance(self.result, Agari):
            entry.append([t.encode_tenhou() for t in self.result.uras])
        else:
            entry.append([])

        for i in range(self.nplayers):
            entry.append([t.encode_tenhou() for t in self.haipais[i]])
            entry.append([t.encode_tenhou() for t in self.draws[i]])
            entry.append([t.encode_tenhou() for t in self.discards[i]])

        if self.result is not None:
            entry.append(self.result.dump())

        return entry
