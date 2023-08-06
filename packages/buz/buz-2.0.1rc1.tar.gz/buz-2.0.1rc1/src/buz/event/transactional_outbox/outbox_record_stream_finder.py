from abc import ABC, abstractmethod
from typing import Iterable

from buz.event.transactional_outbox import OutboxCriteria, OutboxRecord


class OutboxRecordStreamFinder(ABC):
    @abstractmethod
    def find(self, criteria: OutboxCriteria) -> Iterable[OutboxRecord]:
        pass
