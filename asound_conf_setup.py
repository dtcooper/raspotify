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
    _YELLOW = "\u001b[33m"
    _BOLD_RED = "\x1b[31;1m"
    _RESET = "\u001b[0m"

    @staticmethod
    def input(text):
        return input(f"{Stylize._BOLD}{text}{Stylize._RESET}")

    @staticmethod
    def warn(text):
        print(f"{Stylize._YELLOW}{text}{Stylize._RESET}")

    @staticmethod
    def error(text):
        print(f"{Stylize._BOLD_RED}{text}{Stylize._RESET}")
        raise SystemExit(1)

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

    def add(self, items):
        i_len = len(items)

        for i, item in enumerate(items):
            num = i + 1
            self._add_row(item, num)

            if num == i_len:
                self._table.append(self._bottom_line)
            else:
                self._table.append(self._center_line)

        self._print()

    def _add_row(self, text, num):
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


def bailout():
    print("")
    raise SystemExit(0)


def privilege_check():
    try:
        open(DUMMY_FILE_PATH, "w").close()
        os.remove(DUMMY_FILE_PATH)

    except:
        Stylize.error("\tError: This script requires write privileges to /etc.")


def backup_asound_conf():
    try:
        os.rename(ASOUND_FILE_PATH, BACKUP_FILE_PATH)

    except FileNotFoundError:
        pass

    except Exception as e:
        Stylize.error(f"\n\tError renaming existing {ASOUND_FILE_PATH}: {e}")

    else:
        Stylize.comment(
            f"\n\t{ASOUND_FILE_PATH} already exists renaming it to: {BACKUP_FILE_PATH}\n"
        )


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

    return hw_pcm_names


def get_sample_rate_converters():
    base_path = glob.glob("/usr/lib/*/alsa-lib")[0]
    search_term = f"{base_path}/libasound_module_rate_"
    return [
        f.replace(search_term, "").replace(".so", "")
        for f in glob.glob(f"{search_term}*")
    ]


def invalid_choice(len_choices):
    Stylize.warn(f"\tPlease enter a number from 1 - {len_choices}.\n")


def choose_hw_pcm(hw_pcm_names):
    if len(hw_pcm_names) > 1:
        title = "Outputs"
        width = max(len(max([n for s in hw_pcm_names for n in s], key=len)), len(title))
        table = Table(title, width)
        table.add_pcms(hw_pcm_names)
        print("")

        while True:
            try:
                choice = Stylize.input("\tPlease choose an Output: ")

                print("")
                pcm = hw_pcm_names[int(choice) - 1][0]

            except KeyboardInterrupt:
                bailout()

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
            for f in line.strip("FORMAT: ").split(" "):
                if f in COMMON_FORMATS:
                    formats.append(f)

        elif line.startswith("RATE:"):
            for r in line.strip("RATE:[ ]").split(" "):
                try:
                    rates.append(int(r))

                except:
                    pass

    return formats, rates


def choose_format(formats):
    if len(formats) > 1:
        title = "Formats"
        width = max(len(max(formats, key=len)), len(title))
        table = Table(title, width)
        table.add(formats)

        Stylize.comment(
            "\n\tIt's generally advised to choose the highest bit depth format that your device supports.\n"
        )

        while True:
            try:
                choice = Stylize.input("\tPlease choose a Format: ")

                print("")
                format = formats[int(choice) - 1]

            except KeyboardInterrupt:
                bailout()

            except:
                invalid_choice(len(formats))
                continue

            else:
                break

    else:
        format = formats[0]

        Stylize.comment(f"\t{format} is the only Format so that's what we'll use…\n")

    return format


def choose_rate(rates):
    if len(rates) > 1:
        r_range = range(rates[0], rates[-1] + 1)
        rates = [r for r in COMMON_RATES if r in r_range]
        title = "Sampling Rates"
        width = max(len(max([str(r) for r in rates], key=len)), len(title))
        table = Table(title, width)
        table.add(rates)

        Stylize.comment(
            "\n\tStandard CD quality is 44100.\n\n"
            "\tAn unnecessarily high sampling rate can lead to high CPU usage,\n"
            "\tdegraded audio quality, and audio dropouts and glitches on low spec devices.\n"
            "\tUnless the music you normally listen to is a higher sampling rate,\n"
            "\t44100 (or as close as you can get to it) is the best choice.\n"
        )

        while True:
            try:
                choice = Stylize.input("\tPlease choose a Sampling Rate: ")

                print("")
                rate = rates[int(choice) - 1]

            except KeyboardInterrupt:
                bailout()

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

    return card, device


def choose_sample_rate_converter():
    converters = get_sample_rate_converters()

    if len(converters) > 1:
        title = "Sample Rate Converters"
        width = max(len(max(converters, key=len)), len(title))
        table = Table(title, width)
        table.add(converters)

        Stylize.comment(
            '\n\tsamplerate_medium is the best "Bang for your buck" Converter.\n\n'
            "\tIf you don't see that in the choices you can install it on Debian based systems with:\n\n"
            "\tsudo apt install -y --no-install-recommends libasound2-plugins\n\n"
        )

        while True:
            try:
                choice = Stylize.input("\tPlease choose a Sample Rate Converter: ")

                print("")
                converter = converters[int(choice) - 1]

            except KeyboardInterrupt:
                bailout()

            except:
                invalid_choice(len(converters))
                continue

            else:
                break

    else:
        if converters:
            converter = converters[0]

            Stylize.comment(
                f"\t{converter} is the only Sample Rate Converter so that's what we'll use…\n"
            )

        else:
            converter = None

    return converter


def get_choices():
    hw_pcm_names = get_hw_pcm_names()

    while True:
        try:
            pcm = choose_hw_pcm(hw_pcm_names)
            formats, rates = get_formats_and_rates(pcm)

            if not formats or not rates:
                Stylize.warn(
                    "\tNo supported formats or sampling rates were returned.\n"
                    "\tThe Output you chose may be busy or not support any common formats and rates?\n"
                    "\tPlease make sure it's not in use and try again.\n"
                )

                continue

            else:
                format = choose_format(formats)
                rate = choose_rate(rates)
                converter = choose_sample_rate_converter()
                card, device = pcm_to_card_device(pcm)

                if format not in ("S24_LE", "S24_BE"):
                    Stylize.comment(
                        "\tPlease make sure your device is connected,\n"
                        "\tand set the volume to a comfortable level.\n\n"
                        "\tTest tones at 25% full scale will now be played to test your choices.\n"
                    )

                    Stylize.input("\tPlease press Enter to continue")
                    print("")

                return card, device, format, rate, converter

        except KeyboardInterrupt:
            bailout()


def test_choices():
    while True:
        card, device, format, rate, converter = get_choices()

        # speaker-test does not support S24_LE / S24_BE.
        if format not in ("S24_LE", "S24_BE"):
            try:
                subprocess.run(
                    [
                        "speaker-test",
                        f"-Dhw:CARD={card},DEV={device}",
                        f"-F{format}",
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
                bailout()

            except:
                Stylize.warn(
                    "\tThe speaker test Failed.\n\n"
                    "\tPlease try again with a different Format and Sampling Rate combination.\n"
                )

                continue

            else:
                confirm = Stylize.input(
                    '\tPlease enter "Y" if you heard the test tones: '
                )

                if confirm.lower() == "y":
                    return card, device, format, rate, converter

                else:
                    Stylize.comment(
                        "\n\tPlease make sure you're connected to the correct Output and try again.\n"
                    )

                    continue

        else:
            return card, device, format, rate, converter


def write_asound_conf():
    privilege_check()

    Stylize.comment(
        f"\tThis script will backup {ASOUND_FILE_PATH} if it already exists,\n"
        f"\tand create a new {ASOUND_FILE_PATH} based on your choices.\n\n"
        f"\tThis will create a system wide static audio configuration\n"
        f"\tassuming a 2 channel stereo Output Device.\n"
        f"\tIt does not take into account audio inputs at all.\n\n"
        f"\tThis script is intended to be used on headless systems where the hardware\n"
        f"\tdoes not change often or at all.\n\n"
        f"\tIt is not advisable to run this script on desktop systems.\n\n"
        f"\tIf running this script breaks your system you get to keep all the pieces.\n\n"
    )

    try:
        choice = Stylize.input('\tPlease enter "OK" to continue: ')

        if choice.lower() != "ok":
            bailout()

        print("")

    except KeyboardInterrupt:
        bailout()

    card, device, format, rate, converter = test_choices()

    rate_converter = ""

    if converter:
        rate_converter = f"defaults.pcm.rate_converter {converter}"

    file_data = f"""# /etc/asound.conf

{rate_converter}

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
            format {format}
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

    else:
        Stylize.comment(
            f"\t{ASOUND_FILE_PATH} was written successfully with the following values:\n"
            f"\n\tCard: {card}\n\tDevice: {device}\n\tFormat: {format}\n\tSampling Rate: {rate}"
        )

        if converter:
            Stylize.comment(f"\tSample Rate Converter: {converter}")

        Stylize.comment(
            "\n\n\tPlease verify that this is correct.\n\n"
            f"\tYou can revert your system to it's default state by deleting {ASOUND_FILE_PATH} with:\n\n"
            f"\tsudo rm {ASOUND_FILE_PATH}\n\n"
            "\tor optionally revert it from the back up if one was created\n"
            "\tif you have any issue with the generated config.\n"
        )


if __name__ == "__main__":
    write_asound_conf()

