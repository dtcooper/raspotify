#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, amd64 or riscv64 Debian based OS."

SUDO="sudo"

if ! which apt-get >/dev/null; then
	echo "\nUnspported OS:\n"
	echo "$ERROR_MESG"
	exit 1
fi

# ARMv6 (Pi v1 / Pi Zero v1.x) is built and reported by Raspberry Pi OS as
# "armhf", the same as the ARMv7 build, so the two cannot be told apart in a
# single apt repository. ARMv6 is therefore shipped as a standalone .deb rather
# than via this apt-based installer. See ARMV6.md.
if uname -a | grep -F -iq -e armv6; then
	echo "\nARMv6 detected (Pi v1 / Pi Zero v1.x):\n"
	echo "Raspotify is available for ARMv6 as a standalone .deb (not via this apt repo)."
	echo "Download raspotify_*_armv6.deb from the releases page and install it with:"
	echo "\n    sudo dpkg -i raspotify_*_armv6.deb"
	echo "    sudo apt-get -f install   # to pull in any missing dependencies\n"
	echo "    https://github.com/dtcooper/raspotify/releases\n"
	exit 1
fi

if uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64 -e riscv64; then
	echo "\nUnspported architecture:\n"
	echo "$ERROR_MESG"
	exit 1
fi

if ! which sudo >/dev/null; then
	SUDO=""

	if [ "$(id -u)" -ne 0 ]; then
		echo "\nInsufficient privileges:\n"
		echo "Please run this script as root."
		exit 1
	fi
fi

$SUDO curl -sSfL https://dtcooper.github.io/raspotify/key.asc -o /usr/share/keyrings/raspotify_key.asc
$SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $SUDO tee /etc/apt/sources.list.d/raspotify.list

$SUDO apt-get update
$SUDO apt-get -y install raspotify

echo
echo "Thanks for installing Raspotify!"
echo
echo "Check the Wiki for tips, tricks and configuration info:"
echo
echo "    https://github.com/dtcooper/raspotify/wiki"
echo
echo "And if you're feeling generous, you could buy me a beer:"
echo
echo "    https://github.com/sponsors/kimtore"
echo
