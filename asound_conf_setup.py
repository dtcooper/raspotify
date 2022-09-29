#!/usr/bin/python3
"""Generate /etc/asound.conf based on user choices"""
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

from textwrap import TextWrapper
from glob import glob
from shutil import which
from sys import exit as sys_exit
from signal import signal, SIGINT, SIGTERM, SIGHUP
from subprocess import CalledProcessError, PIPE, STDOUT, DEVNULL
from subprocess import run as subprocess_run
from os import rename as os_rename
from os import remove as os_remove
from time import time as time_time

ASOUND_FILE_PATH = "/etc/asound.conf"
DUMMY_FILE_PATH = f"/etc/foobarbaz{int(time_time())}"
BACKUP_FILE_PATH = f"/etc/asound.conf.bak{int(time_time())}"
CONVERTERS_FILE_PATH = "/usr/lib/*/alsa-lib"
CONVERTERS_SEARCH_SUFFIX = "/libasound_module_rate_"
ALSA_PLUGINS = "libasound2-plugins"
ALSA_UTILS = "alsa-utils"

NOT_SUPPORTED_BY_SPEAKER_TEST = ("S24_LE", "S24_BE")

APT = which("apt")
SUDO = which("sudo")

if APT:
    if SUDO:
        UPDATE_CMD = [SUDO, APT, "update"]

        ALSA_UTILS_INSTALL_CMD = [
            SUDO,
            APT,
            "install",
            "-y",
            ALSA_UTILS,
        ]

        CONVERTER_INSTALL_CMD = [
            SUDO,
            APT,
            "install",
            "-y",
            "--no-install-recommends",
            ALSA_PLUGINS,
        ]

    else:
        UPDATE_CMD = [APT, "update"]

        ALSA_UTILS_INSTALL_CMD = [
            APT,
            "install",
            "-y",
            ALSA_UTILS,
        ]

        CONVERTER_INSTALL_CMD = [
            APT,
            "install",
            "-y",
            "--no-install-recommends",
            ALSA_PLUGINS,
        ]

else:
    UPDATE_CMD = None
    CONVERTER_INSTALL_CMD = None
    ALSA_UTILS_INSTALL_CMD = None

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

COMMON_RATE_CONVERTERS = [
    "speexrate",
    "speexrate_medium",
    "speexrate_best",
    "lavrate_faster",
    "lavrate_fast",
    "lavrate",
    "lavrate_high",
    "lavrate_higher",
    "samplerate_linear",
    "samplerate_order",
    "samplerate",
    "samplerate_medium",
    "samplerate_best",
]

BEST_CONVERTERS = (
    "speexrate_medium",
    "lavrate",
    "samplerate",
)

CHANNEL_COUNTS = [
    1,
    2,
    4,
    6,
    8,
]

ONE_CH_ROUTE = """
    ttable.0.0 0.5
    ttable.1.0 0.5
"""

ONE_CH_BINDINGS = """
        0 0
"""

TWO_CH_BINDINGS = """
        0 0
        1 1
"""

FOUR_CH_ROUTE = """
    ttable.0.0 1
    ttable.1.1 1
    ttable.0.2 1
    ttable.1.3 1
"""

FOUR_CH_BINDINGS = """
        0 0
        1 1
        2 2
        3 3
"""

SIX_CH_ROUTE = """
    ttable.0.0 1
    ttable.1.1 1
    ttable.0.2 1
    ttable.1.3 1
    ttable.0.4 0.5
    ttable.1.4 0.5
    ttable.1.5 0.5
    ttable.0.5 0.5
"""

SIX_CH_BINDINGS = """
        0 0
        1 1
        2 2
        3 3
        4 4
        5 5
"""

EIGHT_CH_ROUTE = """
    ttable.0.0 1
    ttable.1.1 1
    ttable.0.2 1
    ttable.1.3 1
    ttable.0.4 0.5
    ttable.1.4 0.5
    ttable.0.5 0.5
    ttable.1.5 0.5
    ttable.0.6 1
    ttable.1.7 1
"""

EIGHT_CH_BINDINGS = """
        0 0
        1 1
        2 2
        3 3
        4 4
        5 5
        6 6
        7 7
"""

ASOUND_TEMPLATE = """
{rate_converter}

pcm.default_hw {{
    type hw
    card {card}
    device {device}
    channels {channels}
    rate {rate}
    format {fmt}
}}

pcm.dmixer {{
    type dmix
    slave.pcm default_hw
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
    bindings {{
{bindings}
    }}
}}

pcm.!default {{
    type plug
{route}
    slave.pcm dmixer
}}
"""

class AsoundConfWizardError(Exception):
    """Asound Conf Wizard Error"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AudioSoftwareConflictError(AsoundConfWizardError):
    """Audio Software Conflict Error"""
    def __init__(self, software, message="This script is not compatible with"):
        if "/" in software:
            message_end = "which are installed on your system"
        else:
            message_end = "which is installed on your system"

        self.message = f"{message} {software} {message_end}"
        super().__init__(self.message)

class InsufficientPrivilegesError(AsoundConfWizardError):
    """Insufficient Privileges Error"""
    def __init__(self, message="This script requires write privileges to /etc"):
        self.message = message
        super().__init__(self.message)

class InstallError(AsoundConfWizardError):
    """Package Install Error"""
    def __init__(self, package, error, message="Unable to Install Package"):
        self.message = f"{message} {package}: {error}"
        super().__init__(self.message)

class MissingDependenciesError(AsoundConfWizardError):
    """Missing Dependencies Error"""
    def __init__(
        self,
        message="This script requires that aplay and speaker-test be installed",
    ):
        self.message = message
        super().__init__(self.message)

class RenamingError(AsoundConfWizardError):
    """Renaming Error"""
    def __init__(self, error, message=f"Could not rename existing {ASOUND_FILE_PATH}"):
        self.message = f"{message}: {error}"
        super().__init__(self.message)

class NoHwPcmError(AsoundConfWizardError):
    """No Hw Pcm Error"""
    def __init__(self, error, message="No available hw PCM"):
        if error:
            message = f"{message}: {error}"
        self.message = message
        super().__init__(self.message)

class PcmParsingError(AsoundConfWizardError):
    """Pcm Parsing Error"""
    def __init__(self, error, message="Could not parsing card and device"):
        self.message = f"{message}: {error}"
        super().__init__(self.message)

class PcmOpenError(AsoundConfWizardError):
    """Pcm Open Error"""
    def __init__(self, error):
        self.message = error
        super().__init__(self.message)

class AsoundConfWriteError(AsoundConfWizardError):
    """Asound Conf Write Error"""
    def __init__(self, error, message=f"Error writing {ASOUND_FILE_PATH}"):
        self.message = f"{message}: {error}"
        super().__init__(self.message)

class Stylize:
    """Stylize Text"""
    _BOLD = "\033[1m"
    _CYAN = "\033[36m"
    _BOLD_YELLOW = "\033[1;33m"
    _BOLD_RED = "\033[1;31m"
    _BOLD_GREEN = "\033[1;32m"
    _RESET = "\033[00m"

    _WRAPPER = TextWrapper(initial_indent="\n\t", subsequent_indent="\t")

    @staticmethod
    def input(text):
        """Makes the input text bold"""
        try:
            return input(f"\n\t{Stylize._BOLD}{text}{Stylize._RESET}")
        except EOFError:
            print("")
            sys_exit(0)

    @staticmethod
    def warn(warning):
        """Makes the warn text bold yellow"""
        if isinstance(warning, AsoundConfWizardError):
            print(f"\n\t{Stylize._BOLD_YELLOW}{type(warning).__doc__}{Stylize._RESET}")

        print(f"\n\t{Stylize._BOLD_YELLOW}{warning}{Stylize._RESET}")

    @staticmethod
    def error(error):
        """Makes the error text bold red and exits with a status 1"""
        if isinstance(error, AsoundConfWizardError):
            print(f"\n\t{Stylize._BOLD_RED}{type(error).__doc__}{Stylize._RESET}")

        print(f"\n\t{Stylize._BOLD_RED}{error}{Stylize._RESET}")

        if isinstance(error, InsufficientPrivilegesError):
            print(
                f"\n\t{Stylize._BOLD_RED}HINT: Try running this "
                f"script with sudo or as root{Stylize._RESET}"
            )
        elif isinstance(error, AudioSoftwareConflictError):
            print(
                f"\n\t{Stylize._BOLD_RED}It is intended to be used on systems "
                f"that run bare ALSA{Stylize._RESET}"
            )

        sys_exit(1)

    @staticmethod
    def comment(text):
        """Makes the comment text cyan"""
        print(Stylize._WRAPPER.fill(f"{Stylize._CYAN}{text}{Stylize._RESET}"))

    @staticmethod
    def suggestion(text):
        """Makes the suggestion text bold green"""
        print(f"\n\t{Stylize._BOLD_GREEN}{text}{Stylize._RESET}")

class Table:
    """Basic Unicode Table"""
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
        """Add Hw PCMs to the Table"""
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

    def add_choices(self, choices):
        """Add choices to the Table"""
        pad = int(self._padding / 4)
        choices_len = len(choices)

        for i, choice in enumerate(choices):
            num = i + 1
            [key, value] = choice
            center_pad = (self._width - len(key)) + int(self._padding / 2)

            row = (
                f"{{:<{pad}}}{{:>{pad}}}{{:>{center_pad}}}{{:>{pad}}}".format("┃", key, value, "┃")
            )

            self._table.append(row)

            if num == choices_len:
                self._table.append(self._bottom_line)
            else:
                self._table.append(self._center_line)

        self._print()

    def add(self, items):
        """Add other things to the Table"""
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

class AsoundConfWizard:
    """Generate /etc/asound.conf based on user choices"""
    def __init__(self):
        self._get_pcm_names_cmd = []
        self._hw_params_cmd_template = ""
        self._speaker_test_cmd_template = ""

    def run(self):
        """Run the Wizard"""
        try:
            self._privilege_check()
            self._write_asound_conf()
        except AsoundConfWizardError as err:
            raise err

    @staticmethod
    def quit(*_args, **_kwargs):
        """Quit the Wizard"""
        print("")
        sys_exit(0)

    def _build_cmds(self):
        aplay = which("aplay")
        speaker_test = which("speaker-test")

        if aplay and speaker_test:
            self._get_pcm_names_cmd = [aplay, "-L"]

            self._hw_params_cmd_template = (
                f"{aplay} "
                "-D{} --dump-hw-params /usr/share/sounds/alsa/Front_Right.wav"
            )

            self._speaker_test_cmd_template = (
                f"{speaker_test} "
                "-Dhw:CARD={},DEV={} -F{} -r{} -l1 -c{} -S25"
            )

        elif not ALSA_UTILS_INSTALL_CMD:
            raise MissingDependenciesError()
        else:
            Stylize.comment(
                "This script requires aplay and speaker-test "
                f"which are contained in the {ALSA_UTILS} package"
            )

            choice = Stylize.input(f'Please enter "Y" to install {ALSA_UTILS}: ')

            if choice.lower() != "y":
                raise MissingDependenciesError()

            Stylize.comment("This may take a moment…")

            try:
                subprocess_run(
                    UPDATE_CMD,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

                subprocess_run(
                    ALSA_UTILS_INSTALL_CMD,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

            except CalledProcessError as err:
                raise InstallError(ALSA_UTILS, err.stderr.decode("utf-8")) from err
            else:
                aplay = which("aplay")
                speaker_test = which("speaker-test")

                if aplay and speaker_test:
                    Stylize.comment(f"{ALSA_UTILS} Installed Successfully")
                    self._get_pcm_names_cmd = [aplay, "-L"]

                    self._hw_params_cmd_template = (
                        f"{aplay} "
                        "-D{} --dump-hw-params /usr/share/sounds/alsa/Front_Right.wav"
                    )

                    self._speaker_test_cmd_template = (
                        f"{speaker_test} "
                        "-Dhw:CARD={},DEV={} -F{} -r{} -l1 -c{} -S25"
                    )

                else:
                    raise MissingDependenciesError()

    def _get_hw_pcm_names(self):
        try:
            all_pcm_name = (
                subprocess_run(
                    self._get_pcm_names_cmd,
                    check=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode("utf-8")
                .split("\n")
            )
        except CalledProcessError as err:
            raise NoHwPcmError(err.stderr.decode("utf-8")) from err

        hw_pcm_names = [
            [n.strip(), all_pcm_name[i + 1].strip()]
            for i, n in enumerate(all_pcm_name)
            # HDMI's show up as hw Outputs on Raspberry Pi's,
            # but I can't get either to work properly with this script.
            if n.startswith("hw:") and "vc4hdmi," not in n and "CARD=b1," not in n
        ]

        if not hw_pcm_names:
            raise NoHwPcmError(None)

        return hw_pcm_names

    def _choose_hw_pcm(self):
        try:
            hw_pcm_names = self._get_hw_pcm_names()
        except NoHwPcmError as err:
            raise err

        if len(hw_pcm_names) > 1:
            title = "Outputs"

            width = max(
                len(max([n for s in hw_pcm_names for n in s], key=len)),
                len(title),
            )

            table = Table(title, width)
            table.add_pcms(hw_pcm_names)

            while True:
                choice = Stylize.input("Please choose an Output: ")
                try:
                    pcm = hw_pcm_names[int(choice) - 1][0]
                except (ValueError, IndexError):
                    self._invalid_choice(len(hw_pcm_names))
                    continue
                else:
                    break
        else:
            pcm = hw_pcm_names[0][0]
            Stylize.comment(f"{pcm} is the only available Output so that's what we'll use…")

        return pcm

    def _get_formats_rates_channels(self, pcm):
        Stylize.comment("Outputs must not in use while querying their Hardware Parameters.")
        Stylize.comment("Please make sure the Output you chose is not in use before continuing.")
        enter = Stylize.input("Please press Enter to continue")

        if enter != "":
            self.quit()

        cmd = self._hw_params_cmd_template.format(pcm).split(" ")

        try:
            hw_params = subprocess_run(
                cmd,
                check=False,
                stderr=STDOUT,
                stdout=PIPE,
            ).stdout.decode("utf-8")

        except Exception as err:
            raise PcmOpenError(err) from err

        if "audio open error:" in hw_params:
            err = hw_params.split(":")[-1].strip().title()
            raise PcmOpenError(err)

        formats = []
        rates = []
        channels = []

        for line in hw_params.split("\n"):
            if line.startswith("FORMAT:"):
                for fmt in line.strip("FORMAT: ").split(" "):
                    if fmt in COMMON_FORMATS:
                        formats.append(fmt)

            elif line.startswith("RATE:"):
                for rate in line.strip("RATE:[ ]").split(" "):
                    try:
                        rates.append(int(rate))
                    except ValueError:
                        pass

            elif line.startswith("CHANNELS:"):
                for channel in line.strip("CHANNELS:[ ]").split(" "):
                    try:
                        channels.append(int(channel))
                    except ValueError:
                        pass

        return formats, rates, channels

    def _choose_channel_count(self, channels):
        if len(channels) > 1:
            c_range = range(channels[0], channels[-1] + 1)
            channels = [c for c in CHANNEL_COUNTS if c in c_range]
            title = "Channel Counts"
            width = max(len(max([str(c) for c in channels], key=len)), len(title))
            table = Table(title, width)
            table.add(channels)

            Stylize.comment(
                "Channel Up Mixing is done with channel duplication for the "
                "Right and Left Surround Channels and channel combination for "
                "the Center and LFE (Sub) Channels without any effects or high/low pass filtering."
            )

            Stylize.comment("It is not true surround sound.")
            Stylize.comment("Channel Down Mixing is done with channel combination for Mono.")

            Stylize.comment(
                "Some Devices do not map their channels correctly. "
                f"If so you may need to edit {ASOUND_FILE_PATH} and correct "
                "the mapping manually."
            )

            Stylize.comment("When in doubt choose 2 (Stereo) if available.")

            while True:
                choice = Stylize.input("Please choose a Channel Count: ")
                try:
                    channel_count = channels[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(channels))
                    continue
                else:
                    break
        else:
            channel_count = channels[0]
            Stylize.comment(f"{channel_count} is the only Channel Count so that's what we'll use…")

        return channel_count

    def _choose_format(self, formats):
        if len(formats) > 1:
            title = "Formats"
            width = max(len(max(formats, key=len)), len(title))
            table = Table(title, width)
            table.add(formats)

            Stylize.comment(
                "It's generally advised to choose the highest bit "
                "depth format that your device supports."
            )

            for fmt in reversed(COMMON_FORMATS):
                if fmt in formats:
                    self._best_choice(fmt)
                    break

            while True:
                choice = Stylize.input("Please choose a Format: ")
                try:
                    fmt = formats[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(formats))
                    continue
                else:
                    break
        else:
            fmt = formats[0]
            Stylize.comment(f"{fmt} is the only Format so that's what we'll use…")

        return fmt

    def _choose_rate(self, rates):
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

            for rate in rates:
                choice = None
                if rate >= 44100:
                    choice = rate
                    break

            self._best_choice(choice or rates[-1])

            while True:
                choice = Stylize.input("Please choose a Sampling Rate: ")
                try:
                    rate = rates[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(rates))
                    continue
                else:
                    break
        else:
            rate = rates[0]
            Stylize.comment(f"{rate} is the only Sampling Rate so that's what we'll use…")

            if rate > 88200:
                Stylize.warn(
                    "High sampling rates can lead to high CPU usage, degraded "
                    "audio quality, and audio dropouts and "
                    "glitches on low spec devices."
                )

        return rate

    def _choose_sample_rate_converter(self):
        converters = self._get_sample_rate_converters()
        if len(converters) > 1:
            title = "Sample Rate Converters"
            width = max(len(max(converters, key=len)), len(title))
            table = Table(title, width)
            table.add(converters)

            Stylize.comment(
                "Sample Rate Converters are very subjective as far as if you can "
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

            for converter in BEST_CONVERTERS:
                if converter in converters:
                    self._best_choice(converter)
                    break

            while True:
                choice = Stylize.input("Please choose a Sample Rate Converter: ")
                try:
                    converter = converters[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(converters))
                    continue
                else:
                    break
        else:
            if converters:
                converter = converters[0]

                Stylize.comment(
                    f"{converter} is the only Sample Rate Converter so that's what we'll use…"
                )
            else:
                converter = None

        return converter

    def _get_choices(self):
        while True:
            try:
                pcm = self._choose_hw_pcm()

            except NoHwPcmError as err:
                raise err
            try:
                formats, rates, channels = self._get_formats_rates_channels(pcm)

            except PcmOpenError as err:
                Stylize.warn(err)

                Stylize.warn(
                    "Please make sure the Output you chose is not in use and try again."
                )

                continue

            if not formats or not rates or not channels:
                Stylize.warn(
                    "No supported formats, sampling rates or channel counts were returned."
                )

                Stylize.warn(
                    "The Output you chose may not support any common formats and rates?"
                )

                Stylize.warn("Please choose a different Output.")
                continue

            fmt = self._choose_format(formats)
            rate = self._choose_rate(rates)
            channel_count = self._choose_channel_count(channels)
            converter = self._choose_sample_rate_converter()
            card, device = self._pcm_to_card_device(pcm)

            return card, device, fmt, rate, converter, channel_count

    def _test_choices(self):
        while True:
            card, device, fmt, rate, converter, channel_count = self._get_choices()

            title = "Your Choices"

            choices = [
                ["Card", card],
                ["Device", str(device)],
                ["Format", fmt],
                ["Sampling Rate", str(rate)],
                ["Channel Count", str(channel_count)],
            ]

            if converter:
                choices.append(["Sample Rate Converter", converter])

            width = max(len(max(["".join(c) for c in choices], key=len)), len(title))
            table = Table(title, width)
            table.add_choices(choices)

            if fmt in NOT_SUPPORTED_BY_SPEAKER_TEST:
                return card, device, fmt, rate, converter, channel_count

            Stylize.comment(
                "Unless you are ABSOLUTELY certain your choices are correct you should test them."
            )

            confirm = Stylize.input(
                'Please enter "Y" if you would like to test your choices: '
            )

            if confirm.lower() != "y":
                return card, device, fmt, rate, converter, channel_count

            Stylize.comment(
                "Please make sure your device is connected, "
                "and set the volume to a comfortable level."
            )

            Stylize.comment(
                "Pink noise at 25% full scale will now be played "
                "to test your choices."
            )

            enter = Stylize.input("Please press Enter to continue")

            if enter != "":
                self.quit()

            cmd = self._speaker_test_cmd_template.format(
                card,
                device,
                fmt,
                rate,
                channel_count,
            ).split(" ")

            try:
                subprocess_run(
                    cmd,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

            except CalledProcessError as err:
                Stylize.warn(f"The speaker test Failed: {err.stderr.decode('utf-8')}")

                Stylize.warn(
                    "Please try again with a different Format, "
                    "Sampling Rate and Channel Count combination."
                )

                continue

            confirm = Stylize.input(
                'Please enter "Y" if you heard the test tones: '
            )

            if confirm.lower() == "y":
                return card, device, fmt, rate, converter, channel_count

            Stylize.warn("Please make sure you're connected to the correct Output and try again.")

    def _build_conf(self):
        try:
            card, device, fmt, rate, converter, channel_count = self._test_choices()
        except AsoundConfWizardError as err:
            raise err

        rate_converter = ""

        if converter:
            rate_converter = f"defaults.pcm.rate_converter {converter}"

        if channel_count == 1:
            route = ONE_CH_ROUTE.strip("\n")
            bindings = ONE_CH_BINDINGS.strip("\n")
        elif channel_count == 4:
            route = FOUR_CH_ROUTE.strip("\n")
            bindings = FOUR_CH_BINDINGS.strip("\n")
        elif channel_count == 6:
            route = SIX_CH_ROUTE.strip("\n")
            bindings = SIX_CH_BINDINGS.strip("\n")
        elif channel_count == 8:
            route = EIGHT_CH_ROUTE.strip("\n")
            bindings = EIGHT_CH_BINDINGS.strip("\n")
        else:
            route = ""
            bindings = TWO_CH_BINDINGS.strip("\n")

        file_data = ASOUND_TEMPLATE.format(
            card=card,
            device=device,
            fmt=fmt,
            rate=rate,
            rate_converter=rate_converter,
            channels=channel_count,
            route=route,
            bindings=bindings,
        ).strip("\n")

        return file_data

    def _write_asound_conf(self):
        Stylize.comment(
            f"This script will backup {ASOUND_FILE_PATH} if it already exists, "
            f"and create a new {ASOUND_FILE_PATH} based on your choices."
        )

        Stylize.comment("This will create a system wide static audio configuration")
        Stylize.comment("It does not take into account audio inputs at all.")

        Stylize.comment(
            "This script is intended to be used on headless Debian based systems "
            "that run bare ALSA where the hardware does not change often or at all."
        )

        Stylize.comment("Your mileage may vary on non-Debian based distros.")
        Stylize.comment("It is not advisable to run this script on desktop systems.")

        Stylize.comment(
            "This script will NOT run on systems that have PulseAudio, Jack Audio "
            "or PipeWire installed. That is by design. You should use those to configure "
            "audio if they are installed."
        )

        Stylize.comment(
            "If running this script breaks your system you get to keep all the "
            "pieces, and it's your responsibility to put them back together."
        )

        choice = Stylize.input('Please enter "OK" to continue: ')

        if choice.lower() != "ok":
            self.quit()

        try:
            self._conflict_check()
            self._build_cmds()
            file_data = self._build_conf()
        except AsoundConfWizardError as err:
            raise err

        choice = Stylize.input(
            f'Please enter "OK" to commit your choices to {ASOUND_FILE_PATH}: '
        )

        if choice.lower() != "ok":
            self.quit()

        try:
            self._backup_asound_conf()
        except AsoundConfWizardError as err:
            raise err

        try:
            with open(ASOUND_FILE_PATH, "w", encoding="utf-8") as asf:
                asf.write(file_data)
        except Exception as err:
            raise AsoundConfWriteError(err) from err

        Stylize.comment(f"{ASOUND_FILE_PATH} was written successfully.")

        Stylize.comment(
            "You can revert your system to it's default state by deleting "
            f"{ASOUND_FILE_PATH} with:"
        )

        Stylize.comment(f"sudo rm {ASOUND_FILE_PATH}")

        Stylize.comment(
            "or optionally revert it from the back up if one was created "
            "if you have any issue with the generated config."
        )

    @staticmethod
    def _conflict_check():
        conflicts = []
        if which("pulseaudio"):
            conflicts.append("PulseAudio")
        if  which("pipewire"):
            conflicts.append("PipeWire")
        if which("jackd"):
            conflicts.append("JACK Audio")
        if conflicts:
            raise AudioSoftwareConflictError(" / ".join(conflicts))

    @staticmethod
    def _privilege_check():
        try:
            with open(DUMMY_FILE_PATH, "w", encoding="utf-8") as _:
                pass

            os_remove(DUMMY_FILE_PATH)
        except Exception as err:
            raise InsufficientPrivilegesError() from err

    @staticmethod
    def _backup_asound_conf():
        try:
            os_rename(ASOUND_FILE_PATH, BACKUP_FILE_PATH)

        except FileNotFoundError:
            pass
        except Exception as err:
            raise RenamingError(err) from err
        else:
            Stylize.comment(f"{ASOUND_FILE_PATH} already exists renaming it to:")
            Stylize.comment(f"{BACKUP_FILE_PATH}")

    @staticmethod
    def _pcm_to_card_device(pcm):
        try:
            [card, device] = pcm.split(",")
            card = card.replace("hw:CARD=", "").strip()
            device = int(device.strip("DEV= "))
        except Exception as err:
            raise PcmParsingError(err) from err

        return card, device

    @staticmethod
    def _invalid_choice(len_choices):
        Stylize.warn(f"Please enter a number from 1 - {len_choices}.")

    @staticmethod
    def _best_choice(best_choice):
        Stylize.suggestion(f"{best_choice} is the best choice.")

    @staticmethod
    def _get_sample_rate_converters():
        while True:
            converters = []
            base_path = glob(CONVERTERS_FILE_PATH)

            if base_path:
                base_path = base_path[0]
                search_term = f"{base_path}{CONVERTERS_SEARCH_SUFFIX}"

                converters = [
                    f.replace(search_term, "").replace(".so", "")
                    for f in glob(f"{search_term}*")
                ]

                ordered_converters = [
                    i for i in COMMON_RATE_CONVERTERS if i in converters
                ]

                leftovers = [i for i in converters if i not in ordered_converters]

                converters = ordered_converters + leftovers

            if converters or not UPDATE_CMD:
                return converters

            confirm = Stylize.input(
                'Please enter "Y" if you would like to install '
                "high quality Sample Rate Converters: "
            )

            if confirm.lower() != "y":
                return converters

            Stylize.comment("This may take a moment…")

            try:
                subprocess_run(
                    UPDATE_CMD,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

                subprocess_run(
                    CONVERTER_INSTALL_CMD,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

            except CalledProcessError as err:
                i_err = InstallError(ALSA_PLUGINS, err.stderr.decode("utf-8"))
                Stylize.warn(i_err)

                return converters

            Stylize.comment(f"{ALSA_PLUGINS} Installed Successfully")

if __name__ == "__main__":
    for sig in (SIGINT, SIGTERM, SIGHUP):
        signal(sig, AsoundConfWizard.quit)
    try:
        AsoundConfWizard().run()
    except AsoundConfWizardError as e:
        Stylize.error(e)
