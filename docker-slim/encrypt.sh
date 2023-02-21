#!/bin/bash
set -x

check_result()
{
  echo input params:$1
  if [ $1 != 0 ]; then
     exit $1
  fi
}

# read info
if test -f ./.ab ; then
  . ./.ab
  check_result $?

  if [ "$enable_encrypt_python" = "true" ]; then
    if [ -n "$encrypt_python_include" ]; then
      printf -v joined '%s,' "${encrypt_python_exclude[@]}"
      printf -v injoined '%s,' "${encrypt_python_include[@]}"
      abt encrypt -i "${injoined%,}" -e "${joined%,}" -c true
    else
      echo "encrypt info is NULL, you don't need to encrypt. "
    fi
  fi
fi
