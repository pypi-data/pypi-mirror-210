import logging
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable, Dict, Optional, Tuple, Union

from marshmallow import Schema, ValidationError

from dh_potluck.messaging import (
    IncomingMessageRouter,
    Message,
    MessageConsumer,
    MessageHandlerCallback,
)

LOG = logging.getLogger(__name__)


class MessageConsumerApp(object):

    _router: IncomingMessageRouter
    _consumer: MessageConsumer
    _handlers: Dict[Tuple[str, str], MessageHandlerCallback]

    def __init__(self, consumer: MessageConsumer):
        """
        :param str consumer: MessageConsumer
        """
        self._consumer = consumer
        self._handlers = {}
        self._router = IncomingMessageRouter(self._consumer, self._handlers)

    def register(self, topic: str, message_type: str):
        """
        Registers decorated function as a message handler
        :param str topic: Topic to handle
        :param str message_type: Message Type to handle
        """

        def decorator_register_message_handler(func: MessageHandlerCallback):
            self.register_handler(topic, message_type, func)
            return func

        return decorator_register_message_handler

    def register_handler(
        self, topic: str, message_type: str, handler: MessageHandlerCallback
    ) -> None:
        self._router.register_handler(topic, message_type, handler)

    def run(self):
        """
        Start consuming messages. On new messages, use the registered message_handler to handle it.
        :return: None
        """
        self._router.run()


def validate_schema(schema: Schema):
    """
    Validate a message's schema

    :param Schema schema: schema to use when validating the message payload
    """

    def _wrapper(handler: Callable[[str, str, Any, Message], Optional[bool]]):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            payload = schema.loads(message.value()['payload'])
            return handler(topic, message_type, payload, message)

        return wrapper

    return _wrapper


def validate_schema_and_ignore_errors(schema: Schema):
    """
    Validate a message's schema, but catch errors and return them to the function

    This can be useful in some cases when skipping messages on schema errors is acceptable, but
    allowing schema issues to crash the consumer will prevent skipping messages and losing data.

    :param Schema schema: schema to use when validating the message payload
    """

    def _wrapper(
        handler: Callable[
            [str, str, Any, Union[ValidationError, JSONDecodeError, None], Message],
            Optional[bool],
        ]
    ):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            payload = None
            error = None
            try:
                payload = schema.loads(message.value()['payload'])
            except (ValidationError, JSONDecodeError) as e:
                error = e
            return handler(topic, message_type, payload, error, message)

        return wrapper

    return _wrapper
