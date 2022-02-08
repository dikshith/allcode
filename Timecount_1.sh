#!/bin/bash

m=${1}-1 # add minus 1 

Floor () {
  DIVIDEND=${1}
  DIVISOR=${2}
  RESULT=$(( ( ${DIVIDEND} - ( ${DIVIDEND} % ${DIVISOR}) )/${DIVISOR} ))
  echo ${RESULT}
}

Timecount(){
        s=${1}
        HOUR=$( Floor ${s} 60/60 )
        s=$((${s}-(60*60*${HOUR})))
        MIN=$( Floor ${s} 60 )
        SEC=$((${s}-60*${MIN}))
     while [ $HOUR -ge 0 ]; do
        while [ $MIN -ge 0 ]; do
                while [ $SEC -ge 0 ]; do
                        printf "Cuntdown Tims is : %02d:%02d:%02d\033[0K\r\n" $HOUR $MIN $SEC
                        CpuAndMem
                        SEC=$((SEC-5sssssssss))
                        sleep 5
                done
                SEC=59
                MIN=$((MIN-1))
        done
        MIN=59
        HOUR=$((HOUR-1))
     done
}

CpuAndMem(){

   pids=$(ps --no-header -eo pcpu,pid,user,args | sort -k 1 -r | head -40 |awk '{print $2}'|tr '\n' ','|sed 's/,$//')
   echo "$pids"
   ps --no-header -ww -o pid,pcpu,pmem,etimes,comm -p "$pids" >> result.txt 


}

Timecount $m