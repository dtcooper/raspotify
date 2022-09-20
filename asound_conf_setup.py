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

import subprocess
import os
import time

BOLD = "\033[1m"
CYAN = "\u001b[36m"
BOLD_RED = "\x1b[31;1m"
RESET = "\u001b[0m"

ASOUND_FILE_PATH = "/etc/asound.conf"
DUMMY_FILE_PATH = "/etc/foobarbaz{}".format(int(time.time()))
BACKUP_FILE_PATH = "/etc/asound.conf.bak{}".format(int(time.time()))

COMMON_FORMATS = [
    "S16_LE",
    "S16_BE",
    "S24_LE",
    "S24_BE",
    "S24_3LE",
    "S24_3BE",
    "S32_LE",
    "S32_BE",
]

COMMON_RATES = [
    8000,
    11025,
    16000,
    22050,
    44100,
    48000,
    88200,
    96000,
    176400,
    192000,
    352800,
    384000,
]


def stylize_input(text):
    return f"{BOLD}{text}{RESET}"


def stylize_error(text):
    return f"{BOLD_RED}{text}{RESET}"


def stylize_comment(text):
    return f"{CYAN}{text}{RESET}"


def print_table_row(text, num, width, padding, justify, print_line):
    if justify is None:
        pad = int(padding / 2)
        row = f"{{:<{pad}}}{{:^{width}}}{{:>{pad}}}".format("|", text, "|")

    else:
        if justify == "left":
            j = "<"

        else:
            j = ">"

        center_pad = int(padding / 2)
        pad = int(center_pad / 2)
        row = f"{{:<{pad}}}{{:<{center_pad}}}{{:{j}{width}}}{{:>{pad}}}".format(
            "|", num, text, "|"
        )

    print(row)

    if print_line:
        line = "-" * (width + padding)
        print(line)


def print_table_header(title, width, padding):
    line = "-" * (width + padding)
    print(line)
    print_table_row(title, "", width, padding, None, True)


def privilege_check():
    try:
        open(DUMMY_FILE_PATH, "w").close()
        os.remove(DUMMY_FILE_PATH)

    except:
        e = stylize_error("Error: This script requires write privileges to /etc.")
        print(e)
        raise SystemExit(1)


def backup_asound_conf():
    try:
        os.rename(ASOUND_FILE_PATH, BACKUP_FILE_PATH)

    except FileNotFoundError:
        pass

    except Exception as e:
        e = stylize_error(f"Error renaming existing {ASOUND_FILE_PATH}: {e}")
        print(e)
        raise SystemExit(1)

    else:
        comment = stylize_comment(
            f"{ASOUND_FILE_PATH} already exists renaming it to: {BACKUP_FILE_PATH}\n"
        )

        print(comment)


def revert_asound_conf():
    try:
        os.rename(BACKUP_FILE_PATH, ASOUND_FILE_PATH)

    except:
        pass


def get_all_pcm_name():
    return (
        subprocess.run(
            ["aplay", "-L"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        .stdout.decode("utf-8")
        .split("\n")
    )


def get_hw_pcm_names():
    all_pcm_name = get_all_pcm_name()

    hw_pcm_names = [
        [n.strip(), all_pcm_name[i + 1].strip()]
        for i, n in enumerate(all_pcm_name)
        if n.startswith("hw:")
    ]

    if not hw_pcm_names:
        print("\n".join(all_pcm_name))
        e = stylize_error("No available hw PCM")
        print(e)
        raise SystemExit(1)

    return hw_pcm_names


def invalid_choice(len_choices):
    e = stylize_error(f"Enter a number from 1 - {len_choices}.\n")
    print(e)


def choose_hw_pcm(hw_pcm_names):
    if len(hw_pcm_names) > 1:
        title = "Available hw PCMs"
        width = max(len(max([n for s in hw_pcm_names for n in s], key=len)), len(title))
        print_table_header(title, width, 8)

        for i, pcm in enumerate(hw_pcm_names):
            [name, desc] = pcm
            print_table_row(name, i + 1, width, 8, "left", False)
            print_table_row(desc, "", width, 8, "left", True)

        print("")

        while True:
            try:
                choice = input(
                    stylize_input("Please choose the hw PCM you wish to use: ")
                )

                print("")
                pcm = hw_pcm_names[int(choice) - 1][0]

            except KeyboardInterrupt:
                print("")
                raise SystemExit(0)

            except:
                invalid_choice(len(hw_pcm_names))
                continue

            else:
                break

    else:
        pcm = hw_pcm_names[0][0]
        comment = stylize_comment(
            f"{pcm} is the only available hw PCM so that's what we'll use…\n"
        )

        print(comment)

    return pcm


def get_formats_and_rates(pcm):
    hw_params = subprocess.run(
        [
            "aplay",
            f"-D{pcm}",
            "--dump-hw-params",
            "/usr/share/sounds/alsa/Front_Right.wav",
        ],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    formats = []
    rates = []

    for line in hw_params.split("\n"):
        if line.startswith("FORMAT:"):
            line = line.strip("FORMAT: ")

            for format_ in line.split(" "):
                format_.strip()

                if format_ in COMMON_FORMATS:
                    formats.append(format_)

        elif line.startswith("RATE:"):
            line = line.strip("RATE:[ ]")

            for line in line.split(" "):
                try:
                    rates.append(int(line.strip()))

                except:
                    pass

    return formats, rates


def choose_format(formats):
    if len(formats) > 1:
        title = "Supported Formats"
        width = max(len(max(formats, key=len)), len(title))
        print_table_header(title, width, 8)

        for i, format_ in enumerate(formats):
            print_table_row(format_, i + 1, width, 8, "right", True)

        comment = stylize_comment(
            "\nIt's generally advised to choose the highest bit depth format that your device supports.\n"
        )

        print(comment)

        while True:
            try:
                choice = input(
                    stylize_input("Please choose the desired supported format: ")
                )

                print("")
                format_ = formats[int(choice) - 1]

            except KeyboardInterrupt:
                print("")
                raise SystemExit(0)

            except:
                invalid_choice(len(formats))
                continue

            else:
                break

    else:
        format_ = formats[0]

        comment = stylize_comment(
            f"{format_} is the only supported format so that's what we'll use…\n"
        )

        print(comment)

    return format_


def choose_rate(rates):
    if len(rates) > 1:
        r_range = range(rates[0], rates[-1] + 1)
        rates = [r for r in COMMON_RATES if r in r_range]
        title = "Supported Sampling Rates"
        width = max(len(max([str(r) for r in rates], key=len)), len(title))
        print_table_header(title, width, 8)

        for i, rate in enumerate(rates):
            print_table_row(rate, i + 1, width, 8, "right", True)

        comment = stylize_comment(
            "\nStandard CD quality is 44100.\n\n"
            "An unnecessarily high sampling rate can lead to high CPU usage,\n"
            "degraded audio quality, and audio dropouts and glitches on low spec devices.\n"
            "Unless the music you normally listen to is a higher sampling rate,\n"
            "44100 (or as close as you can get to it) is the best choice.\n"
        )

        print(comment)

        while True:
            try:
                choice = input(
                    stylize_input("Please choose the desired supported sampling rate: ")
                )

                print("")
                rate = rates[int(choice) - 1]

            except KeyboardInterrupt:
                print("")
                raise SystemExit(0)

            except:
                invalid_choice(len(rates))
                continue

            else:
                break

    else:
        rate = rates[0]

        comment = stylize_comment(
            f"{rate} is the only supported sampling rate so that's what we'll use…\n"
        )

        print(comment)

        if rate > 48000:
            comment = stylize_comment(
                "High sampling rates can lead to high CPU usage, degraded audio quality,\n"
                "and audio dropouts and glitches on low spec devices.\n"
            )

            print(comment)

    return rate


def pcm_to_card_device(pcm):
    try:
        [card, device] = pcm.split(",")
        card = card.replace("hw:CARD=", "").strip()
        device = int(device.strip("DEV= "))

    except Exception as e:
        e = stylize_error(f"Error parsing card and device: {e}")
        print(e)
        raise SystemExit(1)

    return card, device


def get_choices():
    hw_pcm_names = get_hw_pcm_names()

    while True:
        try:
            pcm = choose_hw_pcm(hw_pcm_names)
            formats, rates = get_formats_and_rates(pcm)

            if not formats or not rates:
                e = stylize_error(
                    "No supported formats or sampling rates were returned.\n"
                    "The hw PCM you chose may be busy or not support any common formats and rates?\n"
                    "Make sure it's not in use and try again.\n"
                )

                print(e)
                continue

            else:
                format_ = choose_format(formats)
                rate = choose_rate(rates)
                card, device = pcm_to_card_device(pcm)
                return card, device, format_, rate

        except KeyboardInterrupt:
            print("")
            raise SystemExit(0)


def write_asound_conf():
    privilege_check()

    comment = stylize_comment(
        f"This script will backup {ASOUND_FILE_PATH} if it already exists,\n"
        f"and create a new {ASOUND_FILE_PATH} based on your choices.\n"
    )

    print(comment)

    try:
        choice = input(stylize_input("Enter OK to continue: "))

        if choice.lower() != "ok":
            print("")
            raise SystemExit(0)

        print("")

    except KeyboardInterrupt:
        print("")
        raise SystemExit(0)

    card, device, format_, rate = get_choices()

    file_data = f"""# /etc/asound.conf

pcm.!default {{
    type plug
    slave.pcm {{
        type dmix
        ipc_key {{
            @func refer
            name defaults.pcm.ipc_key
        }}
        ipc_gid {{
            @func refer
            name defaults.pcm.ipc_gid
        }}
        ipc_perm {{
            @func refer
            name defaults.pcm.ipc_perm
        }}
        slave {{
            pcm {{
                type hw
                card {card}
                device {device}
                nonblock {{
                    @func refer
                    name defaults.pcm.nonblock
                }}
            }}
            channels 2
            rate {rate}
            format {format_}
        }}
        bindings {{
            0 0
            1 1
        }}
    }}
}}

ctl.!default {{
    type hw
    card {card}
}}"""

    backup_asound_conf()

    try:
        with open(ASOUND_FILE_PATH, "w") as f:
            f.write(file_data)

    except Exception as e:
        print(stylize_error(f"Error: {e}"))
        revert_asound_conf()
        raise SystemExit(1)

    else:
        comment = stylize_comment(
            f"Using Card: {card}, Device: {device}, Format: {format_}, and Sampling Rate: {rate},\n"
            f"{ASOUND_FILE_PATH} was written successfully.\n\n"
            "Please verify that it is correct."
        )

        print(comment)


if __name__ == "__main__":
    write_asound_conf()

