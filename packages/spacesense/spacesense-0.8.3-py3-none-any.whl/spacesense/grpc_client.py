import abc
import logging
import time
from random import randint
from typing import Optional, Tuple

import grpc

from spacesense import config
from spacesense.common.proto.backend import backend_pb2_grpc
from spacesense.grpc_auth import GrpcAuth
from spacesense.utils import Singleton

logger = logging.getLogger(__name__)


class SleepingPolicy(abc.ABC):
    @abc.abstractmethod
    def sleep(self, try_i: int):
        """
        How long to sleep in milliseconds.
        :param try_i: the number of retry (starting from zero)
        """
        assert try_i >= 0


class ExponentialBackoff(SleepingPolicy):
    def __init__(self, *, init_backoff_ms: int, max_backoff_ms: int, multiplier: int):
        self.init_backoff = randint(0, init_backoff_ms)
        self.max_backoff = max_backoff_ms
        self.multiplier = multiplier

    def sleep(self, try_i: int):
        sleep_range = min(self.init_backoff * self.multiplier**try_i, self.max_backoff)
        sleep_ms = randint(0, sleep_range)
        logger.debug(f"Sleeping for {sleep_ms}")
        time.sleep(sleep_ms / 1000)


class RetryOnRpcErrorClientInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor):
    def __init__(
        self,
        *,
        max_attempts: int,
        sleeping_policy: SleepingPolicy,
        status_for_retry: Optional[Tuple[grpc.StatusCode]] = None,
    ):
        self.max_attempts = max_attempts
        self.sleeping_policy = sleeping_policy
        self.status_for_retry = status_for_retry

    def _intercept_call(self, continuation, client_call_details, request_or_iterator):

        for try_i in range(self.max_attempts):
            response = continuation(client_call_details, request_or_iterator)

            if isinstance(response, grpc.RpcError):

                # Return if it was last attempt
                if try_i == (self.max_attempts - 1):
                    return response

                # If status code is not in retryable status codes
                if self.status_for_retry and response.code() not in self.status_for_retry:
                    return response

                self.sleeping_policy.sleep(try_i)
            else:
                return response

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept_call(continuation, client_call_details, request_iterator)


class GrpcClient(metaclass=Singleton):
    def initialize(self, api_key, backend_url):

        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        channel = grpc.secure_channel(
            backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(api_key))
            ),
            options=channel_opt,
        )

        interceptors = (
            RetryOnRpcErrorClientInterceptor(
                max_attempts=4,
                sleeping_policy=ExponentialBackoff(init_backoff_ms=100, max_backoff_ms=1600, multiplier=2),
                status_for_retry=(grpc.StatusCode.UNAVAILABLE,),
            ),
        )

        self.job_stub = backend_pb2_grpc.JobStub(grpc.intercept_channel(channel, *interceptors))
        self.core_stub = backend_pb2_grpc.CoreStub(grpc.intercept_channel(channel, *interceptors))
