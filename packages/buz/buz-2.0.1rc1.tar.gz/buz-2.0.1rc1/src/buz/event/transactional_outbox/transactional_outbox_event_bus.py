from typing import Collection

from buz.event import Event, EventBus
from buz.event.transactional_outbox.event_to_outbox_record_translator import EventToOutboxRecordTranslator
from buz.event.transactional_outbox.outbox_repository import OutboxRepository


class TransactionalOutboxEventBus(EventBus):
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        event_to_outbox_record_translator: EventToOutboxRecordTranslator,
    ):
        self.__outbox_repository = outbox_repository
        self.__event_to_outbox_record_translator = event_to_outbox_record_translator

    def publish(self, event: Event) -> None:
        outbox_record = self.__event_to_outbox_record_translator.translate(event)
        self.__outbox_repository.save(outbox_record)

    def bulk_publish(self, events: Collection[Event]) -> None:
        for event in events:
            self.publish(event)
