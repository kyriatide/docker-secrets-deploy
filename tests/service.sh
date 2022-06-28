#!/bin/bash
#

for i in {1..5}; do
        printf "$i\n"
        sleep 0.5
done

for i in {6..10}; do
        printf "$i"
        [[ $i -lt 10 ]] && printf " "
        sleep 0.5
done
printf "\n"

