#!/bin/bash

output=`wmctrl -l | grep -c Zulip`
echo $output
if [ $output > 0 ]
then
    wmctrl -a zulip
fi
