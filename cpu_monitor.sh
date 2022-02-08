#!/bin/bash

pids=$(ps --no-header -eo pcpu,pid,user,args | sort -k 1 -r | head -40 |awk '{print $2}'|tr '\n' ','|sed 's/,$//')
echo "$pids"

ps --no-header -ww -o pid,pcpu,pmem,etimes,comm -p "$pids"

countdown()
(
  IFS=:
  set -- "$*"
 
  secs=$( "${1#0}" '*' 3600 + "${2#0}" '*' 60 + "${3#0}" )

  while [ "$secs" -gt 0 ]
  do
    sleep 1 &
    printf "\r%02d:%02d:%02d" $((secs/3600)) $(( (secs/60)%60)) $((secs%60))
    secs=$(( "$secs" - 1 ))
    wait
  done
  echo
)

