#!/bin/bash
set -x

check_result()
{
  echo input params:$1
  if [ $1 != 0 ]; then
     exit $1
  fi
}

# read crypto info
if test -f ./.ab ; then
  . ./.ab
  check_result $?

  if [ "$enable_crypto" = "true" ]; then
    if [ -n "$crypto" ]; then
      for value in "${crypto[@]}";
        do
          abt crypto -i "${value}" -c true
          check_result $?
      done
    else
      echo "crypto info is NULL, you don't need to crypto. "
    fi
  else
    # remove algorithm/__init__.py
    # echo "" > /root/app/algorithms/__init__.py
    echo "todo"
  fi
fi
