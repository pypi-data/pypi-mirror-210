#!/usr/bin/env fish
# -*- coding: utf-8 -*-

function useChangeDetector
    # Get the current time
    set now (date +"%s")
    set end ".chg.dtctr"
    # Use changedetector module
    echo "from changedetector import detectchange" > __temp$now$end.py
    echo "print(detectchange.activate(True))" >> __temp$now$end.py
    if [ "$argv[1]" = "Linux" ]
        python3 __temp$now$end.py
    else if [ "$argv[1]" = "Darwin" ]
        python3 __temp$now$end.py
    else if [ "$argv[1]" = "Windows" ]
        py __temp$now$end.py
    end
    # if the python script exits with a 1 error, remove the temp.py file
    if [ $status -eq 1 ]
        if [ "$argv[1]" = "Linux" ]
            rm __temp$now$end.py
        else if [ "$argv[1]" = "Darwin" ]
            rm __temp$now$end.py
        else if [ "$argv[1]" = "Windows" ]
            del __temp$now$end.py
        end
    end
end

# Check for the OS
if [ (uname) = "Darwin" ]
    # Mac OS X platform
    echo "Mac OS X"
    # Use changedetector module
    useChangeDetector "Darwin"
else if [ (expr substr (uname -s) 1 5) = "Linux" ]
    # GNU/Linux platform
    echo "Linux"
    # Use changedetector module
    useChangeDetector "Linux"
else if [ (expr substr (uname -s) 1 10) = "MINGW32_NT" ]
    # 32 bits Windows NT platform
    echo "32 bits Windows NT"
    # Use changedetector module
    useChangeDetector "Windows"
else if [ (expr substr (uname -s) 1 10) = "MINGW64_NT" ]
    # 64 bits Windows NT platform
    echo "64 bits Windows NT"
    # Use changedetector module
    useChangeDetector "Windows"
end
