#!/usr/bin/env bash

blur=$(shuf -i 1-3 -n 1)
white=$(shuf -i 44-48 -n 1)
size="900x100"
echo "convert -size ${size} xc:white +noise random -blur 0x${blur} -white-threshold ${white}% -gravity center result_${blur}_${white}.png"
convert -size ${size} xc:white +noise random -blur 0x${blur} -white-threshold ${white}% -gravity center result_${blur}_${white}.png
