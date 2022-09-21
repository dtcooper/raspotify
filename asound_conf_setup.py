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
import glob

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


class Stylize:
    _BOLD = "\033[1m"
    _CYAN = "\u001b[36m"
    _BOLD_RED = "\x1b[31;1m"
    _RESET = "\u001b[0m"

    @staticmethod
    def input(text):
        return f"{Stylize._BOLD}{text}{Stylize._RESET}"

    @staticmethod
    def error(text):
        print(f"{Stylize._BOLD_RED}{text}{Stylize._RESET}")

    @staticmethod
    def comment(text):
        print(f"{Stylize._CYAN}{text}{Stylize._RESET}")


class Table:
    def __init__(self, title, width, padding=8):
        self._width = width
        self._padding = padding
        tp_center = "\u2550" * (width + (padding - 2))
        c_center = "\u2500" * (width + (padding - 2))
        self._top_line = "\u2554" + tp_center + "\u2557"
        self._title_bottom_line = "\u2560" + tp_center + "\u2563"
        self._center_line = "\u255F" + c_center + "\u2562"
        self._bottom_line = "\u255A" + tp_center + "\u255D"
        self._table = []
        self._add_table_header(title)

    def add_pcms(self, pcms):
        pcm_len = len(pcms)

        for i, pcm in enumerate(pcms):
            [name, desc] = pcm
            num = i + 1
            self._add_pcm_name_row(name, num)
            self._add_pcm_desc_row(desc)

            if num == pcm_len:
                self._table.append(self._bottom_line)
            else:
                self._table.append(self._center_line)

        self._print()

    def add_rates_formats(self, rates_formats):
        rf_len = len(rates_formats)

        for i, item in enumerate(rates_formats):
            num = i + 1
            self._add_rate_format_row(item, num)

            if num == rf_len:
                self._table.append(self._bottom_line)
            else:
                self._table.append(self._center_line)

        self._print()

    def _add_rate_format_row(self, text, num):
        self._add_table_row(text, num, False)

    def _add_pcm_name_row(self, text, num):
        self._add_table_row(text, num, True)

    def _add_pcm_desc_row(self, text):
        self._add_table_row(text, "", True)

    def _print(self):
        table = "\t" + "\n\t".join(self._table)
        print(table)

    def _add_table_header(self, title):
        self._table.append(self._top_line)
        self._add_table_row(title, "", None)
        self._table.append(self._title_bottom_line)

    def _add_table_row(self, text, num, justify_left):
        if justify_left is None:
            pad = int(self._padding / 2)
            row = f"{{:<{pad}}}{{:^{self._width}}}{{:>{pad}}}".format(
                "\u2551", text, "\u2551"
            )

        else:
            if justify_left:
                j = "<"

            else:
                j = ">"

            center_pad = int(self._padding / 2)
            pad = int(center_pad / 2)
            row = (
                f"{{:<{pad}}}{{:<{center_pad}}}{{:{j}{self._width}}}{{:>{pad}}}".format(
                    "\u2551", num, text, "\u2551"
                )
            )

        self._table.append(row)


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
        Stylize.error("\tError: This script requires write privileges to /etc.")
        raise SystemExit(1)


def backup_asound_conf():
    try:
        os.rename(ASOUND_FILE_PATH, BACKUP_FILE_PATH)

    except FileNotFoundError:
        pass

    except Exception as e:
        Stylize.error(f"\n\tError renaming existing {ASOUND_FILE_PATH}: {e}")
        raise SystemExit(1)

    else:
        Stylize.comment(
            f"\n\t{ASOUND_FILE_PATH} already exists renaming it to: {BACKUP_FILE_PATH}\n"
        )


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
        Stylize.error("\tNo available hw PCM")
        raise SystemExit(1)

    return hw_pcm_names


def get_sample_rate_converters():
    base_path = glob.glob("/usr/lib/*/alsa-lib")[0]
    search_term = f"{base_path}/libasound_module_rate_"
    return [
        f.replace(search_term, "").replace(".so", "")
        for f in glob.glob(f"{search_term}*")
    ]


def invalid_choice(len_choices):
    Stylize.error(f"\tPlease enter a number from 1 - {len_choices}.\n")


def choose_hw_pcm(hw_pcm_names):
    if len(hw_pcm_names) > 1:
        title = "Outputs"
        width = max(len(max([n for s in hw_pcm_names for n in s], key=len)), len(title))
        table = Table(title, width)
        table.add_pcms(hw_pcm_names)
        print("")

        while True:
            try:
                choice = input(Stylize.input("\tPlease choose an Output: "))

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
        Stylize.comment(
            f"\t{pcm} is the only available Output so that's what we'll use…\n"
        )

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
        title = "Formats"
        width = max(len(max(formats, key=len)), len(title))
        table = Table(title, width)
        table.add_rates_formats(formats)

        Stylize.comment(
            "\n\tIt's generally advised to choose the highest bit depth format that your device supports.\n"
        )

        while True:
            try:
                choice = input(Stylize.input("\tPlease choose a Format: "))

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

        Stylize.comment(f"\t{format_} is the only Format so that's what we'll use…\n")

    return format_


def choose_rate(rates):
    if len(rates) > 1:
        r_range = range(rates[0], rates[-1] + 1)
        rates = [r for r in COMMON_RATES if r in r_range]
        title = "Sampling Rates"
        width = max(len(max([str(r) for r in rates], key=len)), len(title))
        table = Table(title, width)
        table.add_rates_formats(rates)

        Stylize.comment(
            "\n\tStandard CD quality is 44100.\n\n"
            "\tAn unnecessarily high sampling rate can lead to high CPU usage,\n"
            "\tdegraded audio quality, and audio dropouts and glitches on low spec devices.\n"
            "\tUnless the music you normally listen to is a higher sampling rate,\n"
            "\t44100 (or as close as you can get to it) is the best choice.\n"
        )

        while True:
            try:
                choice = input(Stylize.input("\tPlease choose a Sampling Rate: "))

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

        Stylize.comment(
            f"\t{rate} is the only Sampling Rate so that's what we'll use…\n"
        )

        if rate > 88200:
            Stylize.comment(
                "\tHigh sampling rates can lead to high CPU usage, degraded audio quality,\n"
                "\tand audio dropouts and glitches on low spec devices.\n"
            )

    return rate


def pcm_to_card_device(pcm):
    try:
        [card, device] = pcm.split(",")
        card = card.replace("hw:CARD=", "").strip()
        device = int(device.strip("DEV= "))

    except Exception as e:
        Stylize.error(f"\tError parsing card and device: {e}")
        raise SystemExit(1)

    return card, device


def choose_sample_rate_converter():
    converters = get_sample_rate_converters()

    if len(converters) > 1:
        title = "Sample Rate Converters"
        width = max(len(max(converters, key=len)), len(title))
        table = Table(title, width)
        table.add_rates_formats(converters)

        Stylize.comment(
            '\n\tsamplerate_medium is the best "Bang for your buck" Converter.\n\n'
            "\tIf you don't see that in the choices you can install it on Debian based systems with:\n\n"
            '\t"sudo apt install -y --no-install-recommends libasound2-plugins"\n\n'
        )

        while True:
            try:
                choice = input(
                    Stylize.input("\tPlease choose a Sample Rate Converter: ")
                )

                print("")
                converter = converters[int(choice) - 1]

            except KeyboardInterrupt:
                print("")
                raise SystemExit(0)

            except:
                invalid_choice(len(converters))
                continue

            else:
                break

    else:
        converter = converters[0]

        Stylize.comment(
            f"\t{converter} is the only Sample Rate Converter so that's what we'll use…\n"
        )

    return converter


def get_choices():
    hw_pcm_names = get_hw_pcm_names()

    while True:
        try:
            pcm = choose_hw_pcm(hw_pcm_names)
            formats, rates = get_formats_and_rates(pcm)

            if not formats or not rates:
                Stylize.error(
                    "\tNo supported formats or sampling rates were returned.\n"
                    "\tThe Output you chose may be busy or not support any common formats and rates?\n"
                    "\tPlease make sure it's not in use and try again.\n"
                )

                continue

            else:
                format_ = choose_format(formats)
                rate = choose_rate(rates)
                converter = choose_sample_rate_converter()
                card, device = pcm_to_card_device(pcm)

                if format_ not in ("S24_LE", "S24_BE"):
                    Stylize.comment(
                        "\tPlease make sure your device is connected,\n"
                        "\tand set the volume to a comfortable level.\n\n"
                        "\tTest tones at 25% full scale will now be played to test your choices.\n"
                    )

                    input(Stylize.input("\tPlease press Enter to continue"))
                    print("")

                return card, device, format_, rate, converter

        except KeyboardInterrupt:
            print("")
            raise SystemExit(0)


def test_choices():
    while True:
        card, device, format_, rate, converter = get_choices()

        # speaker-test does not support S24_LE / S24_BE.
        if format_ not in ("S24_LE", "S24_BE"):
            try:
                subprocess.run(
                    [
                        "speaker-test",
                        f"-Dhw:CARD={card},DEV={device}",
                        f"-F{format_}",
                        f"-r{rate}",
                        "-l1",
                        "-c2",
                        "-S25",
                    ],
                    check=True,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )

            except KeyboardInterrupt:
                print("")
                raise SystemExit(0)

            except:
                Stylize.error(
                    "\tThe speaker test Failed.\n\n"
                    "\tPlease try again with a different Format and Sampling Rate combination.\n"
                )

                continue

            else:
                confirm = input(
                    Stylize.input('\tPlease enter "Y" if you heard the test tones: ')
                )

                if confirm.lower() == "y":
                    return card, device, format_, rate, converter

                else:
                    Stylize.comment(
                        "\n\tPlease make sure you're connected to the correct Output and try again.\n"
                    )

                    continue

        else:
            return card, device, format_, rate, converter


def write_asound_conf():
    privilege_check()

    Stylize.comment(
        f"\tThis script will backup {ASOUND_FILE_PATH} if it already exists,\n"
        f"\tand create a new {ASOUND_FILE_PATH} based on your choices.\n"
    )

    try:
        choice = input(Stylize.input('\tPlease enter "OK" to continue: '))

        if choice.lower() != "ok":
            print("")
            raise SystemExit(0)

        print("")

    except KeyboardInterrupt:
        print("")
        raise SystemExit(0)

    card, device, format_, rate, converter = test_choices()

    file_data = f"""# /etc/asound.conf

defaults.pcm.rate_converter {converter}

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
        Stylize.error(f"\tError: {e}")
        revert_asound_conf()
        raise SystemExit(1)

    else:
        Stylize.comment(
            f"\tUsing Card: {card}, Device: {device}, Format: {format_},\n"
            f"\tSampling Rate: {rate}, and Sample Rate Converter: {converter},\n"
            f"\t{ASOUND_FILE_PATH} was written successfully.\n\n"
            "\tPlease verify that it is correct.\n"
        )


if __name__ == "__main__":
    write_asound_conf()

