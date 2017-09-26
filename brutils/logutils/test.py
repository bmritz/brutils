import sys
from git import Repo
import os

repo_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

print repo_dir

x = Repo(repo_dir)



print x

