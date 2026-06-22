#!/bin/sh
# vi: set noexpandtab sw=4 ts=4 sts=4:
#
# Turn the copied-in Raspberry Pi OS (Raspbian) ARMv6 rootfs into a sysroot the
# Debian cross gcc can link against, and stage its ARMv6 startup files for that
# link step. Run once when building the ARMv6 builder image (Dockerfile.armv6).
#
# Environment inputs:
#   RPI_SYSROOT  the Raspbian rootfs, fixed up in place                (required)
#   V6GCC        a dedicated dir to collect the ARMv6 startup files in (required)
#
# gcc versions and library sonames are detected rather than hard-coded: they
# change if the Raspbian base image (Dockerfile.armv6) is bumped to a newer
# suite, so detecting keeps that a one-line change instead of breaking here.

set -eu
: "${RPI_SYSROOT:?RPI_SYSROOT must be set}"
: "${V6GCC:?V6GCC must be set}"

# The arm-linux-gnueabihf library dirs. Debian splits glibc across /lib and
# /usr/lib, so both may exist; fix up each in place.
for d in usr/lib/arm-linux-gnueabihf lib/arm-linux-gnueabihf; do
	dir="$RPI_SYSROOT/$d"
	[ -d "$dir" ] || continue

	# Drop the static glibc archives: they reference loader internals that
	# don't cross-link, so removing them forces ld onto the shared libs.
	for name in pthread dl rt util anl resolv m c; do
		rm -f "$dir/lib$name.a"
	done

	# glibc >= 2.34 folded pthread/dl/rt/util/anl/resolv into libc, leaving
	# only empty stub .so.N files and dropping the unversioned lib<name>.so
	# that "-lpthread", "-ldl", etc. need. Recreate each one pointing at its
	# stub (ln -sfn also repairs a leftover dangling symlink).
	for name in pthread dl rt util anl resolv; do
		[ -e "$dir/lib$name.so" ] && continue
		stub=$(ls -1 "$dir/lib$name.so."* 2>/dev/null | sort -V | tail -n1 || true)
		[ -n "$stub" ] && ln -sfn "$(basename "$stub")" "$dir/lib$name.so"
	done
done

# ld follows absolute symlinks against the builder's real "/", where the target
# is the host's ARMv7 lib or nothing ("cannot find -lm"). Re-point every
# absolute symlink (-lname '/*') at the same file inside the sysroot, relative.
find "$RPI_SYSROOT" -type l -lname '/*' | while IFS= read -r link; do
	target=$(readlink "$link")
	ln -sfn "$(realpath -m --relative-to="$(dirname "$link")" "$RPI_SYSROOT$target")" "$link"
done

# Debian's arm-linux-gnueabihf-gcc is only the link driver; by default it links
# the cross toolchain's ARMv7 startup files, which SIGILL on an ARM1176. Collect
# the sysroot's ARMv6 ones into V6GCC -- nothing else lives there -- so build.sh
# can pass "-B$V6GCC" and have gcc prefer them:
#   - gcc's crt*.o (crtbegin*/crtend*) and libgcc.a, from its versioned dir
#   - glibc's crt1.o/crti.o/crtn.o/Scrt1.o, from the lib dir
gcc_dir="$RPI_SYSROOT/usr/lib/gcc/arm-linux-gnueabihf"
gcc_ver=$(ls "$gcc_dir" | grep -E '^[0-9]+$' | sort -n | tail -1)  # newest gcc major
[ -d "$gcc_dir/$gcc_ver" ] || { echo "no gcc found in $gcc_dir" >&2; exit 1; }
lib_dir="$RPI_SYSROOT/usr/lib/arm-linux-gnueabihf"

mkdir -p "$V6GCC"
cp "$gcc_dir/$gcc_ver/"crt*.o "$gcc_dir/$gcc_ver/libgcc.a" "$V6GCC/"
cp "$lib_dir/crt1.o" "$lib_dir/crti.o" "$lib_dir/crtn.o" "$lib_dir/Scrt1.o" "$V6GCC/"

echo "ARMv6 sysroot prepared; v6 startfiles staged in $V6GCC"
