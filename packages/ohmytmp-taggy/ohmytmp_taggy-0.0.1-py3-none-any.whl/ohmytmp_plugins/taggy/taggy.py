from typing import Union, Callable
import pyparsing as pp

from ohmytmp import PluginAfter, Info

ALL = '/all'

class Taggy(PluginAfter):
    def __init__(self) -> None:
        self.data = dict()
        self.data[ALL] = set()

        def __func(info: Info):
            for i in info.to_taglist():
                self.data.setdefault(i, set())
                self.data[i].add(info.SRC)
            self.data[ALL] = set()

        super().__init__(__func)

    def get(self, k: str) -> set:
        return self.data.get(k, set())


# x = word
# x = x|x
# x = x&x
# x = ~x
# x = (x)
ALPHAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'

lparen = pp.Suppress("(")
rparen = pp.Suppress(")")
word = pp.Word(ALPHAS)
sexp = pp.Forward()
atom = word | pp.Group(lparen + sexp + rparen)
term = pp.ZeroOrMore('~') + atom
sexp << term + pp.ZeroOrMore(pp.oneOf('| &') + term)


def getlist(x: str) -> list:
    try:
        return sexp.parseString(x, parse_all=True).asList()
    except pp.exceptions.ParseException:
        return list()


class TagInterpreter(Taggy):
    def __init__(self) -> None:
        super().__init__()

    def l2s(self, l: list) -> set:
        if not l:
            return set()
        ans = ppList(self.get, self.l2s)
        for item in l:
            ans.appenditem(item)
        return ans.result()

    def getsrcs(self, x: str) -> set:
        l = getlist(x)
        return self.l2s(l)


class ppList:
    def __init__(self, get: Callable[[str], set], l2s: Callable[[list], set]) -> None:
        self.get = get
        self.l2s = l2s
        self.l = list()

    def result(self) -> set:
        assert len(self.l) == 1
        ans = self.l.pop()
        assert isinstance(ans, set)
        return ans

    def appendset(self, items: set) -> None:
        if not self.l or self.l[-1] == '(':
            self.l.append(items)
            return

        fn = self.l.pop()

        assert fn in '~|&'

        if fn == '~':
            self.appendset(self.get(ALL) - items)

        if fn == '|':
            self.appendset(self.l.pop() | items)

        if fn == '&':
            self.appendset(self.l.pop() & items)

    def appenditem(self, item: Union[str, list]) -> None:
        if not isinstance(item, str):
            self.appendset(self.l2s(item))
            return

        if item not in '|&~()':
            self.appendset(self.get(item))
            return

        if item in '|&':
            assert self.l
            assert isinstance(self.l[-1], set)
            self.l.append(item)
            return

        if item in '(':
            if self.l:
                assert isinstance(self.l[-1], str)
            self.l.append(item)
            return

        if item == '~':
            if self.l:
                assert isinstance(self.l[-1], str)
                if self.l[-1] == '~':
                    self.l.pop()
                    return
            self.l.append('~')
            return

        if item == ')':
            assert len(self.l) >= 2
            mid = self.l.pop()
            assert isinstance(mid, set)
            left = self.l.pop()
            assert left == '('
            self.l.append(mid)
            return
