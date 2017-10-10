#!/bin/sh

printf "Issues > "
read ISSUES

IN=$(<$1)
set -- "$IN" 
IFS=";"; declare -a foo=($*) 

for student in "${foo[@]}"
  do
    echo "python gh-issues-import.py --source stevebrownlee/personal-site --target ${student}/${student}.github.io --issues ${ISSUES}"
    python gh-issues-import.py --source stevebrownlee/personal-site --target ${student}/${student}.github.io --issues ${ISSUES}
  done


