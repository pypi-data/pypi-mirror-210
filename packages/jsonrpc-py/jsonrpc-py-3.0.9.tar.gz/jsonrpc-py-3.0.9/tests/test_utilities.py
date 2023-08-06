from asyncio import create_task, sleep, wait_for
from typing import Any, Literal, NoReturn
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, sentinel

from jsonrpc.utilities import Undefined, UndefinedType, ensure_async, make_hashable, multiple_coroutines


class TestHashable(TestCase):
    def test_equality(self) -> None:
        tests: tuple[tuple[Any, Any], ...] = (
            ([], ()),
            (["a", 1], ("a", 1)),
            ({}, ()),
            ({"a"}, ("a",)),
            (frozenset({"a"}), {"a"}),
            ({"a": 1, "b": 2}, (("a", 1), ("b", 2))),
            ({"b": 2, "a": 1}, (("a", 1), ("b", 2))),
            (("a", ["b", 1]), ("a", ("b", 1))),
            (("a", {"b": 1}), ("a", (("b", 1),))),
        )
        for actual, expected in tests:
            with self.subTest(actual=actual):
                self.assertEqual(make_hashable(actual), expected)

    def test_count_equality(self) -> None:
        tests: tuple[tuple[Any, Any], ...] = (
            ({"a": 1, "b": ["a", 1]}, (("a", 1), ("b", ("a", 1)))),
            ({"a": 1, "b": ("a", [1, 2])}, (("a", 1), ("b", ("a", (1, 2))))),
        )
        for actual, expected in tests:
            with self.subTest(actual=actual):
                self.assertCountEqual(make_hashable(actual), expected)

    def test_unhashable(self) -> None:
        class Unhashable:
            __hash__: Literal[None] = None

        with self.assertRaises(TypeError) as context:
            make_hashable(Unhashable())

        self.assertIn("unhashable type", str(context.exception))


class TestUndefined(TestCase):
    def test_hash(self) -> None:
        self.assertEqual(hash(Undefined), 0xBAADF00D)

    def test_equality(self) -> None:
        self.assertEqual(Undefined, UndefinedType())
        self.assertNotEqual(Undefined, None)

    def test_is_truth(self) -> None:
        self.assertFalse(Undefined)


class TestAsyncioUtilities(IsolatedAsyncioTestCase):
    async def test_ensure_async(self) -> None:
        for mock in (
            MagicMock(return_value=sentinel.sync_def),
            AsyncMock(return_value=sentinel.async_def),
        ):
            with self.subTest(mock=mock):
                result: Any = await ensure_async(mock, 1, 2, 3, key="value")
                self.assertIs(result, mock.return_value)
                mock.assert_called_once_with(1, 2, 3, key="value")

    async def test_multiple_coroutines(self) -> None:
        mocks: set[AsyncMock] = {AsyncMock(return_value=i) for i in ("a", "b", "c")}

        async def inner(mock: AsyncMock) -> Any:
            return await mock()

        results: tuple[str, ...] = await multiple_coroutines(map(inner, mocks))
        self.assertCountEqual(results, ("a", "b", "c"))

        for mock in mocks:
            with self.subTest(mock=mock):
                mock.assert_awaited_once()

    async def test_multiple_coroutines_preserved_order(self) -> None:
        results: tuple[str, ...] = await multiple_coroutines(
            (
                sleep(0.04, "a"),  # <-- accepted latest but should be first in results
                sleep(0.02, "b"),  # <-- accepted second and should be second in results
                sleep(0.01, "c"),  # <-- accepted first but should be third in results
                sleep(0.03, "d"),  # <-- accepted third but should be latest in results
            )
        )
        self.assertTupleEqual(results, ("a", "b", "c", "d"))

    async def test_multiple_coroutines_exception(self) -> None:
        first_exception_mock: AsyncMock = AsyncMock(side_effect=Exception("first exception"))
        second_exception_mock: AsyncMock = AsyncMock(side_effect=Exception("second exception"))

        async def inner(mock: AsyncMock) -> Any:
            return await mock()

        with self.assertRaises(Exception) as context:
            await multiple_coroutines(map(inner, (first_exception_mock, second_exception_mock)))

        self.assertRegex(str(context.exception), r"(?:first|second) exception")
        first_exception_mock.assert_awaited_once()
        second_exception_mock.assert_awaited_once()

    async def test_multiple_coroutines_timeout_error(self) -> None:
        hello_task, world_task = create_task(sleep(3600.0, "hello")), create_task(sleep(3600.0, "world"))
        with self.assertRaises(TimeoutError):
            await multiple_coroutines(
                [
                    wait_for(hello_task, timeout=0.001),
                    wait_for(world_task, timeout=0.002),
                ]
            )
        self.assertTrue(hello_task.cancelled())
        self.assertTrue(world_task.cancelled())

    async def test_multiple_coroutines_exception_group(self) -> None:
        async def inner() -> NoReturn:
            raise ExceptionGroup(
                "one",
                (
                    Exception("for testing purposes"),  # <-- this should be raised first
                    ExceptionGroup(
                        "two",
                        (
                            Exception("2"),
                            Exception("3"),
                        ),
                    ),
                    ExceptionGroup(
                        "three",
                        (
                            Exception("4"),
                            Exception("5"),
                        ),
                    ),
                ),
            )

        with self.assertRaises(Exception) as context:
            await multiple_coroutines([inner()])

        self.assertEqual(str(context.exception), "for testing purposes")
