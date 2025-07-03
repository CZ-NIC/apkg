#!/bin/bash
# create archive from current source using git
set -e

VERSION_TAG=$(git describe --tags --abbrev=0)
VERSION=${VERSION_TAG#v}
if ! git describe --tags --exact-match 2> /dev/null; then
    # devel version (not tagged)
    GIT_HASH=$(git rev-parse --short=6 HEAD)
    N_COMMITS=$(git rev-list $VERSION_TAG.. --count)
    # PEP 440 compatible dev version string
    VERSION="$VERSION.dev$N_COMMITS+$GIT_HASH"
fi

OUTPATH=pkg/archives/dev
NAMEVER=apkg-v$VERSION
ARCHIVE=$NAMEVER.tar.gz
ARPATH=$OUTPATH/$ARCHIVE

# ensure clean git because archive is created using `git archive` so
# uncommited changes won't be included and also make sure we
# don't accidentally add / overwrite forgotten changes in git
(git diff-index --quiet HEAD && git diff-index --cached --quiet HEAD) || \
    (echo "git index has uncommitted changes, can't commit version change :("; exit 1)

if [[ $VERSION = *"dev"* ]]; then
    # update devel version
    sed -i "s/\(__version__ *= *'\)[^']\+'/\1$VERSION'/" apkg/__init__.py
    git add apkg/__init__.py
    if git commit -a -m "DROP: update __version__ = $VERSION" > /dev/null; then
        # undo commit in the end
        cleanup() {
            git reset --hard HEAD^ >/dev/null
        }
        trap cleanup EXIT
    else
        echo "Failed to commit version changes :("
        git reset --hard >/dev/null
        exit 1
    fi
fi

mkdir -p "$OUTPATH"
git archive --format tgz --output $ARPATH --prefix $NAMEVER/ HEAD

# apkg expects stdout contains YAML dict with archive set
echo "archive: '$ARPATH'"
