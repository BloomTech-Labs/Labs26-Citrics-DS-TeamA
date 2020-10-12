import sys
import os

sys.path.append(os.path.join(os.getcwd(), "development"))

for line in sys.path:
    print(line)

from utilities.database import PostgreSQL