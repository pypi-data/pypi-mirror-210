from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class CommandBase(Protocol):
    @property
    def name(self) -> str: ...

    def setup_args(self, parser: ArgumentParser) -> None: ...

    def setup_subparser(self, parser: ArgumentParser) -> None: ...


@runtime_checkable
class Command(CommandBase, Protocol):
    def run(self, args: Namespace) -> None: ...


@runtime_checkable
class AsyncCommand(CommandBase, Protocol):
    async def async_run(self, args: Namespace) -> None: ...
