#!/usr/bin/env bash

username='eddo888'
hostname='haversine.com'
password=$(squirrel.py get "${username}@${hostname}")

declare -a arguments
arguments=($*)

haversine.py ${arguments[0]} -u "${username}" -p "${password}" ${arguments[@]:1}

