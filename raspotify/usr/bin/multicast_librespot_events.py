#!/usr/bin/python3

"""
This script sends Librespot events via UDP Multicast. It retrieves player event data
from environment variables and formats it into JSON. The JSON data is then sent to the
specified multicast group and port using a UDP socket.

Usage:
    librespot --onevent=/path/to/multicast_librespot_events.py

Command-line arguments:
    -g/--group (str): Address of the MultiCast Group you would like to send events on.
        Defaults to '224.0.0.0'.
    -p/--port (int): Port on the MultiCast Group you would like to send events on.
        Defaults to 49152.
    -t/--ttl (int): The TTL (number of "hops") when sending events. Defaults to 2.
    -d/--debug: Enable Debug Logging.

Module Dependencies:
    - os
    - json
    - socket
    - argparse
    - sys
    - signal
    - logging
    - ipaddress
"""

import os
import json
import socket
import argparse
import sys
import signal
import logging
import ipaddress

log = logging.getLogger(__name__)

DEFAULT_GROUP = "224.0.0.0"
MAX_GROUP = "239.255.255.255"
DEFAULT_PORT = 49152
MAX_PORT = 65535
PORT_RANGE = range(49152, 65536)
DEFAULT_TTL = 2
MIN_TTL = 1
MAX_TTL = 31
TTL_RANGE = range(1, 32)
SOCKET_TIMEOUT = 0.5


def parse_args(parser: argparse.ArgumentParser) -> tuple[str, int, int]:
    """
    Parse command-line arguments and validate their values.

    Parameters:
        parser (argparse.ArgumentParser): ArgumentParser instance to parse the arguments.

    Returns:
        tuple[str, int, int]: A tuple containing the group (address), port, and TTL values.
    """

    def in_multi_cast_range(addr: str) -> bool:
        def convert_ipv4(addr: str) -> tuple[int, ...]:
            return tuple(int(n) for n in addr.split("."))

        return (
            convert_ipv4(DEFAULT_GROUP) <= convert_ipv4(addr) <= convert_ipv4(MAX_GROUP)
        )

    try:
        args, unknown = parser.parse_known_args()

        if unknown:
            log.error("unrecognized arguments: '{}'".format(" ".join(unknown)))
            parser.print_help(sys.stderr)
            exit(1)

    except argparse.ArgumentError as e:
        log.error(e)
        parser.print_help(sys.stderr)
        exit(1)

    if args.group != parser.get_default("g"):
        try:
            ipaddress.ip_address(args.group)
        except ValueError:
            log.error(
                "argument -g/--group: invalid choice: '{}' "
                "(choose from {}-{})".format(args.group, DEFAULT_GROUP, MAX_GROUP)
            )

            parser.print_help(sys.stderr)

            exit(1)

        if not in_multi_cast_range(args.group):
            log.error(
                "argument -g/--group: invalid choice: '{}' "
                "(choose from {}-{})".format(args.group, DEFAULT_GROUP, MAX_GROUP)
            )

            parser.print_help(sys.stderr)

            exit(1)

    if args.port != parser.get_default("p"):
        if args.port not in PORT_RANGE:
            log.error(
                "argument -p/--port: invalid choice: '{}' "
                "(choose from {}-{})".format(args.port, DEFAULT_PORT, MAX_PORT)
            )

            parser.print_help(sys.stderr)

            exit(1)

    if args.ttl != parser.get_default("t"):
        if args.ttl not in TTL_RANGE:
            log.error(
                "argument -t/--ttl: invalid choice: '{}' "
                "(choose from {}-{})".format(args.ttl, MIN_TTL, MAX_TTL)
            )

            parser.print_help(sys.stderr)

            exit(1)

    if hasattr(args, "debug"):
        log.setLevel(logging.DEBUG)

        log.debug(
            "Group: {}, Port: {}, TTL: {}".format(
                args.group,
                args.port,
                args.ttl,
            )
        )

    return args.group, args.port, args.ttl


def get_event() -> bytes:
    """
    Get the player event data from environment variables and format it into a JSON string.

    Returns:
        bytes: JSON-formatted player event data.
    """

    player_event: str | None = os.getenv("PLAYER_EVENT")

    if player_event is None or player_event.startswith("sink"):
        exit(0)

    log.debug("PlayerEvent: {}".format(player_event))

    json_dict: dict[
        str, None | str | dict[str, None | str] | dict[str, None | str | list[str]]
    ] = {
        "event": player_event,
    }

    # Invalid bools and numbers are left as null.
    # Invalid strings are substituted with an empty string.
    # Invalid arrays are replaced with an empty array.
    if player_event in ("session_connected", "session_disconnected"):
        json_dict["user_name"] = os.getenv("USER_NAME") or ""
        json_dict["connection_id"] = os.getenv("CONNECTION_ID") or ""

    elif player_event == "session_client_changed":
        json_dict["client_id"] = os.getenv("CLIENT_ID") or ""
        json_dict["client_name"] = os.getenv("CLIENT_NAME") or ""
        json_dict["client_brand_name"] = os.getenv("CLIENT_BRAND_NAME") or ""
        json_dict["client_model_name"] = os.getenv("CLIENT_MODEL_NAME") or ""

    elif player_event == "shuffle_changed":
        json_dict["shuffle"] = os.getenv("SHUFFLE")

    elif player_event == "repeat_changed":
        json_dict["repeat"] = os.getenv("REPEAT")

    elif player_event == "auto_play_changed":
        json_dict["auto_play"] = os.getenv("AUTO_PLAY")

    elif player_event == "filter_explicit_content_changed":
        json_dict["filter"] = os.getenv("FILTER")

    elif player_event == "volume_changed":
        json_dict["volume"] = os.getenv("VOLUME")

    elif player_event in (
        "seeked",
        "position_correction",
        "playing",
        "paused",
    ):
        json_dict["track_id"] = os.getenv("TRACK_ID") or ""
        json_dict["position_ms"] = os.getenv("POSITION_MS")

    elif player_event in (
        "end_of_track",
        "stopped",
        "preload_next",
        "loading",
        "unavailable",
    ):
        json_dict["track_id"] = os.getenv("TRACK_ID") or ""

    elif player_event in ("track_changed", "preloading"):
        common_metadata_fields: dict[str, None | str | list[str]] = {}

        item_type = os.getenv("ITEM_TYPE") or ""
        common_metadata_fields["item_type"] = item_type
        common_metadata_fields["track_id"] = os.getenv("TRACK_ID") or ""
        common_metadata_fields["uri"] = os.getenv("URI") or ""
        common_metadata_fields["name"] = os.getenv("NAME") or ""
        common_metadata_fields["duration_ms"] = os.getenv("DURATION_MS")
        common_metadata_fields["is_explicit"] = os.getenv("IS_EXPLICIT")

        langs = os.getenv("LANGUAGE")

        common_metadata_fields["language"] = langs.split("\n") if langs else []

        covers = os.getenv("COVERS")

        common_metadata_fields["covers"] = covers.split("\n") if covers else []

        json_dict["common_metadata_fields"] = common_metadata_fields

        if item_type == "Track":
            track_metadata_fields: dict[str, None | str | list[str]] = {}

            track_metadata_fields["number"] = os.getenv("NUMBER")
            track_metadata_fields["disc_number"] = os.getenv("DISC_NUMBER")
            track_metadata_fields["popularity"] = os.getenv("POPULARITY")
            track_metadata_fields["album"] = os.getenv("ALBUM") or ""

            artists = os.getenv("ARTISTS")

            track_metadata_fields["artists"] = artists.split("\n") if artists else []

            album_artists = os.getenv("ALBUM_ARTISTS")

            track_metadata_fields["album_artists"] = (
                album_artists.split("\n") if album_artists else []
            )

            json_dict["track_metadata_fields"] = track_metadata_fields

        elif item_type == "Episode":
            episode_metadata_fields: dict[str, None | str] = {}

            episode_metadata_fields["show_name"] = os.getenv("SHOW_NAME") or ""
            # Unix timestamp
            episode_metadata_fields["publish_time"] = os.getenv("PUBLISH_TIME")

            episode_metadata_fields["description"] = os.getenv("DESCRIPTION") or ""

            json_dict["episode_metadata_fields"] = episode_metadata_fields

    log.debug("JSON Dict: {}".format(json_dict))

    return bytes(json.dumps(json_dict), encoding="utf-8")


def get_send_socket(ttl: int) -> socket.socket:
    """
    Create and configure a UDP multicast socket for sending events.

    Parameters:
        ttl (int): Time to live (TTL) value for the socket.

    Returns:
        socket.socket: A configured UDP multicast socket.
    """

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP,
        )

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        sock.settimeout(SOCKET_TIMEOUT)

    except Exception as e:
        log.error(e)
        sys.exit(1)

    return sock


def send_event(group: str, port: int, ttl: int) -> None:
    """
    Send the player event data to the specified multicast group and port.

    Parameters:
        group (str): The multicast group address to send the data to.
        port (int): The port on the multicast group to send the data to.
        ttl (int): Time to live (TTL) value for the socket.
    """

    event: bytes = get_event()

    with get_send_socket(ttl) as s:
        try:
            # Shout into the void...
            bytes_sent: int = s.sendto(event, (group, port))
            log.debug("{} Bytes sent of {}".format(bytes_sent, len(event)))

        except socket.timeout:
            log.info("Socket TimeOut")

        except Exception as e:
            log.error(e)
            sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *args, **kwargs: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *args, **kwargs: sys.exit(0))

    class ColorFormatter(logging.Formatter):
        blue = "\u001b[34m"
        green = "\u001b[32m"
        yellow = "\u001b[33m"
        red = "\u001b[31m"
        bold_red = "\x1b[31;1m"

        # reset = "\u001b[0m"
        msg = (
            "[%(asctime)s {color}%(levelname)s\u001b[0m "
            "%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
        )

        FORMATS = {
            logging.DEBUG: msg.format(color=blue),
            logging.INFO: msg.format(color=green),
            logging.WARNING: msg.format(color=yellow),
            logging.ERROR: msg.format(color=red),
            logging.CRITICAL: msg.format(color=bold_red),
        }

        def format(self, record: logging.LogRecord) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(ColorFormatter())
    log.addHandler(handler)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        exit_on_error=False,
        description="Send Librespot Events via UDP MultiCast.",
        epilog="librespot --onevent=/path/to/multicast_librespot_events.py",
    )

    parser.add_argument(
        "-g",
        "--group",
        help="Address of the MultiCast Group you would like to send Events on.",
        type=str,
        metavar="[{}-{}]".format(DEFAULT_GROUP, MAX_GROUP),
        default=DEFAULT_GROUP,
    )

    parser.add_argument(
        "-p",
        "--port",
        help="Port on the MultiCast Group you would like to send Events on.",
        type=int,
        metavar="[{}-{}]".format(DEFAULT_PORT, MAX_PORT),
        default=DEFAULT_PORT,
    )

    parser.add_argument(
        "-t",
        "--ttl",
        help='The TTL (number of "hops") when sending Events.',
        type=int,
        metavar="[{}-{}]".format(MIN_TTL, MAX_TTL),
        default=DEFAULT_TTL,
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        metavar=None,
        const=True,
        default=argparse.SUPPRESS,
        help="Enable Debug Logging.",
    )

    send_event(*parse_args(parser))
