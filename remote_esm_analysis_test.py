#!/usr/bin/env python3
from fabric import Connection

c = Connection(host="ollie0.awi.de", user="pgierz")
c.run("echo $PATH")
c.run("which esm_analysis")
c.run("module load cdo && which cdo")
