#!/bin/sh


  printf "Issues > "
  read ISSUES
  SOURCE=${2}

  IN=$(<$1)
  set -- "$IN"
  IFS=";"; declare -a foo=($*) 

  for student in "${foo[@]}"
    do
      echo "python gh-issues-import.py --source ${SOURCE} --target ${student}/${student}.github.io --issues ${ISSUES}"
      python gh-issues-import.py --source ${SOURCE} --target ${student}/${student}.github.io --issues ${ISSUES}
    done
