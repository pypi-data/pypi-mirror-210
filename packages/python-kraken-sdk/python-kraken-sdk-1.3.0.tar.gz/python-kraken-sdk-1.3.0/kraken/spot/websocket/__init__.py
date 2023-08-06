#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger
#

"""Module that implements the kraken Spot websocket clients"""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
from copy import deepcopy
from random import random
from time import time
from typing import Any, Callable, List, Optional, Union

import websockets

from ...exceptions import KrakenException
from ...spot.ws_client import SpotWsClientCl


class ConnectSpotWebsocket:
    """
    This class is only called by the :class:`kraken.spot.KrakenSpotWSClient`
    to establish and handle a websocket connection.

    :param client: The websocket client that wants to connect
    :type client: :class:`kraken.spot.KrakenSpotWSClient`
    :param endpoint: The websocket endpoint
    :type endpoint: str
    :param callback: Callback function that receives the websocket messages
    :type callback: function
    :param private: If the websocket connects to endpoints that
        require authentication (default: ``False``)
    :type private: bool, optional
    """

    MAX_RECONNECT_NUM: int = 10

    def __init__(
        self: "ConnectSpotWebsocket",
        client: KrakenSpotWSClient,
        endpoint: str,
        callback: Any,
        is_auth: bool = False,
    ):
        self.__client: KrakenSpotWSClient = client
        self.__ws_endpoint: str = endpoint
        self.__callback: Any = callback

        self.__reconnect_num: int = 0
        self.__ws_conn_details: Optional[dict] = None

        self.__is_auth: bool = is_auth

        self.__last_ping: Optional[Union[int, float]] = None
        self.__socket: Optional[Any] = None
        self.__subscriptions: List[dict] = []

        asyncio.ensure_future(self.__run_forever(), loop=asyncio.get_running_loop())

    @property
    def subscriptions(self: "ConnectSpotWebsocket") -> list:
        """Returns the active subscriptions"""
        return self.__subscriptions

    @property
    def is_auth(self: "ConnectSpotWebsocket") -> bool:
        """Returns true if the connection can access privat endpoints"""
        return self.__is_auth

    async def __run(self: "ConnectSpotWebsocket", event: asyncio.Event) -> None:
        keep_alive: bool = True
        self.__last_ping = time()
        self.__ws_conn_details = (
            None if not self.__is_auth else self.__client.get_ws_token()
        )
        logging.debug(f"Websocket token: {self.__ws_conn_details}")

        async with websockets.connect(  # pylint: disable=no-member
            f"wss://{self.__ws_endpoint}", ping_interval=30
        ) as socket:
            logging.info("Websocket connected!")
            self.__socket = socket

            if not event.is_set():
                await self.send_ping()
                event.set()
            self.__reconnect_num = 0

            while keep_alive:
                if time() - self.__last_ping > 10:
                    await self.send_ping()
                try:
                    _msg = await asyncio.wait_for(self.__socket.recv(), timeout=15)
                except asyncio.TimeoutError:  # important
                    await self.send_ping()
                except asyncio.CancelledError:
                    logging.exception("asyncio.CancelledError")
                    keep_alive = False
                    await self.__callback({"error": "asyncio.CancelledError"})
                else:
                    try:
                        msg: dict = json.loads(_msg)
                    except ValueError:
                        logging.warning(_msg)
                    else:
                        if "event" in msg:
                            if msg["event"] == "subscriptionStatus" and "status" in msg:
                                ##      remove and assign un-/subscriptions
                                ##
                                try:
                                    if msg["status"] == "subscribed":
                                        self.__append_subscription(msg)
                                    elif msg["status"] == "unsubscribed":
                                        self.__remove_subscription(msg)
                                    elif msg["status"] == "error":
                                        logging.warning(msg)
                                except AttributeError:
                                    pass
                        await self.__callback(msg)

    async def __run_forever(self: "ConnectSpotWebsocket") -> None:
        try:
            while True:
                await self.__reconnect()
        except KrakenException.MaxReconnectError:
            await self.__callback(
                {"error": "kraken.exceptions.KrakenException.MaxReconnectError"}
            )
        except Exception as exc:
            logging.error(f"{exc}: {traceback.format_exc()}")
        finally:
            self.__client.exception_occur = True

    async def __reconnect(self: "ConnectSpotWebsocket") -> None:
        logging.info("Websocket start connect/reconnect")

        self.__reconnect_num += 1
        if self.__reconnect_num >= self.MAX_RECONNECT_NUM:
            raise KrakenException.MaxReconnectError()

        reconnect_wait: float = self.__get_reconnect_wait(self.__reconnect_num)
        logging.debug(
            f"asyncio sleep reconnect_wait={reconnect_wait} s reconnect_num={self.__reconnect_num}"
        )
        await asyncio.sleep(reconnect_wait)
        logging.debug("asyncio sleep done")
        event: asyncio.Event = asyncio.Event()

        tasks: dict = {
            asyncio.ensure_future(
                self.__recover_subscriptions(event)
            ): self.__recover_subscriptions,
            asyncio.ensure_future(self.__run(event)): self.__run,
        }

        while set(tasks.keys()):
            finished, pending = await asyncio.wait(
                tasks.keys(), return_when=asyncio.FIRST_EXCEPTION
            )
            exception_occur: bool = False
            for task in finished:
                if task.exception():
                    exception_occur = True
                    traceback.print_stack()
                    message: str = f"{task} got an exception {task.exception()}\n {task.get_stack()}"
                    logging.warning(message)
                    for process in pending:
                        logging.warning(f"pending {process}")
                        try:
                            process.cancel()
                        except asyncio.CancelledError:
                            logging.exception("asyncio.CancelledError")
                        logging.warning("Cancel OK")
                    await self.__callback({"error": message})
            if exception_occur:
                break
        logging.warning("reconnect over")

    async def __recover_subscriptions(
        self: "ConnectSpotWebsocket", event: asyncio.Event
    ) -> None:
        logging.info(
            f'Recover {"auth" if self.__is_auth else "public"} subscriptions {self.__subscriptions} waiting.'
        )
        await event.wait()

        for sub in self.__subscriptions:
            cpy = deepcopy(sub)
            private = False
            if (
                "subscription" in sub
                and "name" in sub["subscription"]
                and sub["subscription"]["name"] in self.__client.private_sub_names
            ):
                cpy["subscription"]["token"] = self.__ws_conn_details["token"]
                private = True
            await self.send_message(cpy, private=private)
            logging.info(f"{sub} OK")

        logging.info(
            f'Recovering {"auth" if self.__is_auth else "public"} subscriptions {self.__subscriptions} done.'
        )

    async def send_ping(self: "ConnectSpotWebsocket") -> None:
        """Sends ping to Kraken"""
        await self.__socket.send(
            json.dumps(
                {
                    "event": "ping",
                    "reqid": int(time() * 1000),
                }
            )
        )
        self.__last_ping = time()

    async def send_message(
        self: "ConnectSpotWebsocket", msg: dict, private: Optional[bool] = False
    ) -> None:
        """
        Sends a message via websocket

        :param msg: The content to send
        :type msg: dict
        :param private: Use authentication (default: ``False``)
        :type private: bool, optional
        """
        if private and not self.__is_auth:
            raise ValueError("Cannot send private message with public websocket.")

        while not self.__socket:
            await asyncio.sleep(0.4)

        msg["reqid"] = int(time() * 1000)
        if private and "subscription" in msg:
            msg["subscription"]["token"] = self.__ws_conn_details["token"]
        elif private:
            msg["token"] = self.__ws_conn_details["token"]
        await self.__socket.send(json.dumps(msg))

    def __append_subscription(self: "ConnectSpotWebsocket", msg: dict) -> None:
        """
        Add a dictionary containing subscription information to list
        This is used to recover when the connection gets interrupted.

        :param msg: The subscription
        :type msg: dict

        This function should only be called in
        when self.__run receives a msg and the following conditions met:
        - ``msg.get("event") == "subscriptionStatus"```
        - ``msg.get("status") == "subscribed"``
        """
        self.__remove_subscription(msg)  # remove from list, to avoid duplicate entries
        self.__subscriptions.append(self.__build_subscription(msg))

    def __remove_subscription(self: "ConnectSpotWebsocket", msg: dict) -> None:
        """
        Remove a dictionary containing subscription information from list.

        :param msg: The subscription to remove
        :type msg: dict

        This function should only be called in
        when self.__run receives a msg and the following conditions met:
        - ``msg.get("event") == "subscriptionStatus"```
        - ``msg.get("status") == "unsubscribed"``
        """
        sub: dict = self.__build_subscription(msg)
        self.__subscriptions = [x for x in self.__subscriptions if x != sub]

    def __build_subscription(self: "ConnectSpotWebsocket", msg: dict) -> dict:
        sub: dict = {"event": "subscribe"}

        if not "subscription" in msg or "name" not in msg["subscription"]:
            raise ValueError("Cannot remove subscription with missing attributes.")
        if (
            msg["subscription"]["name"] in self.__client.public_sub_names
        ):  # public endpoint
            if "pair" in msg:
                sub["pair"] = (
                    msg["pair"] if isinstance(msg["pair"], list) else [msg["pair"]]
                )
            sub["subscription"] = msg["subscription"]
        elif (
            msg["subscription"]["name"] in self.__client.private_sub_names
        ):  # private endpoint
            sub["subscription"] = {"name": msg["subscription"]["name"]}
        else:
            logging.warning(
                "Feed not implemented. Please contact the python-kraken-sdk package author."
            )
        return sub

    def __get_reconnect_wait(self, attempts: int) -> Union[float, Any]:
        return round(random() * min(60 * 3, (2**attempts) - 1) + 1)


class KrakenSpotWSClient(SpotWsClientCl):
    """
    Class to access public and (optional)
    private/authenticated websocket connection.

    - https://docs.kraken.com/websockets/#overview

    This class holds up to two websocket connections, one private
    and one public.

    When accessing private endpoints that need authentication make sure,
    that the ``Access WebSockets API`` API key permission is set in the user's
    account.

    :param key: API Key for the Kraken Spot API (default: ``""``)
    :type key: str, optional
    :param secret: Secret API Key for the Kraken Spot API (default: ``""``)
    :type secret: str, optional
    :param url: Set a specific/custom url to access the Kraken API
    :type url: str, optional
    :param beta: Use the beta websocket channels (maybe not supported anymore, default: ``False``)
    :type beta: bool

    .. code-block:: python
        :linenos:
        :caption: HowTo: Create a Bot and integrate the python-kraken-sdk Spot Websocket Client

        import asyncio
        from kraken.spot import KrakenSpotWSClient

        async def main() -> None:
            class Bot(KrakenSpotWSClient):

                async def on_message(self, event: dict) -> None:
                    print(event)

            bot = Bot()         # unauthenticated
            auth_bot = Bot(     # authenticated
                key='kraken-api-key',
                secret='kraken-secret-key'
            )

            # subscribe to the desired feeds:
            await bot.subscribe(
                subscription={"name": ticker},
                pair=["XBTUSD", "DOT/EUR"]
            )
            # from now on the on_message function receives the ticker feed

            while True:
                await asyncio.sleep(6)

        if __name__ == '__main__':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                loop.close()

    .. code-block:: python
        :linenos:
        :caption: HowTo: Use the websocket client as context manager

        import asyncio
        from kraken.spot import KrakenSpotWSClient

        async def on_message(msg):
            print(msg)

        async def main() -> None:
            async with KrakenSpotWSClient(
                key="api-key",
                secret="secret-key",
                callback=on_message
            ) as session:
                await session.subscribe(
                    subscription={"name": "ticker"},
                    pair=["XBT/USD"]
                )

            while True:
                await asyncio.sleep(6)


        if __name__ == "__main__":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass
            finally:
                loop.close()
    """

    PROD_ENV_URL: str = "ws.kraken.com"
    AUTH_PROD_ENV_URL: str = "ws-auth.kraken.com"
    BETA_ENV_URL: str = "beta-ws.kraken.com"
    AUTH_BETA_ENV_URL: str = "beta-ws-auth.kraken.com"

    def __init__(
        self: "KrakenSpotWSClient",
        key: str = "",
        secret: str = "",
        url: str = "",
        callback: Optional[Callable] = None,
        beta: bool = False,
    ):
        super().__init__(key=key, secret=secret, url=url, sandbox=beta)
        self.__callback: Any = callback
        self.__is_auth: bool = bool(key and secret)
        self.exception_occur: bool = False
        self._pub_conn: ConnectSpotWebsocket = ConnectSpotWebsocket(
            client=self,
            endpoint=self.PROD_ENV_URL if not beta else self.BETA_ENV_URL,
            is_auth=False,
            callback=self.on_message,
        )

        self._priv_conn: Optional[ConnectSpotWebsocket] = (
            ConnectSpotWebsocket(
                client=self,
                endpoint=self.AUTH_PROD_ENV_URL if not beta else self.AUTH_BETA_ENV_URL,
                is_auth=True,
                callback=self.on_message,
            )
            if self.__is_auth
            else None
        )

    async def on_message(self: "KrakenSpotWSClient", msg: dict) -> None:
        """
        Calls the defined callback function (if defined)
        or overload this function.

        Can be overloaded as described in :class:`kraken.spot.KrakenSpotWSClient`

        :param msg: The message received sent by Kraken via the websocket connection
        :type msg: dict
        """
        if self.__callback is not None:
            await self.__callback(msg)
        else:
            logging.warning("Received event but no callback is defined.")
            print(msg)

    async def subscribe(
        self: "KrakenSpotWSClient", subscription: dict, pair: List[str] = None
    ) -> None:
        """
        Subscribe to a channel

        Success or failures are sent over the websocket connection and can be
        received via the on_message callback function.

        When accessing private endpoints and subscription feeds that need authentication
        make sure, that the ``Access WebSockets API`` API key permission is set
        in the users Kraken account.

        - https://docs.kraken.com/websockets-beta/#message-subscribe

        :param subscription: The subscription message
        :type subscription: dict
        :param pair: The pair to subscribe to
        :type pair: List[str] | None, optional

        Initialize your client as described in :class:`kraken.spot.KrakenSpotWSClient` to
        run the following example:

        .. code-block:: python
            :linenos:
            :caption: Spot Websocket: Subscribe to a websocket feed

            >>> await bot.subscribe(
            ...     subscription={"name": ticker},
            ...     pair=["XBTUSD", "DOT/EUR"]
            ... )
        """

        if "name" not in subscription:
            raise AttributeError('Subscription requires a "name" key."')
        private: bool = bool(subscription["name"] in self.private_sub_names)

        payload: dict = {"event": "subscribe", "subscription": subscription}
        if pair is not None:
            if not isinstance(pair, list):
                raise ValueError(
                    'Parameter pair must be type of List[str] (e.g. pair=["XBTUSD"])'
                )
            payload["pair"] = pair

        if private:  # private == without pair
            if not self.__is_auth:
                raise ValueError(
                    "Cannot subscribe to private feeds without valid credentials!"
                )
            if pair is not None:
                raise ValueError(
                    "Cannot subscribe to private endpoint with specific pair!"
                )
            await self._priv_conn.send_message(payload, private=True)

        elif pair is not None:  # public with pair
            for symbol in pair:
                sub = deepcopy(payload)
                sub["pair"] = [symbol]
                await self._pub_conn.send_message(sub, private=False)

        else:
            await self._pub_conn.send_message(payload, private=False)

    async def unsubscribe(
        self: "KrakenSpotWSClient", subscription: dict, pair: Optional[List[str]] = None
    ) -> None:
        """
        Unsubscribe from a topic

        Success or failures are sent over the websocket connection and can be
        received via the on_message callback function.

        When accessing private endpoints and subscription feeds that need authentication
        make sure, that the ``Access WebSockets API`` API key permission is set
        in the users Kraken account.

        - https://docs.kraken.com/websockets/#message-unsubscribe

        :param subscription: The subscription to unsubscribe from
        :type subscription: dict
        :param pair: The pair or list of pairs to unsubscribe
        :type pair: List[str], optional

        Initialize your client as described in :class:`kraken.spot.KrakenSpotWSClient` to
        run the following example:

        .. code-block:: python
            :linenos:
            :caption: Spot Websocket: Unsubscribe from a websocket feed

            >>> await bot.unsubscribe(
            ...     subscription={"name": ticker},
            ...     pair=["XBTUSD", "DOT/EUR"]
            ... )
        """
        if "name" not in subscription:
            raise AttributeError('Subscription requires a "name" key."')
        private: bool = bool(subscription["name"] in self.private_sub_names)

        payload: dict = {"event": "unsubscribe", "subscription": subscription}
        if pair is not None:
            if not isinstance(pair, list):
                raise ValueError(
                    'Parameter pair must be type of List[str] (e.g. pair=["XBTUSD"])'
                )
            payload["pair"] = pair

        if private:  # private == without pair
            if not self.__is_auth:
                raise ValueError(
                    "Cannot unsubscribe from private feeds without valid credentials!"
                )
            if pair is not None:
                raise ValueError(
                    "Cannot unsubscribe from private endpoint with specific pair!"
                )
            await self._priv_conn.send_message(payload, private=True)

        elif pair is not None:  # public with pair
            for symbol in pair:
                sub = deepcopy(payload)
                sub["pair"] = [symbol]
                await self._pub_conn.send_message(sub, private=False)

        else:
            await self._pub_conn.send_message(payload, private=False)

    @property
    def private_sub_names(self: "KrakenSpotWSClient") -> List[str]:
        """
        Returns the private subscription names

        :return: List of private subscription names (``ownTrades``, ``openOrders``)
        :rtype: List[str]
        """
        return ["ownTrades", "openOrders"]

    @property
    def public_sub_names(self: "KrakenSpotWSClient") -> List[str]:
        """
        Returns the public subscription names

        :return: List of public subscription names (``ticker``,
         ``spread``, ``book``, ``ohlc``, ``trade``, ``*``)
        :rtype: List[str]
        """
        return ["ticker", "spread", "book", "ohlc", "trade", "*"]

    @property
    def active_public_subscriptions(
        self: "KrakenSpotWSClient",
    ) -> Union[List[dict], Any]:
        """
        Returns the active public subscriptions

        :return: List of active public subscriptions
        :rtype: Union[List[dict], Any]
        :raises ConnectionError: If there is no public connection.
        """
        if self._pub_conn is not None:
            return self._pub_conn.subscriptions
        raise ConnectionError("Public connection does not exist!")

    @property
    def active_private_subscriptions(
        self: "KrakenSpotWSClient",
    ) -> Union[List[dict], Any]:
        """
        Returns the active private subscriptions

        :return: List of active private subscriptions
        :rtype: Union[List[dict], Any]
        :raises ConnectionError: If there is no private connection
        """
        if self._priv_conn is not None:
            return self._priv_conn.subscriptions
        raise ConnectionError("Private connection does not exist!")

    async def __aenter__(self: "KrakenSpotWSClient") -> "KrakenSpotWSClient":
        return self

    async def __aexit__(self, *exc: tuple, **kwargs: dict) -> None:
        pass
