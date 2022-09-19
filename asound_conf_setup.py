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

if "SUDO_UID" not in os.environ or os.geteuid() != 0:
    print ("Error: This script requires super user privileges.")
    exit(1)

file_path = "/etc/asound.conf"

if os.path.exists(file_path):
    new_name = "/etc/asound.conf.bak{}".format(int(time.time()))

    try:
        os.rename("/etc/asound.conf", new_name)
    except Exception as e:
        print ("Error renaming existing /etc/asound.conf: {}".format(e))
        exit(1)
    else:
        print(
            "/etc/asound.conf already exists renaming it to {}.".format(
                new_name
            )
        )

pcm_names = subprocess.run(
    ["aplay", "-L"],
    stdout=subprocess.PIPE).stdout.decode(
    "utf-8"
)

print("ALSA PCM Names:")
print(pcm_names)

while True:
    try:
        pcm = input(
            "Please enter the Name of the hw PCM you wish "
            "to use (for example hw:CARD=D10s,DEV=0): "
        )

        if pcm.startswith("hw:"):
            card = pcm.replace("hw:CARD=", "").strip()
            [card, dev] = card.split(",")
            dev = dev.replace("DEV=", "").strip()
            dev = int(dev)
        else:
            print("Invalid hw PCM: {}".format(pcm))
            print("Try Again…")
            continue
    except KeyboardInterrupt:
        print("\n")
        exit(0)
    except:
        print("Invalid hw PCM: {}".format(pcm))
        print("Try Again…")
        continue
    else:
        break

result = subprocess.run(
    [
        "aplay",
        "-D{}".format(pcm),
        "--dump-hw-params",
        "/usr/share/sounds/alsa/Front_Right.wav",
    ],
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
)

out = result.stdout.decode("utf-8")
err = result.stderr.decode("utf-8")
hw_params = out or err

formats = []
rates = []

common_formats = [
    "S16_LE",
    "S16_BE",
    "S24_LE",
    "S24_BE",
    "S24_3LE",
    "S24_3BE",
    "S32_LE",
    "S32_BE",
]

common_rates = [
    44100,
    48000,
    88200,
    96000,
    176400,
    192000,
    352800,
    384000,
]

for line in hw_params.split("\n"):
    if line.startswith("FORMAT:"):
        line = line.replace("FORMAT:", "")
        line.strip()

        for format_ in line.split(" "):
            format_.strip()
            if format_ in common_formats:
                formats.append(format_)

    elif line.startswith("RATE:"):
        line = line.replace("RATE:", "")
        line = line.replace("[", "")
        line = line.replace("]", "")
        line.strip()

        for line in line.split(" "):
            line.strip()
            if line:
                try:
                    rate = int(line)
                    if rate in common_rates:
                        rates.append(rate)
                except:
                    pass

if not formats or not rates:
    print(hw_params)
    exit(1)

if len(formats) > 1:
    print("Supported Formats:")

    for i, format_ in enumerate(formats):
        print("{} - {}".format(i + 1, format_))

    while True:
        try:
            choice = input("Please choose the desired supported format: ")
            format_ = formats[int(choice) - 1]
        except KeyboardInterrupt:
            print("\n")
            exit(0)
        except:
            print("Invalid format choice: {}".format(choice))
            print(
                "Try Again, enter a number from 1 - "
                "{}…".format(len(formats))
            )
            continue
        else:
            break

else:
    format_ = formats[0]

    print(
        "{} is the only supported format "
        "so that's what we'll use…".format(format_)
    )

if len(rates) > 1:
    r_range = range(rates[0], rates[-1] + 1)

    rates = [r for r in common_rates if r in r_range]

    print("Supported Sampling Rates:")

    for i, rate in enumerate(rates):
        print("{} - {}".format(i + 1, rate))

    while True:
        try:
            choice = input(
                "Please choose the desired supported sampling rate: "
            )

            rate = rates[int(choice) - 1]
        except KeyboardInterrupt:
            print("\n")
            exit(0)
        except:
            print("Invalid sampling rate choice: {}".format(choice))
            print(
                "Try Again, enter a number from 1 - {}…".format(len(rates))
            )
            continue
        else:
            break

else:
    rate = rates[0]

    print(
        "{} is the only supported sampling rate "
        "so that's what we'll use…".format(
            rate
        )
    )

file_data = """# /etc/asound.conf

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
                card {0}
                device {1}
                nonblock {{
                    @func refer
                    name defaults.pcm.nonblock
                }}
            }}
            channels 2
            rate {2}
            format {3}
        }}
        bindings {{
            0 0
            1 1
        }}
    }}
}}

ctl.!default {{
    type hw
    card {0}
}}""".format(
    card, dev, rate, format_
)

try:
    with open(file_path, "w") as f:
        f.write(file_data)

except Exception as e:
    print("Error: {}".format(e))
    exit(1)

else:
    print(
        "Using Card: {}, Device: {}, "
        "Format: {}, and Sampling Rate: {},".format(card, dev, format_, rate)
    )

    print(
        "/etc/asound.conf was written successfully. "
        "Please verify that it is correct."
    )
