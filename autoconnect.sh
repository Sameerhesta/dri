#!/bin/bash

bluetoothctl << EOF
power on
agent on
default-agent
pairable on
discoverable on
agent NoInputNoOutput
exit
EOF
agent 
