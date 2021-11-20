.PHONY: all clean container apt apt-deploy apt-repo-warning apt-deploy-warning

# You'll need my GPG_KEY for signing, which I'm pretty sure you don't have :P
APT_GPG_KEY?=2CC9B80F5AE2B7ACEFF2BA3209146F2F7953A455
APT_GH_PAGES_REPO?=git@github.com:dtcooper/raspotify.git
RASPOTIFY_AUTHOR?=David Cooper <david@dtcooper.com>

raspotify_*.deb:
	docker build -t raspotify .
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
		raspotify /mnt/raspotify/build.sh

clean:
	rm -rf *.deb librespot raspotify/usr raspotify/DEBIAN/control apt-repo

distclean: clean
	docker rmi -f raspotify || true

apt: apt-repo

apt-repo-warning:
	@printf '\n >> This will overwrite the apt-repo directory. Are you sure? (y/N) '
	@read YESNO; \
	if echo "$$YESNO" | grep -vq '^[yY]'; then \
		exit 1; \
	fi;

apt-repo: raspotify_*.deb apt-repo-warning
# 	# Shallow clone of github pages for overwrite
	rm -rf apt-repo
	git clone -b gh-pages --single-branch "$(APT_GH_PAGES_REPO)" apt-repo
	docker build -t raspotify .
#	# Needs an interactive terminal to get gpg passphrase
	docker run \
			--interactive \
			--tty \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--volume "$(HOME)/.gnupg:/root/.gnupg" \
			--env GPG_KEY="$(APT_GPG_KEY)" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
		raspotify /mnt/raspotify/make-apt-repo.sh

apt-deploy-warning:
	@printf '\n >> This will amend and overwrite the last commit to the gh-pages branch, and\n'
	@printf ' >> *FORCE PUSH* the branch to $(APT_GH_PAGES_REPO). Are you sure? (y/N) '
	@read YESNO; \
	if echo "$$YESNO" | grep -vq '^[yY]'; then \
		exit 1; \
	fi;

apt-deploy: apt apt-deploy-warning
	gpg --armor --export "$(APT_GPG_KEY)" > apt-repo/key.asc
	cp -v README.md LICENSE install.sh apt-repo
	cd apt-repo && git add -A
	cd apt-repo && git commit -m "Update gh-pages apt repository (release)"
	cd apt-repo && git push origin gh-pages

all: raspotify_*.deb
