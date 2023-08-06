import json
import time
from typing import Dict, Union

import boto3
from pydantic import BaseModel

import logging
from .common import session_maker, validate_response


logger = logging.getLogger(__file__)

################################################################
# Models
################################################################
class Message(BaseModel):
    Id: str = None
    MessageBody: str = None
    MessageAttributes: dict = None
    MessageSystemAttributes: dict = None
    MessageDuplicationId: str = None
    MessageGroupId: str = None


class ReturnedMessage(BaseModel):
    MessageId: str = None
    ReceiptHandle: str = None
    MD5OfMessageBody: str = None
    Body: str = None
    MessageAttributes: dict = None


################################################################
# Queue Hadlers
################################################################
# list queues
def list_queues(prefix=None, session=None, session_opts=None):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    paginate_opts = {
        "QueueNamePrefix": prefix,
        "PaginationConfig": {},
    }
    paginate_opts = {k: v for k, v in paginate_opts.items() if v is not None}

    queue_urls = []
    paginator = client.get_paginator("list_queues")
    for response in paginator.paginate(**paginate_opts):
        for queue_url in response.get("QueueUrls", []):
            queue_urls.append(queue_url)

    return queue_urls


# create queue
def create_queue(
    queue_name: str,
    delay_seconds: int = 0,
    visibility_timeout: int = 60,
    dlq_after_received: int = 10,
    wait_for_queue_to_ready_sec: int = -1,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    """
    [NOTE]
    자동 생성한 DLQ는 queue와 동일한 속성을 가짐.

    Arguments
    ---------
    dql_after_received: int
        consumer가 받은 횟수가 이 값을 초과하면 DLQ로 보냄. 0보다 작게 설정하면 DLQ 사용하지 않음.
    wait_for_queue_to_ready_sec: int
        queue가 생성된 것을 확인한 후에 response를 반환. (queue 생성은 주문 후 30초 이상 걸리기도 함.)
    """
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    _queues = list_queues(prefix=queue_name)
    for _queue in _queues:
        if _queue.rsplit("/", 1)[-1] == queue_name:
            logger.warning(f"queue '{queue_name}' already exists!")
            return

    redrive_policy = {}
    if dlq_after_received > 0:
        dlq_name = f"{queue_name}-dlq"
        response = create_queue(
            queue_name=dlq_name,
            delay_seconds=delay_seconds,
            visibility_timeout=visibility_timeout,
            dlq_after_received=-1,
            wait_for_queue_to_ready_sec=60,
        )
        dlq_url = get_queue_url(queue_name=dlq_name, session=session)
        response = client.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn"])
        _ = validate_response(response)
        dlq_arn = response["Attributes"]["QueueArn"]
        redrive_policy = {
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": str(dlq_after_received),
        }

    attributes = {
        "DelaySeconds": str(delay_seconds),
        "VisibilityTimeout": str(visibility_timeout),
    }
    if redrive_policy:
        attributes.update({"RedrivePolicy": json.dumps(redrive_policy)})

    response = client.create_queue(
        QueueName=queue_name,
        Attributes=attributes,
    )
    _ = validate_response(response)

    if wait_for_queue_to_ready_sec > 0:
        t0 = time.time()
        logger.warning(
            f"wait for the new queue '{queue_name}' to be ready... (maximum {wait_for_queue_to_ready_sec} senconds)"
        )
        for _ in range(wait_for_queue_to_ready_sec):
            time.sleep(1)
            try:
                _ = get_queue(queue_name=queue_name, session=session)
                logger.warning(f"queue '{queue_name}' is created! ({time.time() - t0:.3f} sec.)")
                break
            except KeyError:
                pass
            except Exception as ex:
                logger.error(ex)
                raise ex

    return response


# get queue
def get_queue(
    queue_name: str,
    create_if_not_exists: bool = False,
    create_if_not_exists_timeout: int = 60,
    queue_delay_seconds: int = 0,
    queue_visibility_timeout: int = 900,
    dlq_after_received: int = 10,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    session = session if session else session_maker(session_opts=session_opts)
    resource = session.resource("sqs")

    for queue in resource.queues.all():
        if queue.url.rsplit("/", 1)[-1] == queue_name:
            return queue

    if create_if_not_exists:
        response = create_queue(
            queue_name=queue_name,
            delay_seconds=queue_delay_seconds,
            visibility_timeout=queue_visibility_timeout,
            dlq_after_received=dlq_after_received,
            wait_for_queue_to_ready_sec=create_if_not_exists_timeout,
            session=session,
        )
        _ = validate_response(response)
        return get_queue(queue_name=queue_name, session=session)

    raise KeyError(f"queue '{queue_name}' not found!")


# get queue
def set_queue_attributes(
    queue_name: str,
    delay_seconds: int = None,
    maximum_message_size: int = None,
    message_retention_period: int = None,
    receive_message_wait_time_seconds: int = None,
    dlq_queue_name: str = None,
    dlq_max_recevice_count: int = None,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    attributes = {
        "DelaySeconds": delay_seconds,
        "MaximumMessageSize": maximum_message_size,
        "MessageRetentionPeriod": message_retention_period,
        "ReceviceMessageWaitTimeSeconds": receive_message_wait_time_seconds,
    }
    attributes = {k: str(v) for k, v in attributes.items() if v is not None}
    if dlq_queue_name is not None or dlq_max_recevice_count is not None:
        dlq_queue_url = get_queue_url(queue_name=dlq_queue_name, session=session)
        response = client.get_queue_attributes(QueueUrl=dlq_queue_url, AttributeNames=["QueueArn"])
        _ = validate_response(response)
        dlq_arn = response["Attributes"]["QueueArn"]
        redrive_policy = {
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": dlq_max_recevice_count,
        }
        redrive_policy = {k: str(v) for k, v in redrive_policy.items() if v is not None}

    response = client.set_queue_attributes(
        QueueUrl=get_queue_url(queue_name),
        Attributes=attributes,
    )
    _ = validate_response(response)

    return response


# get queue url
def get_queue_url(
    queue_name: str,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    response = client.get_queue_url(QueueName=queue_name)
    _ = validate_response(response)

    return response["QueueUrl"]


# delete queue
def delete_queue(
    queue_name: str,
    delete_dlq: bool = False,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    if delete_dlq:
        queue = get_queue(queue_name=queue_name, create_if_not_exists=False, session=session)
        redrive_policy = queue.attributes.get("RedrivePolicy")
        if redrive_policy:
            redrive_policy = json.loads(redrive_policy)
            _queue_name = redrive_policy["deadLetterTargetArn"].rsplit(":", 1)[-1]
            dlq_sources = list_dead_letter_source_queues(queue_name=_queue_name, session=session)
            if len(dlq_sources) > 1:
                logger.warning(f"other queue uses '{_queue_name}' as DLQ, we'll not delete it!")
            delete_queue(queue_name=_queue_name)

    queue_url = get_queue_url(queue_name=queue_name)
    response = client.delete_queue(QueueUrl=queue_url)
    _ = validate_response(response)

    return response


# delete queue
def purge_queue(
    queue_name: str,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    queue_url = get_queue_url(queue_name=queue_name)
    response = client.purge_queue(QueueUrl=queue_url)
    _ = validate_response(response)

    return response


# list dead letter source queues
def list_dead_letter_source_queues(queue_name, session=None, session_opts=None):
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("sqs")

    queue_url = get_queue_url(queue_name=queue_name, session=session)

    paginate_opts = {
        "QueueUrl": queue_url,
        "PaginationConfig": {},
    }
    paginate_opts = {k: v for k, v in paginate_opts.items() if v is not None}

    queue_urls = []
    paginator = client.get_paginator("list_dead_letter_source_queues")
    for response in paginator.paginate(**paginate_opts):
        for queue_url in response.get("queueUrls", []):
            queue_urls.append(queue_url)

    return queue_urls


################################################################
# Message Handler
################################################################
# Queue
class Queue:
    def __init__(
        self,
        queue_name: str,
        auto_create_queue: bool = False,
        session: boto3.Session = None,
        session_opts: dict = None,
    ):
        # correct args
        session_opts = session_opts if session_opts else {}

        # props
        self.session = session if session else session_maker(session_opts)
        self.client = self.session.client("sqs")
        self.resource = self.session.resource("sqs")
        self.queue = get_queue(queue_name=queue_name, session=self.session, create_if_not_exists=auto_create_queue)
        self.queue_url = get_queue_url(queue_name, session=self.session)

    def send_messages(self, messages: list):
        if not isinstance(messages, (tuple, list)):
            raise ValueError("input 'messages' should be a list!")

        # request validator
        messages = [msg if isinstance(msg, Message) else Message(**msg) for msg in messages]
        entries = [msg.dict(exclude_none=True) for msg in messages]

        # send messages
        response = self.queue.send_messages(Entries=entries)
        _ = validate_response(response)
        if "Successful" in response:
            n_send = len(messages)
            n_succeed = len(response["Successful"])
            if n_succeed != n_send:
                logger.warning(f"send {n_send} messages, only {n_succeed} messages are succeed!")
            return response["Successful"]

        raise ReferenceError("send messages FAILED!")

    def receive_messages(self, message_attribute_names=["All"], max_number_of_messages=10, wait_time_seconds=1):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MessageAttributeNames=message_attribute_names,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
        )
        _ = validate_response(response)
        if "Messages" in response:
            for msg in response["Messages"]:
                print(msg)
            return [ReturnedMessage(**msg) for msg in response["Messages"]]
        return []

    def delete_message(self, receipt_handle_or_message: Union[str, ReturnedMessage]):
        if isinstance(receipt_handle_or_message, ReturnedMessage):
            receipt_handle_or_message = receipt_handle_or_message.ReceiptHandle
        response = self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle_or_message)
        _ = validate_response(response)
        return response

    def purge_queue(self):
        response = self.client.purge_queue(QueueUrl=self.queue_url)
        _ = validate_response(response)
        return response
