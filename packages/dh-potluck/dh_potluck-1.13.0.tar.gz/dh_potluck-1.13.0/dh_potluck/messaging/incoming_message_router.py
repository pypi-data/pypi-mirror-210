from typing import Dict, Protocol, Tuple

from ddtrace import tracer

from dh_potluck.messaging import Message, MessageConsumer


class MessageHandlerCallback(Protocol):
    def __call__(self, topic: str, message_type: str, message: Message) -> bool:
        pass


class NoHandlerException(Exception):
    def __init__(self, topic, message_type):
        self.topic = topic
        self.message = f'No handler for topic: {topic}, message_type: {message_type}'
        super().__init__(self.message)


class IncomingMessageRouter(object):
    _handlers: Dict[Tuple[str, str], MessageHandlerCallback]
    _consumer: MessageConsumer

    def __init__(
        self,
        consumer: MessageConsumer,
        handlers: Dict[Tuple[str, str], MessageHandlerCallback],
    ):
        """
        :param str consumer: The kafka consumer group to use
        :param dict handlers: Dictionary of topic, message_type -> MessageHandlerCallback
        """
        self._consumer = consumer
        self._handlers = handlers

    def register_handler(
        self, topic: str, message_type: str, handler: MessageHandlerCallback
    ) -> None:
        self._handlers[(topic, message_type)] = handler

    def run(self) -> None:
        """
        Start consuming messages. On new messages, check the handlers map, if the message's topic
        and message_type matches a handler key, use it to serialize the message, and handle it.
        :return: None
        """
        self._consumer.subscribe(set(topic for topic, _ in self._handlers))
        try:
            for message in self._consumer.get_messages():
                self._handle_message(message)
        finally:
            self._consumer.shutdown()

    def _handle_message(self, message: Message) -> None:
        topic = message.topic()
        message_type = message.value()['message_type']
        key = (topic, message_type)
        handler = self._handlers.get(key)
        if not handler:
            raise NoHandlerException(topic, message_type)
        with tracer.trace('kafka.consume', resource=f'{topic} {message_type}'):
            should_commit = handler(topic, message_type, message)
        if should_commit:
            self._consumer.commit(message)
