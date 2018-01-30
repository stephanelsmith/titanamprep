#!/usr/bin/tcsh

ps auxww | grep 'titanamp' | awk '{print $2}' | xargs kill -9
ps auxww | grep 'titanamp' | grep -v 'supervisor' | awk '{print $2}' | xargs kill -9
