#!/usr/bin/python3

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import os
import json
import socket
import struct
import argparse
import sys
import signal
import logging
import ipaddress

log = logging.getLogger(__name__)


def parse_args(parser):
    def in_multi_cast_range(addr):
        def convert_ipv4(addr):
            return tuple(int(n) for n in addr.split("."))

        return (
            convert_ipv4("224.0.0.0") <=
            convert_ipv4(addr) <=
            convert_ipv4("239.255.255.255")
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
                "(choose from 224.0.0.0-239.255.255.255)".format(
                    args.group
                )
            )

            parser.print_help(sys.stderr)

            exit(1)

        if not in_multi_cast_range(args.group):
            log.error(
                "argument -g/--group: invalid choice: '{}' "
                "(choose from 224.0.0.0-239.255.255.255)".format(
                    args.group
                )
            )

            parser.print_help(sys.stderr)

            exit(1)

    if args.port != parser.get_default("p"):
        if args.port not in range(49152, 65536):
            log.error(
                "argument -p/--port: invalid choice: '{}' "
                "(choose from 49152-65535)".format(
                    args.port
                )
            )

            parser.print_help(sys.stderr)

            exit(1)

    if args.ttl != parser.get_default("t"):
        if args.ttl not in range(1, 32):
            log.error(
                "argument -t/--ttl: invalid choice: '{}' "
                "(choose from 1-31)".format(
                    args.ttl
                )
            )

            parser.print_help(sys.stderr)

            exit(1)

    if hasattr(args, "debug"):
        log.setLevel(logging.DEBUG)

        mode = "Send" if args.mode in ("s", "send") else "receive"

        log.debug("Group: {}, Port: {}, TTL: {}, Mode: {}".format(
                args.group,
                args.port,
                args.ttl,
                mode,
            )
        )

    return args.group, args.port, args.ttl, args.mode


def get_event():
    player_event = os.getenv("PLAYER_EVENT")

    if player_event is None or player_event.startswith("sink"):
        exit(0)

    log.debug("PlayerEvent: {}".format(player_event))

    json_dict = {
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
        "preloading",
        "loading",
        "unavailable",
    ):
        json_dict["track_id"] = os.getenv("TRACK_ID") or ""

    elif player_event == "track_changed":
        common_metadata_fields = {}

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
            track_metadata_fields = {}

            track_metadata_fields["number"] = os.getenv("NUMBER")
            track_metadata_fields["disc_number"] = os.getenv("DISC_NUMBER")
            track_metadata_fields["popularity"] = os.getenv("POPULARITY")
            track_metadata_fields["album"] = os.getenv("ALBUM") or ""

            artists = os.getenv("ARTISTS")

            track_metadata_fields["artists"] = (
                artists.split("\n") if artists else []
            )

            album_artists = os.getenv("ALBUM_ARTISTS")

            track_metadata_fields["album_artists"] = (
                album_artists.split("\n") if album_artists else []
            )

            json_dict["track_metadata_fields"] = track_metadata_fields

        elif item_type == "Episode":
            episode_metadata_fields = {}

            episode_metadata_fields["show_name"] = os.getenv("SHOW_NAME") or ""
            # Unix timestamp
            episode_metadata_fields["publish_time"] = os.getenv("PUBLISH_TIME")

            episode_metadata_fields["description"] = (
                os.getenv("DESCRIPTION") or ""
            )

            json_dict["episode_metadata_fields"] = episode_metadata_fields

    log.debug("JSON Dict: {}".format(json_dict))

    return bytes(json.dumps(json_dict), encoding="utf-8")


def get_socket():
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP,
        )

    except Exception as e:
        log.error(e)
        sys.exit(1)

    return sock


def get_send_socket(ttl):
    sock = get_socket()

    try:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        sock.settimeout(0.5)

    except Exception as e:
        log.error(e)
        sys.exit(1)

    return sock


def get_listen_socket(group, port):
    sock = get_socket()

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((group, port))
        mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    except Exception as e:
        log.error(e)
        sys.exit(1)

    return sock


def send_event(group, port, ttl):
    event = get_event()

    with get_send_socket(ttl) as s:
        try:
            # Shout into the void...
            bytes_sent = s.sendto(event, (group, port))
            log.debug("{} Bytes sent of {}".format(bytes_sent, len(event)))

        except socket.timeout:
            log.info("Socket TimeOut")

        except Exception as e:
            log.error(e)
            sys.exit(1)


def listen_for_events(group, port):
    with get_listen_socket(group, port) as s:
        while True:
            try:
                event, addr = s.recvfrom(1024)

                log.debug("{} Bytes received from {}".format(len(event), addr))
                log.debug("Bytes to String: {}".format(
                        event.decode("utf-8", errors="replace")
                    )
                )

                if event:
                    json_data = json.loads(event)
                    # Do interesting things with the json_data.
                    # Or just print it...
                    print(json.dumps(json_data, indent=4))

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
        msg = "[%(asctime)s {color}%(levelname)s\u001b[0m " \
            "%(filename)s:%(funcName)s:%(lineno)d] %(message)s"

        FORMATS = {
            logging.DEBUG: msg.format(color=blue),
            logging.INFO: msg.format(color=green),
            logging.WARNING: msg.format(color=yellow),
            logging.ERROR: msg.format(color=red),
            logging.CRITICAL: msg.format(color=bold_red),
        }

        def format(self, record):
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
        description="Send or Recieve Librespot Events via UDP MultiCast.",
        epilog="librespot --onevent=/path/to/multicast_librespot_events.py "
        "| /path/to/multicast_librespot_events.py -m r",
    )

    parser.add_argument(
        "-g",
        "--group",
        help="Address of the MultiCast Group you would like to "
        "send/receive Events on.",
        type=str,
        metavar="[224.0.0.0-239.255.255.255]",
        default="224.0.0.0",
    )

    parser.add_argument(
        "-p",
        "--port",
        help="Port on the MultiCast Group you would like "
        "to send/receive Events on.",
        type=int,
        metavar="[49152-65535]",
        default=49152,
    )

    parser.add_argument(
        "-t",
        "--ttl",
        help='The TTL (number of "hops") when sending Events.',
        type=int,
        metavar="[1-31]",
        default=2,
    )

    parser.add_argument(
        "-m",
        "--mode",
        help="Send or Receive Events.",
        type=str,
        choices=["s", "send", "r", "receive"],
        metavar="[s, send, r, receive]",
        default="send",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action='store_const',
        metavar=None,
        const=True,
        default=argparse.SUPPRESS,
        help="Enable Debug Logging.",
    )

    group, port, ttl, mode = parse_args(parser)

    if mode in ("s", "send"):
        send_event(group, port, ttl)
    elif mode in ("r", "receive"):
        listen_for_events(group, port)
