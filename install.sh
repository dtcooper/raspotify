#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, or amd64 Debian based OS."

SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
LIBASOUND_MIN_VER="1.2.4"
LIBPULSE_MIN_VER="14.2"

MAYBE_SUDO="sudo"

REQ_PACKAGES="systemd init-system-helpers libasound2 libpulse0 curl apt-transport-https"

# Check if we're running on Debian or a derivative of Debian.
# Are we running on an OS with apt?
if ! which apt-get apt-key > /dev/null; then
    echo "Unspported OS:"
    echo "$ERROR_MESG"
    exit 1
fi

# Check if we're running on a supported architecture?
if uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64; then
    echo "Unspported architecture:"
    echo "$ERROR_MESG"
    exit 1
fi

# Can we maybe get privileges with sudo?
if ! which sudo > /dev/null; then
    MAYBE_SUDO=""
    # If not, are we root?
    if [ "$(id -u)" -ne 0 ]; then
        echo "Insufficient privileges:"
        echo "Please run this script as root."
        exit 1
    fi
fi

# Make sure Raspotify's (systemd init-system-helpers libasound2 libpulse0),
# the script's (curl) and the repo's (apt-transport-https)
# dependencies are installed.
PACKAGES_TO_INSTALL=
for package in $REQ_PACKAGES; do
    if ! dpkg-query -W -f='${db:Status-Status}\n' "$package" 2> /dev/null | grep -q '^installed$'; then
        PACKAGES_TO_INSTALL="$package $PACKAGES_TO_INSTALL"
    fi
done

# If not offer to install them.
if [ "$PACKAGES_TO_INSTALL" ]; then
    echo "Unmet dependencies:"

    for package in $PACKAGES_TO_INSTALL; do
        echo "$package"
    done

    echo "They must be installed to continue with this script."
    printf "Do you want to install them now? [y/N] "

    read -r REPLY
    if ! echo "$REPLY" | grep -Eiq "(y|yes)"; then
        echo "No changes to your system were made."
        echo "Raspotify was not installed and it's repository was not added."
        exit 0
    fi

    $MAYBE_SUDO apt update
    $MAYBE_SUDO apt -y install $PREREQ_PACKAGES_TO_INSTALL
fi

# Check the installed versions of Raspotify's dependencies.
SYSTEMD_VER="$(dpkg-query -W -f='${Version}' systemd)"
HELPER_VER="$(dpkg-query -W -f='${Version}' init-system-helpers)"
LIBASOUND_VER="$(dpkg-query -W -f='${Version}' libasound2)"
LIBPULSE_VER="$(dpkg-query -W -f='${Version}' libpulse0)"

# Make sure they meet the minimum required package versions before we add the repo.
# A person could add the repo without making sure the minimum required package versions
# were met but the package would just refuse to install, so I'm not sure what good that would be? 
MIN_NOT_MET=
if eval dpkg --compare-versions "$SYSTEMD_VER" lt "$SYSTEMD_MIN_VER"; then
    MIN_NOT_MET="systemd (>= $SYSTEMD_MIN_VER) but $SYSTEMD_VER is installed.\n"
fi

if eval dpkg --compare-versions "$HELPER_VER" lt "$HELPER_MIN_VER"; then
    MIN_NOT_MET="$MIN_NOT_MET\ninit-system-helpers (>= $HELPER_MIN_VER) but $HELPER_VER is installed.\n"
fi

if eval dpkg --compare-versions "$LIBASOUND_VER" lt "$LIBASOUND_MIN_VER"; then
    MIN_NOT_MET="$MIN_NOT_MET\nlibasound2 (>= $LIBASOUND_MIN_VER) but $LIBASOUND_VER is installed.\n"
fi

if eval dpkg --compare-versions "$LIBPULSE_VER" lt "$LIBPULSE_MIN_VER"; then
    MIN_NOT_MET="$MIN_NOT_MET\nlibpulse0 (>= $LIBPULSE_MIN_VER) but $LIBPULSE_VER is installed.\n"
fi

if [ "$MIN_NOT_MET" ]; then
    echo "Unmet minimum required package version(s):"
    printf "%b" "$MIN_NOT_MET"
    echo "$ERROR_MESG"
    exit 1
fi

# Add the repos and install Raspotify.
curl -sSL https://dtcooper.github.io/raspotify/key.asc | $MAYBE_SUDO tee /usr/share/keyrings/raspotify_key.asc > /dev/null
$MAYBE_SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $MAYBE_SUDO tee /etc/apt/sources.list.d/raspotify.list

$MAYBE_SUDO apt update
$MAYBE_SUDO apt install -y raspotify

# Thanks and shameless money grab.
echo "Thanks for install Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "And if you're feeling generous you could buy me a RedBull:"
echo "https://github.com/sponsors/JasonLG1979"
