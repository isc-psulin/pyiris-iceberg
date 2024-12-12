import glob
import os
import iris
import pandas as pd
from sqlalchemy import create_engine
from iris import ipm
import json

from time import sleep

# switch namespace to the %SYS namespace
iris.system.Process.SetNamespace("%SYS")

# set credentials to not expire
iris.cls('Security.Users').UnExpireUserPasswords("*")

# switch namespace to IRISAPP built by merge.cpf
iris.system.Process.SetNamespace("IRISAPP")

# load ipm package listed in module.xml
#iris.cls('%ZPM.PackageManager').Shell("load /home/irisowner/dev -v")
print("Starting load of IPM")
assert ipm('load /home/irisowner/dev -v')
print("Completed load of IPM")

# Loading of data usually done here but this started failing when running in IPM
# So now it is a manual install step


