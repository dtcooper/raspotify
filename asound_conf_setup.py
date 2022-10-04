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

import wave
from textwrap import TextWrapper
from glob import glob
from shutil import which
from sys import exit as sys_exit
from sys import byteorder as sys_byteorder
from signal import signal, SIGINT, SIGTERM, SIGHUP
from subprocess import CalledProcessError, PIPE, STDOUT, DEVNULL
from subprocess import run as subprocess_run
from os import rename as os_rename
from os import remove as os_remove
from time import time as time_time
from tempfile import gettempdir
from dataclasses import dataclass

ASOUND_FILE_PATH = "/etc/asound.conf"
DUMMY_FILE_PATH = f"/etc/foobarbaz{int(time_time())}"
BACKUP_FILE_PATH = f"/etc/asound.conf.bak{int(time_time())}"
SILENCE_FILE_PATH = f"{gettempdir()}/silence{int(time_time())}.wav"
MIC_CHECK_FILE_PATH = f"{gettempdir()}/mic-check{int(time_time())}.wav"
CONVERTERS_FILE_PATH = "/usr/lib/*/alsa-lib"
CONVERTERS_SEARCH_SUFFIX = "/libasound_module_rate_"
ALSA_PLUGINS = "libasound2-plugins"
ALSA_UTILS = "alsa-utils"

NOT_SUPPORTED_BY_SPEAKER_TEST = ("S24_LE", "S24_BE")

APT = which("apt")
SUDO = which("sudo")

if APT:
    if SUDO:
        UPDATE_CMD = (SUDO, APT, "update")

        ALSA_UTILS_INSTALL_CMD = (
            SUDO,
            APT,
            "install",
            "-y",
            ALSA_UTILS,
        )

        CONVERTER_INSTALL_CMD = (
            SUDO,
            APT,
            "install",
            "-y",
            "--no-install-recommends",
            ALSA_PLUGINS,
        )

    else:
        UPDATE_CMD = (APT, "update")

        ALSA_UTILS_INSTALL_CMD = (
            APT,
            "install",
            "-y",
            ALSA_UTILS,
        )

        CONVERTER_INSTALL_CMD = (
            APT,
            "install",
            "-y",
            "--no-install-recommends",
            ALSA_PLUGINS,
        )

else:
    UPDATE_CMD = None
    CONVERTER_INSTALL_CMD = None
    ALSA_UTILS_INSTALL_CMD = None

# See:
# https://github.com/alsa-project/alsa-lib/blob/master/src/pcm/pcm_dmix_generic.c#L121
if sys_byteorder == "little":
    FORMATS = (
        "U8",
        "S16_LE",
        "S24_LE",
        "S24_3LE",
        "S32_LE",
    )
else:
    FORMATS = (
        "U8",
        "S16_BE",
        "S24_BE",
        "S24_3BE",
        "S32_BE",
    )

# See:
# https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Audio_sampling
RATES = (
    8000,
    11025,
    16000,
    22050,
    32000,
    37800,
    44056,
    44100,
    47250,
    48000,
    50000,
    50400,
    64000,
    88200,
    96000,
    176400,
    192000,
    352800,
    384000,
)

COMMON_RATE_CONVERTERS = (
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
)

CHANNELS = (
    1,
    2,
    4,
    6,
    8,
)

# dmix and dsnoop are basically mirror images of each other.
# playback_capture, dmix_dsnoop, card, device, channels, rate, format
# See:
# https://github.com/alsa-project/alsa-lib/blob/master/src/conf/pcm/dmix.conf
# https://github.com/alsa-project/alsa-lib/blob/master/src/conf/pcm/dsnoop.conf
PLAYBACK_CAPTURE_TEMPLATE = """
pcm.{playback_capture} {{
    type {dmix_dsnoop}
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
    tstamp_type {{
        @func refer
        name defaults.pcm.tstamp_type
    }}
    slave {{
        pcm {{
            type hw
            card {card}
            device {device}
        }}
        channels {channels}
        rate {rate}
        format {fmt}
    }}
}}
"""

# input_converter, input_pcm,
# output_route_policy, output_converter, output_pcm
# See:
# https://github.com/alsa-project/alsa-lib/blob/master/src/pcm/pcm_asym.c#L20
ASYM_DEFAULT_TEMPLATE = """
pcm.!default {{
    type asym
    capture.pcm {{
        type plug
        {input_converter}
        slave.pcm {input_pcm}
    }}
    playback.pcm {{
        type plug
        route_policy {output_route_policy}
        {output_converter}
        slave.pcm {output_pcm}
    }}
}}
"""
# output_rate, output_fmt, output_channels
HDMI_TEMPLATE = """
defaults.pcm.dmix.rate {output_rate}
defaults.pcm.dmix.format {output_fmt}
defaults.pcm.dmix.channels {output_channels}
"""

# output_card
DEFAULT_CONTROL_TEMPLATE = """
ctl.!default {{
    type hw
    card {output_card}
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
        message="This script requires that aplay, arecord and speaker-test be installed",
    ):
        self.message = message
        super().__init__(self.message)

class RenamingError(AsoundConfWizardError):
    """Renaming Error"""
    def __init__(self, error, message=f"Could not rename existing {ASOUND_FILE_PATH}"):
        self.message = f"{message}: {error}"
        super().__init__(self.message)

class NoOuputPcmError(AsoundConfWizardError):
    """No Output Pcm Error"""
    def __init__(self, error, message="No available Output PCM"):
        if error:
            message = f"{message}: {error}"
        self.message = message
        super().__init__(self.message)

class NoInputPcmError(AsoundConfWizardError):
    """No Input Pcm Error"""
    def __init__(self, error, message="No available Input PCM"):
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

@dataclass(frozen=True)
class InputOuput:
    """Input Ouput data class"""
    pcm: str
    card: str
    device: int
    fmt: str
    rate: int
    converter: str or None
    channel_count: int

class Stylize:
    """Stylize Text"""
    _BOLD = "\033[1m"
    _CYAN = "\033[36m"
    _BOLD_YELLOW = "\033[1;33m"
    _BOLD_RED = "\033[1;31m"
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

        for i, (name, desc) in enumerate(pcms):
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

        for i, (key, value) in enumerate(choices):
            num = i + 1
            center_pad = (self._width - len(key)) + int(self._padding / 2)

            row = f"{{:<{pad}}}{{:>{pad}}}{{:>{center_pad}}}{{:>{pad}}}".format(
                "┃", key, value, "┃"
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
        self._get_output_pcm_names_cmd = ()
        self._get_input_pcm_names_cmd = ()
        self._output_hw_params_cmd_template = ""
        self._input_hw_params_cmd_template = ""
        self._speaker_test_cmd_template = ""
        self._mic_test_cmd_template = ""

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
        arecord = which("arecord")
        speaker_test = which("speaker-test")

        if aplay and arecord and speaker_test:
            self._get_output_pcm_names_cmd = (aplay, "-L")
            self._get_input_pcm_names_cmd = (arecord, "-L")

            self._output_hw_params_cmd_template = (
                f"{aplay} -D{{}} --dump-hw-params {SILENCE_FILE_PATH}"
            )

            self._input_hw_params_cmd_template = (
                f"{arecord} -D{{}} -d1 --dump-hw-params {MIC_CHECK_FILE_PATH}"
            )

            self._speaker_test_cmd_template = (
                f"{speaker_test} -D{{}} -F{{}} -r{{}} -l1 -c{{}} -S25"
            )

            self._mic_test_cmd_template = (
                f"{arecord} -D{{}} -f{{}} -r{{}} -c{{}} " f"-d1 {MIC_CHECK_FILE_PATH}"
            )

        elif not ALSA_UTILS_INSTALL_CMD:
            raise MissingDependenciesError()
        else:
            Stylize.comment(
                "This script requires aplay, arecord and speaker-test "
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
                arecord = which("arecord")
                speaker_test = which("speaker-test")

                if aplay and arecord and speaker_test:
                    Stylize.comment(f"{ALSA_UTILS} Installed Successfully")
                    self._get_output_pcm_names_cmd = (aplay, "-L")
                    self._get_input_pcm_names_cmd = (arecord, "-L")

                    self._output_hw_params_cmd_template = (
                        f"{aplay} -D{{}} --dump-hw-params {SILENCE_FILE_PATH}"
                    )

                    self._input_hw_params_cmd_template = (
                        f"{arecord} "
                        f"-D{{}} -d1 --dump-hw-params {MIC_CHECK_FILE_PATH}"
                    )

                    self._speaker_test_cmd_template = (
                        f"{speaker_test} -D{{}} -F{{}} -r{{}} -l1 -c{{}} -S25"
                    )

                    self._mic_test_cmd_template = (
                        f"{arecord} "
                        "-D{} -f{} -r{} -c{} "
                        f"-d1 {MIC_CHECK_FILE_PATH}"
                    )

                else:
                    raise MissingDependenciesError()

    def _get_output_pcms(self):
        try:
            pcm_names = (
                subprocess_run(
                    self._get_output_pcm_names_cmd,
                    check=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode("utf-8")
                .split("\n")
            )
        except CalledProcessError as err:
            raise NoOuputPcmError(err.stderr.decode("utf-8")) from err

        pcms = tuple(
            (n.strip(), pcm_names[i + 1].strip())
            for i, n in enumerate(pcm_names)
            if n.startswith("hdmi:")
            or (n.startswith("hw:") and not n.replace("hw:", "hdmi:") in pcm_names)
        )

        if not pcms:
            raise NoOuputPcmError(None)

        return pcms

    def _get_input_pcms(self):
        try:
            pcm_names = (
                subprocess_run(
                    self._get_input_pcm_names_cmd,
                    check=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode("utf-8")
                .split("\n")
            )
        except CalledProcessError as err:
            raise NoInputPcmError(err.stderr.decode("utf-8")) from err

        pcms = tuple(
            (n.strip(), pcm_names[i + 1].strip())
            for i, n in enumerate(pcm_names)
            if n.startswith("hw:")
        )

        if not pcms:
            raise NoInputPcmError(None)

        return pcms

    def _choose_pcm(self, pcm_type):
        if pcm_type == "Input":
            try:
                pcms = self._get_input_pcms()
            except NoInputPcmError as err:
                raise err
        else:
            try:
                pcms = self._get_output_pcms()
            except NoOuputPcmError as err:
                raise err

        if len(pcms) > 1:
            self._show_pcm_table(f"{pcm_type}s", pcms)

            while True:
                choice = Stylize.input(f"Please choose an {pcm_type}: ")
                try:
                    pcm = pcms[int(choice) - 1][0]
                except (ValueError, IndexError):
                    self._invalid_choice(len(pcms))
                    continue
                else:
                    break
        else:
            pcm = pcms[0][0]
            Stylize.comment(
                f"[{pcm}] is the only available {pcm_type} so that's what we'll use…"
            )

        return pcm

    def _get_params(self, pcm, pcm_type):
        def try_get_int(thing):
            try:
                return int(thing)
            except ValueError:
                return None

        Stylize.comment(
            f"{pcm_type}s must not be in use while querying their Hardware Parameters."
        )

        Stylize.comment(
            f"Please make sure the {pcm_type} you chose is not in use before continuing."
        )

        enter = Stylize.input("Please press Enter to continue")

        if enter != "":
            self.quit()

        try:
            if pcm_type == "Input":
                cmd = self._input_hw_params_cmd_template.format(pcm).split(" ")

                hw_params = subprocess_run(
                    cmd,
                    check=False,
                    stderr=STDOUT,
                    stdout=PIPE,
                ).stdout.decode("utf-8")

                os_remove(MIC_CHECK_FILE_PATH)
            else:
                cmd = self._output_hw_params_cmd_template.format(pcm).split(" ")

                # aplay will not dump-hw-params without at least
                # trying to read a file it does not matter if the
                # device can actually play it or not so we just write
                # a 1 sec mono wav to tmp and delete it after aplay
                # tries to read it.
                with wave.open(SILENCE_FILE_PATH, mode="wb") as silence:
                    silence.setnchannels(1)
                    silence.setsampwidth(2)
                    silence.setframerate(44100)
                    silence.writeframes(bytearray(44100))

                hw_params = subprocess_run(
                    cmd,
                    check=False,
                    stderr=STDOUT,
                    stdout=PIPE,
                ).stdout.decode("utf-8")

                os_remove(SILENCE_FILE_PATH)

        except FileNotFoundError:
            pass
        except Exception as err:
            raise PcmOpenError(err) from err

        if "audio open error:" in hw_params:
            err = hw_params.split(":")[-1].strip().title()
            raise PcmOpenError(err)

        formats = ()
        rates = ()
        channels = ()

        for line in hw_params.split("\n"):
            if line.startswith("FORMAT:"):
                formats = tuple(
                    fmt for fmt in FORMATS if fmt in line.strip("FORMAT: ").split(" ")
                )

            elif line.startswith("RATE:"):
                rates = tuple(
                    rate
                    for rate in RATES
                    if rate
                    in tuple(
                        try_get_int(rate) for rate in line.strip("RATE:[ ]").split(" ")
                    )
                )

            elif line.startswith("CHANNELS:"):
                channels = tuple(
                    channel
                    for channel in CHANNELS
                    if channel
                    in tuple(
                        try_get_int(channel)
                        for channel in line.strip("CHANNELS:[ ]").split(" ")
                    )
                )

        return formats, rates, channels

    def _choose_channel_count(self, channels, pcm_type):
        if len(channels) > 1:
            c_range = range(channels[0], channels[-1] + 1)
            channels = tuple(c for c in CHANNELS if c in c_range)

            self._show_channel_count_table(f"{pcm_type} Channel Counts", channels)

            while True:
                choice = Stylize.input(f"Please choose an {pcm_type} Channel Count: ")
                try:
                    channel_count = channels[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(channels))
                    continue
                else:
                    break
        else:
            channel_count = channels[0]

            Stylize.comment(
                f"[{channel_count}] is the only {pcm_type} Channel Count so that's what we'll use…"
            )

        return channel_count

    def _choose_format(self, formats, pcm_type):
        if len(formats) > 1:
            self._show_format_table(f"{pcm_type} Formats", formats)

            while True:
                choice = Stylize.input(f"Please choose an {pcm_type} Format: ")
                try:
                    fmt = formats[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(formats))
                    continue
                else:
                    break
        else:
            fmt = formats[0]
            Stylize.comment(
                f"[{fmt}] is the only {pcm_type} Format so that's what we'll use…"
            )

        return fmt

    def _choose_rate(self, rates, pcm_type):
        if len(rates) > 1:
            r_range = range(rates[0], rates[-1] + 1)
            rates = tuple(r for r in RATES if r in r_range)

            self._show_rate_table(f"{pcm_type} Sampling Rates", rates)

            while True:
                choice = Stylize.input(f"Please choose an {pcm_type} Sampling Rate: ")
                try:
                    rate = rates[int(choice) - 1]
                except (ValueError, IndexError):
                    self._invalid_choice(len(rates))
                    continue
                else:
                    break
        else:
            rate = rates[0]

            Stylize.comment(
                f"[{rate}] is the only {pcm_type} Sampling Rate so that's what we'll use…"
            )

        return rate

    def _choose_sample_rate_converter(self, pcm_type, ask):
        converters = self._get_sample_rate_converters(ask)
        if len(converters) > 1:
            self._show_converter_table(f"{pcm_type} Rate Converters", converters)

            while True:
                choice = Stylize.input(
                    f"Please choose an {pcm_type} Sample Rate Converter: "
                )
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
                    f"[{converter}] is the only {pcm_type} "
                    "Sample Rate Converter so that's what we'll use…"
                )
            else:
                converter = None

        return converter

    def _get_choices(self, pcm_type, ask):
        while True:
            try:
                pcm = self._choose_pcm(pcm_type)

            except (NoOuputPcmError, NoInputPcmError) as err:
                raise err
            try:
                formats, rates, channels = self._get_params(pcm, pcm_type)

            except PcmOpenError as err:
                Stylize.warn(err)
                if "busy" in err.message:
                    Stylize.warn(
                        f"Please make sure the {pcm_type} you chose is not in use and try again."
                    )
                elif "No Such Device" in err.message:
                    Stylize.warn(
                        f"Digital {pcm_type}s may need to be plugged into "
                        "something to be functional."
                    )

                    Stylize.warn(
                        f"If so please connect the {pcm_type} to something and try again."
                    )

                    Stylize.warn(f"Otherwise please choose a different {pcm_type}.")

                continue

            if not formats or not rates or not channels:
                Stylize.warn(
                    "No supported formats, sampling rates or channel counts were returned."
                )

                Stylize.warn(
                    f"The {pcm_type} you chose may not support any common formats and rates?"
                )

                Stylize.warn(
                    f"Digital {pcm_type}s may need to be plugged into something to be functional."
                )

                Stylize.warn(
                    f"If so please connect the {pcm_type} to something and try again."
                )

                Stylize.warn(f"Otherwise please choose a different {pcm_type}.")
                continue

            fmt = self._choose_format(formats, pcm_type)
            rate = self._choose_rate(rates, pcm_type)
            channel_count = self._choose_channel_count(channels, pcm_type)
            converter = self._choose_sample_rate_converter(pcm_type, ask)
            card, device = self._pcm_to_card_and_device(pcm)

            return InputOuput(pcm, card, device, fmt, rate, converter, channel_count)

    def _test_output_choices(self):
        while True:
            output_choices = self._get_choices("Output", True)

            if output_choices.card == "vc4hdmi":
                Stylize.warn(
                    "[vc4hdmi] does not support software mixing. Only one application "
                    "will be able to use it at a time."
                )

                confirm = Stylize.input(
                    'Please enter "Y" if you would like to use it anyway: '
                )

                if confirm.lower() != "y":
                    continue

            choices = [
                ("Output", output_choices.pcm),
                ("Format", output_choices.fmt),
                ("Sampling Rate", str(output_choices.rate)),
                ("Channel Count", str(output_choices.channel_count)),
            ]

            if output_choices.converter:
                choices.append(("Sample Rate Converter", output_choices.converter))

            self._show_choices_table("Your Output Choices", choices)

            if output_choices.fmt in NOT_SUPPORTED_BY_SPEAKER_TEST:
                return output_choices

            Stylize.comment(
                "Unless you are ABSOLUTELY certain your choices are correct you should test them."
            )

            confirm = Stylize.input(
                'Please enter "Y" if you would like to test your choices: '
            )

            if confirm.lower() != "y":
                return output_choices

            Stylize.comment(
                "Please make sure your Output is connected, "
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
                output_choices.pcm,
                output_choices.fmt,
                output_choices.rate,
                output_choices.channel_count,
            ).split(" ")

            try:
                subprocess_run(
                    cmd,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

            except CalledProcessError as err:
                Stylize.warn(f"The Speaker Test Failed: {err.stderr.decode('utf-8')}")

                Stylize.warn(
                    "Please try again with a different Format, "
                    "Sampling Rate and Channel Count combination."
                )

                continue

            confirm = Stylize.input('Please enter "Y" if you heard the test tones: ')

            if confirm.lower() == "y":
                return output_choices

            Stylize.warn(
                "Please make sure you're connected to the correct Output and try again."
            )

    def _test_input_choices(self):
        confirm = Stylize.input(
            'Please enter "Y" if you would like to configure an Input also: '
        )

        if confirm.lower() != "y":
            return None

        while True:
            try:
                input_choices = self._get_choices("Input", False)
            except NoInputPcmError as err:
                Stylize.warn(err)
                Stylize.warn("Please make sure the Input is connected.")
                confirm = Stylize.input(
                    'Please enter "Y" if you would like to try again: '
                )

                if confirm.lower() != "y":
                    return None

                continue

            choices = [
                ("Input", input_choices.pcm),
                ("Format", input_choices.fmt),
                ("Sampling Rate", str(input_choices.rate)),
                ("Channel Count", str(input_choices.channel_count)),
            ]

            if input_choices.converter:
                choices.append(("Sample Rate Converter", input_choices.converter))

            self._show_choices_table("Your Input Choices", choices)

            Stylize.comment(
                "Unless you are ABSOLUTELY certain your choices are correct you should test them."
            )

            confirm = Stylize.input(
                'Please enter "Y" if you would like to test your choices: '
            )

            if confirm.lower() != "y":
                return input_choices

            cmd = self._mic_test_cmd_template.format(
                input_choices.pcm,
                input_choices.fmt,
                input_choices.rate,
                input_choices.channel_count,
            ).split(" ")

            try:
                subprocess_run(
                    cmd,
                    check=True,
                    stderr=PIPE,
                    stdout=DEVNULL,
                )

                os_remove(MIC_CHECK_FILE_PATH)

            except FileNotFoundError:
                pass
            except CalledProcessError as err:
                Stylize.warn(f"The Mic Test Failed: {err.stderr.decode('utf-8')}")

                Stylize.warn(
                    "Please try again with a different Format, "
                    "Sampling Rate and Channel Count combination."
                )

                continue

            return input_choices

    def _build_conf(self):
        input_choices = None
        try:
            output_choices = self._test_output_choices()
        except AsoundConfWizardError as err:
            raise err

        try:
            input_choices = self._test_input_choices()
        except AsoundConfWizardError as err:
            raise err

        if output_choices.converter:
            output_converter = f"rate_converter {output_choices.converter}"
        else:
            output_converter = ""

        if input_choices and input_choices.converter:
            input_converter = f"rate_converter {input_choices.converter}"
        else:
            input_converter = ""

        config_blocks = []

        if output_choices.card == "b1" or output_choices.pcm.startswith("hdmi:"):
            output_pcm = output_choices.pcm

            playback = HDMI_TEMPLATE.format(
                output_rate=output_choices.rate,
                output_fmt=output_choices.fmt,
                output_channels=output_choices.channel_count,
            ).strip()

        else:
            output_pcm = "playback"

            playback = PLAYBACK_CAPTURE_TEMPLATE.format(
                playback_capture="playback",
                dmix_dsnoop="dmix",
                card=output_choices.card,
                device=output_choices.device,
                channels=output_choices.channel_count,
                rate=output_choices.rate,
                fmt=output_choices.fmt,
            ).strip()

        config_blocks.append(playback)
        config_blocks.append("\n")

        if input_choices:
            input_pcm = "capture"

            capture = PLAYBACK_CAPTURE_TEMPLATE.format(
                playback_capture="capture",
                dmix_dsnoop="dsnoop",
                card=input_choices.card,
                device=input_choices.device,
                channels=input_choices.channel_count,
                rate=input_choices.rate,
                fmt=input_choices.fmt,
            ).strip()

            config_blocks.append(capture)
            config_blocks.append("\n")

        else:
            input_pcm = "null"

        if output_choices.channel_count == 1:
            output_route_policy = "average"
        elif output_choices.channel_count == 2:
            output_route_policy = "copy"
        else:
            output_route_policy = "duplicate"

        asym_default = ASYM_DEFAULT_TEMPLATE.format(
            input_converter=input_converter,
            input_pcm=f'"{input_pcm}"',
            output_route_policy=output_route_policy,
            output_converter=output_converter,
            output_pcm=f'"{output_pcm}"',
        ).strip()

        config_blocks.append(
            "\n".join(tuple(l for l in asym_default.split("\n") if l.strip()))
        )

        config_blocks.append("\n")

        control = DEFAULT_CONTROL_TEMPLATE.format(
            output_card=output_choices.card
        ).strip()

        config_blocks.append(control)

        file_data = "\n".join(config_blocks).strip()

        return file_data

    def _write_asound_conf(self):
        Stylize.comment(
            f"This script will backup {ASOUND_FILE_PATH} if it already exists, "
            f"and create a new {ASOUND_FILE_PATH} based on your choices."
        )

        Stylize.comment("This will create a system wide static audio configuration.")

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
        conflicts = tuple(
            name
            for program, name in (
                ("pulseaudio", "PulseAudio"),
                ("pipewire", "PipeWire"),
                ("jackd", "JACK Audio"),
            )
            if which(program)
        )

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
    def _pcm_to_card_and_device(pcm):
        try:
            card, device = pcm.split(",")
            for sub in (("hw:CARD=", ""), ("hdmi:CARD=", "")):
                card = card.replace(*sub).strip()
            device = int(device.replace("DEV=", "").strip())
        except Exception as err:
            raise PcmParsingError(err) from err

        return card, device

    @staticmethod
    def _show_pcm_table(title, pcms):
        width = max(
            len(max(tuple(n for s in pcms for n in s), key=len)),
            len(title),
        )

        table = Table(title, width)
        table.add_pcms(pcms)

    @staticmethod
    def _show_rate_table(title, rates):
        width = max(len(max(tuple(str(r) for r in rates), key=len)), len(title))
        table = Table(title, width)
        table.add(rates)

    @staticmethod
    def _show_format_table(title, formats):
        width = max(len(max(formats, key=len)), len(title))
        table = Table(title, width)
        table.add(formats)

    @staticmethod
    def _show_channel_count_table(title, channels):
        width = max(len(max(tuple(str(c) for c in channels), key=len)), len(title))
        table = Table(title, width)
        table.add(channels)

    @staticmethod
    def _show_converter_table(title, converters):
        width = max(len(max(converters, key=len)), len(title))
        table = Table(title, width)
        table.add(converters)

    @staticmethod
    def _show_choices_table(title, choices):
        width = max(len(max(tuple("".join(c) for c in choices), key=len)), len(title))
        table = Table(title, width)
        table.add_choices(choices)

    @staticmethod
    def _invalid_choice(len_choices):
        Stylize.warn(f"Please enter a Number: [1 - {len_choices}].")

    @staticmethod
    def _get_sample_rate_converters(ask):
        while True:
            converters = ()
            base_path = glob(CONVERTERS_FILE_PATH)

            if base_path:
                base_path = base_path[0]
                search_term = f"{base_path}{CONVERTERS_SEARCH_SUFFIX}"

                converters = tuple(
                    f.replace(search_term, "").replace(".so", "")
                    for f in glob(f"{search_term}*")
                )

                ordered_converters = tuple(
                    i for i in COMMON_RATE_CONVERTERS if i in converters
                )

                leftovers = tuple(i for i in converters if i not in ordered_converters)

                converters = ordered_converters + leftovers

            if converters or not UPDATE_CMD or not ask:
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
