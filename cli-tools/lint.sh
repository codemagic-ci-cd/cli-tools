#!/usr/bin/env bash

export MYPYPATH=`pwd`/stubs/
mypy $@
