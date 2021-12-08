from abc import ABC, abstractmethod
from typing import Sequence

from src.data.action import Action


class ActionDescriber(ABC):
    @abstractmethod
    def describe(self, actions: Sequence[Action]) -> Sequence[str]:
        """"""

    @abstractmethod
    def describe_applied(self, actions: Sequence[Action]) -> Sequence[str]:
        """"""

    @abstractmethod
    def describe_failed(self, actions: Sequence[Action]) -> Sequence[str]:
        """"""


class BriefActionDescriber(ActionDescriber):
    def describe(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.description for a in actions)

    def describe_applied(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.description for a in actions if a.is_applied())

    def describe_failed(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(f"{a.description} ({a.reason})" for a in actions if a.has_failed())


class DetailedActionDescriber(ActionDescriber):
    def describe(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.detailed_description for a in actions)

    def describe_applied(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.detailed_description for a in actions if a.is_applied())

    def describe_failed(self, actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(f"{a.detailed_description} (error: {a.reason})" for a in actions if a.has_failed())
