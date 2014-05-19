#!/bin/sh

USAGE="Usage: `basename $0` [-hv] <trace>"

# Parse command line options.
while getopts hv: OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        v)
            echo "`basename $0` version 0.1"
            exit 0
            ;;
        \?)
            # getopts issues an error message
            echo $USAGE >&2
            exit 1
            ;;
    esac
done

# Remove the options we parsed above.
shift `expr $OPTIND - 1`

if [ $# -eq 0 ]; then
    echo $USAGE >&2
    exit 1
fi

echo "Starting fsReplay for $@..."
./fsReplay/fsReplay $@
