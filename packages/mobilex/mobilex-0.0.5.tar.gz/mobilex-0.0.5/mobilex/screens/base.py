import re
import sys
import typing as t
from collections import ChainMap, UserString, abc
from copy import copy
from inspect import isawaitable
from logging import getLogger
from operator import attrgetter
from typing import Any, Iterator

from .. import exc
from ..responses import Response, redirect
from ..utils.types import NamespaceDict

if t.TYPE_CHECKING:
    from mobilex import App, Request
    from mobilex.sessions import Session


logger = getLogger(__name__)


NOTHING = object()


T = t.TypeVar("T")
_DT = t.TypeVar("_DT")
_AT = t.TypeVar("_AT", bound="Action")

CON = "CON"

END = "END"

NL = "\r\n" if sys.platform == "win32" else "\n"


class ScreenMetaOptions:
    pass


class ScreenState(NamespaceDict):
    __slots__ = ()

    def __init__(self, screen, *bases, **data):
        super().__init__(*bases, **data)
        self.screen = screen

    def reset(self, *keep, **values):
        ("screen" in keep) or values.setdefault("screen", self.screen)
        for k in keep:
            if k in self:
                values.setdefault(k, getattr(self, k))
        self.clear()
        self.update(values)


class ScreenType(type):
    def __new__(mcls, name, bases, dct):
        super_new = super(ScreenType, mcls).__new__
        cls = super_new(mcls, name, bases, dct)
        return cls


class UssdPayload(UserString):
    __slots__ = ()

    def append(self, *objs, sep=" ", end=NL):
        self.data += f"{sep.join((str(s) for s in objs))}{end}"

    def paginate(self, page_size, next_page_choice, prev_page_choice, foot=""):
        if isinstance(foot, (list, tuple, ActionSet)):
            # foot_list = None  # foot[:1]+[str(next_page_choice), ]+foot[1:]
            foot = NL.join(map(str, foot))
        # else:
        #     foot_list = None

        foot = foot and f"{NL}{foot}"
        lfoot = len(foot)
        if len(self.data.strip()) + lfoot <= page_size:
            yield self.data.strip() + foot
        else:
            lnext, lprev = len(str(next_page_choice)) + len(NL), len(
                str(prev_page_choice)
            )
            lnav = lnext + lprev
            chunk, i = self.data.strip(), 0
            while chunk:
                lc = len(chunk)
                if i > 0 and lc <= lprev + page_size:
                    yield f"{chunk}{NL}{prev_page_choice}"
                    chunk = None
                else:
                    yv = re.sub(
                        rf"([{NL}]+[^{NL}]+[{NL}]*)$",
                        "",
                        chunk[
                            : (page_size - lnav if i > 0 else page_size - lfoot - lnext)
                        ],
                    ).strip()
                    if i > 0:
                        yield f"{yv}{NL}{prev_page_choice}{NL}{next_page_choice}"
                    else:
                        # if foot_list:
                        #     yield "%s\n%s" % (yv, "\n".join(foot_list))
                        # else:
                        #     yield "%s\n%s\n%s" % (yv, next_page_choice, foot)
                        yield f"{yv}{NL}{next_page_choice}{NL}{foot}"

                    chunk = chunk[len(yv) + 1 :].strip()
                i += 1

    # def __str__(self):
    #     return self.data.strip()


class Action(t.NamedTuple):
    label: str
    handler: str | abc.Callable = None
    screen: str | int = None
    args: tuple = None
    kwargs: abc.Mapping = None
    key: str = None
    name: str = None

    def handle(self, screen: "Screen", value: str):
        args, kwds = self.args or (), self.kwargs or {}
        if (to := self.screen) is not None:
            return redirect(to, *args, **kwds)
        elif callable(func := self.handler or "handle"):
            return func(screen, value, *args, **kwds)
        elif isinstance(func, str):
            return getattr(screen, func)(value, *args, **kwds)

    def __str__(self):
        return "" if self.key is None else f"{self.key:<2} {self.label}"

    def __bool__(self):
        return self.key is not None


_null_act = Action(None)


class _ActionDict(dict[str, _AT]):
    __slots__ = ()


class ActionSet(abc.Set[_AT]):
    __slots__ = ("_chain", "_src")
    _src: abc.Mapping[str, _AT]
    _chain: ChainMap[str, _AT]

    def __new__(cls, it: abc.Iterable[_AT] = ()):
        self = object.__new__(cls)
        self._src = _ActionDict(
            it._src
            if isinstance(it, ActionSet)
            else it
            if isinstance(it, _ActionDict)
            else cls._parse_src(it)
        )
        return self

    @classmethod
    def _parse_src(cls, iterable: abc.Iterable[_AT]):
        seen, i = set(), 0

        for it in iterable:
            if it.key is None:
                it = it._replace(key=(i := i + 1))
            key, nm = str(it.key), it.name
            assert key not in seen, f"duplicate action key {key!r}"
            assert nm is None or nm not in seen, f"duplicate action name {nm!r}"
            yield key, it
            seen.update((key, nm))

    @classmethod
    def _to_key(cls, obj):
        return str(obj.key if isinstance(obj, Action) else obj)

    def __ror__(self, x: object):
        if not isinstance(x, abc.Iterable):
            return NotImplemented
        return self.__class__(x) | self

    def __or__(self, x: object):
        if not isinstance(x, ActionSet):
            if not isinstance(x, abc.Iterable):
                return NotImplemented
            x = self.__class__(x)
        return self.__class__(_ActionDict(self._src | x._src))

    def __contains__(self, x: object) -> bool:
        return self._to_key(x) in self._src

    def __len__(self) -> int:
        return len(self._src)

    def __iter__(self) -> Iterator[_AT]:
        return iter(self._src.values())

    def __getitem__(self, key):
        return self._src[self._to_key(key)]

    def __reduce__(self) -> str | tuple[Any, ...]:
        return self.__class__, (self._src,)

    def get(self, key, default: _DT = None):
        return self._src.get(self._to_key(key), default)

    def keys(self):
        return self._src.keys()

    # def names(self):
    #     return self._src.maps[1].keys()


class Screen(t.Generic[T], metaclass=ScreenType):
    # META_OPTIONS_CLASS = ScreenMetaOptions

    CON = CON

    END = END

    exit_code = CON

    init: t.ClassVar[t.Optional[t.Callable]] = None
    validate: t.ClassVar[t.Optional[t.Callable]] = None

    request: "Request"
    app: "App" = property(attrgetter("request.app"))
    session: "Session" = property(attrgetter("request.session"))
    state: ScreenState

    _meta: t.ClassVar[ScreenMetaOptions]
    _payload_class: type[UssdPayload] = UssdPayload
    _state_class: type[ScreenState] = ScreenState
    _has_actions: bool = False

    actions = None

    nav_actions = [
        Action("Back", key="0", screen=-1),
        Action("Home", key="00", screen=0),
    ]

    # pagination_actions = [
    #     Action("Back", key="0", name="prev"),
    #     Action("More", key="99", name="next"),
    # ]

    next_page_action = Action("More", key="99")
    prev_page_action = Action("Back", key="0")

    def __init__(self, state):
        self.state = state
        self.payload = self._payload_class("")

    @t.overload
    def print(self, *objs, sep=" ", end=NL):
        ...

    @property
    def print(self):
        return self.payload.append

    def get_actions(self):
        return self.actions or ()

    # def get_pagination_actions(self):
    #     return self.pagination_actions or ()

    def get_nav_actions(self):
        return self.nav_actions or ()

    def get_action_set(self):
        return ActionSet(self.get_actions())

    # def get_pagination_action_set(self):
    #     return ActionSet(self.get_pagination_actions())

    # def get_next_page_action(self):
    #     return self.next_page_action or _null_action

    # def get_prev_page_action(self):
    #     return self.prev_page_action or _null_action

    def get_nav_action_set(self):
        return ActionSet(self.get_nav_actions())

    async def handle(self, inpt):
        self._has_actions and self.print("Error! Invalid choice.")

    async def render(self):
        pass

    # async def handle_exception(self, e, inpt=None):
    #     if inpt is not None and isinstance(e, exc.ValidationError):
    #         self.payload.prepend(e)
    #         return await self._async_render()
    #     else:
    #         raise e

    async def _async_init(self, inpt=None):
        rv = self.init(inpt)
        if isawaitable(rv):
            rv = await rv
        return rv

    async def _async_render(self):
        rv = self.render()
        if isawaitable(rv):
            rv = await rv
        return rv

    # async def _async_handle(self, inpt):
    #     rv = self.handle(inpt)
    #     if isawaitable(rv):
    #         rv = await rv
    #     return rv

    # async def _async_validate(self, inpt):
    #     rv = self.validate(inpt)
    #     if isawaitable(rv):
    #         rv = await rv
    #     return rv

    async def _async_handle_exception(self, e, inpt=None):
        rv = self.handle_exception(e, inpt)
        if isawaitable(rv):
            rv = await rv
        return rv

    def abort(self, *args, **kwargs):
        raise exc.ValidationError(*args, **kwargs)

    async def __call__(self, request: "Request", input: str = None):
        self.request = request
        rv, pages, i = None, self.state.get("_pages", []), 0
        current_page = self.state.get("_current_page", 0)
        key = input if input is None else f"{input}".strip()

        if not (was_ready := self.state.get("__initialized__")):
            if self.init is not None:
                rv = await self._async_init(input)
            self.state.__initialized__ = True

        next, prev = self.next_page_action, self.prev_page_action
        if is_next := key and key == next.key:
            if current_page < len(pages) - 1:
                self.state._current_page = i = current_page + 1
                rv = self.state._action
        elif key == prev.key and current_page > 0:
            self.state._current_page = i = current_page - 1
            rv = self.state._action

        if rv is None:
            acts, nav_acts = self.get_action_set(), self.get_nav_action_set()
            self._has_actions = not not acts
            if not (key is None or is_next):
                act = acts.get(key) or nav_acts.get(key) or _null_act
                if isawaitable(rv := act.handle(self, input)):
                    rv = await rv

            if rv is None:
                if isawaitable(rv := self.render()):
                    rv = await rv

            if isinstance(rv, Response):
                return rv

            if rv is None:
                rv = self.exit_code

            payload = self.payload
            acts and payload.append(*acts, sep=NL)
            nav_acts = [] if rv == self.END else nav_acts
            mx_page_len = request.app.config.max_page_length - 4
            pages = list(payload.paginate(mx_page_len, next, prev, nav_acts))
            self.state._action, self.state._pages = rv, pages
            self.state._current_page = i = 1 if is_next and len(pages) > 1 else 0

        return f"{rv} {pages[i]}"
