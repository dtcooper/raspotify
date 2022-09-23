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

import textwrap
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
    _CYAN = "\033[36m"
    _BOLD_YELLOW = "\033[1;33m"
    _BOLD_RED = "\033[1;31m"
    _BOLD_GREEN = "\033[1;32m"
    _RESET = "\033[00m"

    _WRAPPER = textwrap.TextWrapper(
        width=50, initial_indent="\n\t", subsequent_indent="\t"
    )

    @staticmethod
    def input(text):
        return input(f"\n\t{Stylize._BOLD}{text}{Stylize._RESET}")

    @staticmethod
    def warn(text):
        print(f"\n\t{Stylize._BOLD_YELLOW}{text}{Stylize._RESET}")

    @staticmethod
    def error(text):
        print(f"\n\t{Stylize._BOLD_RED}{text}{Stylize._RESET}")
        raise SystemExit(1)

    @staticmethod
    def comment(text):
        print(Stylize._WRAPPER.fill(f"{Stylize._CYAN}{text}{Stylize._RESET}"))

    @staticmethod
    def suggestion(text):
        print(f"\n\t{Stylize._BOLD_GREEN}{text}{Stylize._RESET}")


class Table:
    def __init__(self, title, width, padding=8):
        self._width = width
        self._padding = padding
        tp_center = "━" * (width + (padding - 2))
        c_center = "─" * (width + (padding - 2))
        self._top_line = "┏" + tp_center + "┓"
        self._title_bottom_line = "┣" + tp_center + "┫"
        self._center_line = "┠" + c_center + "┨"
        self._bottom_line = "┗" + tp_center + "┛"
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
        table = "\n\t".join(self._table)
        print("\n\t" + table)

    def _add_table_header(self, title):
        self._table.append(self._top_line)
        self._add_table_row(title, "", None)
        self._table.append(self._title_bottom_line)

    def _add_table_row(self, text, num, justify_left):
        if justify_left is None:
            pad = int(self._padding / 2)
            row = f"{{:<{pad}}}{{:^{self._width}}}{{:>{pad}}}".format("┃", text, "┃")

        else:
            if justify_left:
                j = "<"

            else:
                j = ">"

            center_pad = int(self._padding / 2)
            pad = int(center_pad / 2)
            row = (
                f"{{:<{pad}}}{{:<{center_pad}}}{{:{j}{self._width}}}{{:>{pad}}}".format(
                    "┃", num, text, "┃"
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
        Stylize.error("Error: This script requires write privileges to /etc.")


def backup_asound_conf():
    try:
        os.rename(ASOUND_FILE_PATH, BACKUP_FILE_PATH)

    except FileNotFoundError:
        pass

    except Exception as e:
        Stylize.error(f"Error renaming existing {ASOUND_FILE_PATH}: {e}")

    else:
        Stylize.comment(f"{ASOUND_FILE_PATH} already exists renaming it to:")

        Stylize.comment(f"{BACKUP_FILE_PATH}")


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
        Stylize.error("No available hw PCM")

    return hw_pcm_names


def get_sample_rate_converters():
    base_path = glob.glob("/usr/lib/*/alsa-lib")[0]
    search_term = f"{base_path}/libasound_module_rate_"
    return [
        f.replace(search_term, "").replace(".so", "")
        for f in glob.glob(f"{search_term}*")
    ]


def invalid_choice(len_choices):
    Stylize.warn(f"Please enter a number from 1 - {len_choices}.")


def choose_hw_pcm(hw_pcm_names):
    if len(hw_pcm_names) > 1:
        title = "Outputs"
        width = max(
            len(max([n for s in hw_pcm_names for n in s], key=len)),
            len(title),
        )

        table = Table(title, width)
        table.add_pcms(hw_pcm_names)

        while True:
            try:
                choice = Stylize.input("Please choose an Output: ")

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

        Stylize.comment(f"{pcm} is the only available Output so that's what we'll use…")

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
            "It's generally advised to choose the highest bit "
            "depth format that your device supports."
        )

        best_choice = None

        for format in reversed(COMMON_FORMATS):
            if format in formats:
                best_choice = format
                break

        Stylize.suggestion(f"{best_choice} is the best choice.")

        while True:
            try:
                choice = Stylize.input("Please choose a Format: ")

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

        Stylize.comment(f"{format} is the only Format so that's what we'll use…")

    return format


def choose_rate(rates):
    if len(rates) > 1:
        r_range = range(rates[0], rates[-1] + 1)
        rates = [r for r in COMMON_RATES if r in r_range]
        title = "Sampling Rates"
        width = max(len(max([str(r) for r in rates], key=len)), len(title))
        table = Table(title, width)
        table.add(rates)

        Stylize.comment("Standard CD quality is 44100.")

        Stylize.comment(
            "An unnecessarily high sampling rate can lead to high CPU usage, "
            "degraded audio quality, and audio dropouts "
            "and glitches on low spec devices."
        )

        best_choice = None

        for rate in rates:
            if rate >= 44100:
                best_choice = rate
                break
            else:
                best_choice = rates[-1]

        Stylize.suggestion(f"{best_choice} is the best choice.")

        while True:
            try:
                choice = Stylize.input("Please choose a Sampling Rate: ")

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

        Stylize.comment(f"{rate} is the only Sampling Rate so that's what we'll use…")

        if rate > 88200:
            Stylize.comment(
                "High sampling rates can lead to high CPU usage, degraded "
                "audio quality, and audio dropouts and "
                "glitches on low spec devices."
            )

    return rate


def pcm_to_card_device(pcm):
    try:
        [card, device] = pcm.split(",")
        card = card.replace("hw:CARD=", "").strip()
        device = int(device.strip("DEV= "))

    except Exception as e:
        Stylize.error(f"Error parsing card and device: {e}")

    return card, device


def choose_sample_rate_converter():
    converters = get_sample_rate_converters()

    if len(converters) > 1:
        title = "Sample Rate Converters"
        width = max(len(max(converters, key=len)), len(title))
        table = Table(title, width)
        table.add(converters)

        Stylize.comment(
            "Sample Rate Converters are very subjective, as far as if you can "
            "actually tell the difference audibly."
        )

        Stylize.comment(
            "Generally speaking though higher quality = higher CPU usage "
            "which can be a consideration on low spec devices."
        )

        Stylize.comment(
            "However, if the audio source matches the Sampling Rate of the "
            "Output the Converter is bypassed, and will have no performance "
            "or sound quality impact."
        )

        Stylize.comment(
            "All of that being said samplerate_medium is probably the best "
            '"Bang for your buck" Converter in most cases if '
            "a Converter MUST be used."
        )

        Stylize.comment(
            "If you don't see that in the choices you can install it on "
            "Debian based systems with:"
        )

        Stylize.comment(
            "sudo apt install -y --no-install-recommends libasound2-plugins"
        )

        while True:
            try:
                choice = Stylize.input("Please choose a Sample Rate Converter: ")

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
                f"{converter} is the only Sample Rate Converter "
                "so that's what we'll use…"
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
                Stylize.warn("No supported formats or sampling rates were returned.")

                Stylize.warn(
                    "The Output you chose may be busy or not support "
                    "any common formats and rates?"
                )

                Stylize.warn("Please make sure it's not in use and try again.")

                continue

            else:
                format = choose_format(formats)
                rate = choose_rate(rates)
                converter = choose_sample_rate_converter()
                card, device = pcm_to_card_device(pcm)

                return card, device, format, rate, converter

        except KeyboardInterrupt:
            bailout()


def test_choices():
    while True:
        card, device, format, rate, converter = get_choices()

        # speaker-test does not support S24_LE / S24_BE.
        if format in ("S24_LE", "S24_BE"):
            return card, device, format, rate, converter

        else:
            confirm = Stylize.input(
                'Please enter "Y" if you would like to test your choices: '
            )

            if confirm.lower() != "y":
                return card, device, format, rate, converter

            else:
                Stylize.comment(
                    "Please make sure your device is connected, "
                    "and set the volume to a comfortable level."
                )

                Stylize.comment(
                    "Pink noise at 25% full scale will now be played "
                    "to test your choices."
                )

                Stylize.input("Please press Enter to continue")

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
                    Stylize.warn("The speaker test Failed.")

                    Stylize.warn(
                        "Please try again with a different Format and "
                        "Sampling Rate combination."
                    )

                    continue

                else:
                    confirm = Stylize.input(
                        'Please enter "Y" if you heard the test tones: '
                    )

                    if confirm.lower() == "y":
                        return card, device, format, rate, converter

                    else:
                        Stylize.comment(
                            "Please make sure you're connected to the "
                            "correct Output and try again."
                        )

                        continue


def write_asound_conf():
    privilege_check()

    Stylize.comment(
        f"This script will backup {ASOUND_FILE_PATH} if it already exists, "
        f"and create a new {ASOUND_FILE_PATH} based on your choices."
    )

    Stylize.comment(
        "This will create a system wide static audio configuration "
        "assuming a 2 channel stereo Output Device."
    )

    Stylize.comment("It does not take into account audio inputs at all.")

    Stylize.comment(
        "This script is intended to be used on headless Debian based systems "
        "where the hardware does not change often or at all."
    )

    Stylize.comment("Your mileage may vary on non-Debian based distros.")

    Stylize.comment("It is not advisable to run this script on desktop systems.")

    Stylize.comment(
        "If running this script breaks your system you get to keep all the "
        "pieces, and it's your responsibility to put them back together."
    )

    try:
        choice = Stylize.input('Please enter "OK" to continue: ')

        if choice.lower() != "ok":
            bailout()

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
        Stylize.error(f"Error: {e}")

    else:
        Stylize.comment(
            f"{ASOUND_FILE_PATH} was written successfully with the following values:"
        )

        Stylize.comment(f"Card: {card}")
        Stylize.comment(f"Device: {device}")
        Stylize.comment(f"Format: {format}")
        Stylize.comment(f"Sampling Rate: {rate}")

        if converter:
            Stylize.comment(f"Sample Rate Converter: {converter}")

        Stylize.comment("Please verify that this is correct.")

        Stylize.comment(
            "You can revert your system to it's default state by deleting "
            f"{ASOUND_FILE_PATH} with:"
        )

        Stylize.comment(f"sudo rm {ASOUND_FILE_PATH}")

        Stylize.comment(
            "or optionally revert it from the back up if one was created "
            "if you have any issue with the generated config."
        )


if __name__ == "__main__":
    write_asound_conf()

