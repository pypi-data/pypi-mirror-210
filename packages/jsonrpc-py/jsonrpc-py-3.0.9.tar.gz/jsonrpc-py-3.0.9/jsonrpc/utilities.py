from asyncio import AbstractEventLoop, Future, Task, TaskGroup, get_running_loop
from collections.abc import Callable, Coroutine, Generator, Iterable, Iterator, MutableMapping
from contextvars import Context, copy_context
from dataclasses import dataclass, field
from functools import partial
from heapq import heappop, heappush
from inspect import iscoroutinefunction
from typing import Any, Final, Generic, Literal, ParamSpec, TypeAlias, TypeGuard, TypeVar, final

__all__: Final[tuple[str, ...]] = (
    "ensure_async",
    "is_iterable",
    "make_hashable",
    "multiple_coroutines",
    "Undefined",
    "UndefinedType",
)

T = TypeVar("T")
P = ParamSpec("P")
CoroutineLike: TypeAlias = Generator[Any, None, T] | Coroutine[Any, Any, T]


def ensure_async(user_function: Callable[P, Any], /, *args: P.args, **kwargs: P.kwargs) -> Future[Any]:
    loop: AbstractEventLoop = get_running_loop()
    context: Context = copy_context()

    if iscoroutinefunction(callback := partial(user_function, *args, **kwargs)):
        return loop.create_task(callback(), context=context)
    else:
        return loop.run_in_executor(None, context.run, callback)


def is_iterable(obj: Any, /) -> TypeGuard[Iterable[Any]]:
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def make_hashable(obj: Any, /) -> Any:
    if isinstance(obj, MutableMapping):
        return tuple((key, make_hashable(value)) for key, value in sorted(obj.items()))
    #: ---
    #: Try hash to avoid converting a hashable iterable (e.g. string, frozenset)
    #: to a tuple:
    try:
        hash(obj)
    except TypeError:
        if is_iterable(obj):
            return tuple(map(make_hashable, obj))
        #: ---
        #: Non-hashable, non-iterable:
        raise

    return obj


@dataclass(repr=False, eq=False, slots=True)
class multiple_coroutines(Generic[T]):
    coroutines: Iterable[CoroutineLike[T]]
    queue: list[tuple[int, T]] = field(default_factory=list, init=False)

    def __await__(self) -> Generator[Any, None, tuple[T, ...]]:
        #: ---
        #: Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> tuple[T, ...]:
        context: Final[Context] = copy_context()
        try:
            async with TaskGroup() as tg:
                for task_id, coroutine in enumerate(self.coroutines):
                    task: Task[T] = tg.create_task(coroutine, context=context)
                    callback: partial[None] = partial(self.populate_results, task_id=task_id)
                    task.add_done_callback(callback, context=context)
        except BaseExceptionGroup as exc_group:
            #: ---
            #: Propagate the first raised exception from exception group:
            for exc in self.exception_from_group(exc_group):
                raise exc from None

        return tuple(self.iter_results())

    def populate_results(self, task: Task[T], *, task_id: int) -> None:
        if not task.cancelled() and task.exception() is None:
            result: Final[T] = task.result()
            heappush(self.queue, (task_id, result))

    def exception_from_group(self, exc: BaseException) -> Iterator[BaseException]:
        if isinstance(exc, BaseExceptionGroup):
            for nested in exc.exceptions:
                yield from self.exception_from_group(nested)
        else:
            yield exc

    def iter_results(self) -> Iterator[T]:
        while True:
            try:
                _, result = heappop(self.queue)
                yield result
            except IndexError:
                break


@final
class UndefinedType:
    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> Literal["Undefined"]:
        return "Undefined"

    def __hash__(self) -> Literal[0xBAADF00D]:
        return 0xBAADF00D

    def __eq__(self, obj: Any) -> bool:
        return isinstance(obj, self.__class__)

    def __bool__(self) -> Literal[False]:
        return False


Undefined: Final[UndefinedType] = UndefinedType()
