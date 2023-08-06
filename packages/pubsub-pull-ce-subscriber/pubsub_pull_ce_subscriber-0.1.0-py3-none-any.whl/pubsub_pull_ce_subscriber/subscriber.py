#!/usr/bin/env python
import typer
from typing_extensions import Annotated

from cloudevents.http import CloudEvent
from cloudevents.conversion import to_binary, to_structured
import requests


from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber import exceptions as sub_exceptions

import logging
import structlog


def subscribe(
        subscription: Annotated[str, typer.Argument(envvar="SUBSCRIPTION")],
        project: Annotated[str, typer.Option(envvar="PROJECT")] = None,
        ce_sink: Annotated[str, typer.Option(envvar="CE_SINK")] = None,
        batch_size: Annotated[int, typer.Option(envvar="BATCH_SIZE")] = 10,
        ack_timeout: Annotated[int, typer.Option(envvar="ACK_TIMEOUT")] = 10,
        debug: Annotated[bool, typer.Option(envvar="DEBUG")] = False,
        #payload_type: Annotated[str, typer.Option(envvar="PAYLOAD_TYPE")] = "structured"
):
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(debug and logging.DEBUG or logging.INFO),
    )
    logger = structlog.getLogger()

    subscriber = pubsub_v1.SubscriberClient()
    if project is not None:
        subscription = subscriber.subscription_path(project, subscription)
    logger.debug(f"pull from subscription {subscription}")
    if ce_sink is None:
        logger.debug("sink disabled")
    else:
        logger.debug(f"sink to {ce_sink}")
    logger.debug(f"bacth size: {batch_size} ")
    #if payload_type not in ["structured", "binary"]:
    #    logger.error("payload type must be binary or structured (default)")

    def _callback(message: pubsub_v1.subscriber.message.Message) -> None:
        logger.debug(f"Received {message}.")
        # if payload_type == "structured":
        #     data = message.data.decode()
        #     #logger.debug(f"structured data: {data}")
        #     marshaller = to_structured
        # else:  # binary
        #     marshaller = to_binary
        #     data = message.data

        ack_future = message.ack_with_response()
        try:
            ack_future.result(timeout=ack_timeout)
            logger.debug(f"Ack for message {message.message_id} successful")
        except sub_exceptions.AcknowledgeError as e:
            logger.warn(
                f"Ack for message {message.message_id} failed with error: {e.error_code}"
            )

        if ce_sink:
            try:
                event = CloudEvent(message.attributes, message.data)
                headers, body = to_binary(event)
                requests.post(ce_sink, data=body, headers=headers)
            except Exception as ex:
                logger.error(ex)
                return


    flow_control = pubsub_v1.types.FlowControl(max_messages=batch_size)
    streaming_pull_future = subscriber.subscribe(
        subscription, callback=_callback, flow_control=flow_control
    )
    logger.info("Listening for messages...")
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result()
        except Exception as ex:
            logger.error(ex)
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

def main():
    typer.run(subscribe)

if __name__ == '__main__':
    main()

