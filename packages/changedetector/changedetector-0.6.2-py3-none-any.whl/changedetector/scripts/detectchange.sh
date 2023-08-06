#!/usr/bin/env bash

function useChangeDetector () {
    # Get the current time
    now=$(date +"%s")
    end=".chg.dtctr"
    # Use changedetector module
    echo "from changedetector import detectchange" > __temp$now$end.py
    echo "print(detectchange.activate(True))" >> __temp$now$end.py
    if [ "$1" == "Linux" ]; then
        python3 __temp$now$end.py
    elif [ "$1" == "Darwin" ]; then
        python3 __temp$now$end.py
    elif [ "$1" == "Windows" ]; then
        py __temp$now$end.py
    fi
    # if the python script exits with a 1 error, remove the temp.py file
    if [ $? -eq 1 ]; then
        if [ "$1" == "Linux" ]; then
            rm __temp$now$end.py
        elif [ "$1" == "Darwin" ]; then
            rm __temp$now$end.py
        elif [ "$1" == "Windows" ]; then
            del __temp$now$end.py
        fi
    fi
}

# Check for the OS
if [ "$(uname)" == "Darwin" ]; then
    # Mac OS X platform
    echo "Mac OS X"
    # Use changedetector module
    useChangeDetector "Darwin"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # GNU/Linux platform
    echo "Linux"
    # Use changedetector module
    useChangeDetector "Linux"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    # 32 bits Windows NT platform
    echo "32 bits Windows NT"
    # Use changedetector module
    useChangeDetector "Windows"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # 64 bits Windows NT platform
    echo "64 bits Windows NT"
    # Use changedetector module
    useChangeDetector "Windows"
fi
