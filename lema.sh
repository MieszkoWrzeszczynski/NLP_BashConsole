#!/bin/bash
echo  $1 | tok | lem | grep -oh "lem:\w*" | head -1 | cut -c 5-