#!/bin/bash

# taken from Proj3

for t in tests/*.py
do
    nosetests $t
done

