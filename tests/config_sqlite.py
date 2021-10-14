import os
import random


if random.random() > 0.5:
    try:
        os.remove('/tmp/ab.db')
    except:
        pass

# use default sqlite db
DB = 'sqlite:////tmp/ab.db'

# PRINT_SQL = True
