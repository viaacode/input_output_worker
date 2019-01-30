# -*- coding: utf-8 -*-

#!/var/www/localhost/htdocs/app/venv/bin/python
import sys

import os
#
#ALLDIRS = ['/home/tina/VIAA/Scripts/venv/lib/python3.4/site-packages/']
#
#import site
#
## Remember original sys.path.
#prev_sys_path = list(sys.path)
#
## Add each new site-packages directory.
#for directory in ALLDIRS:
#  site.addsitedir(directory)
#
## Reorder sys.path so new directories at the front.
#new_sys_path = []
#for item in list(sys.path):
#    if item not in prev_sys_path:
#        new_sys_path.append(item)
#        sys.path.remove(item)
#sys.path[:0] = new_sys_path
#print(sys.path)
#


#sys.path.insert(0, "/home/tina/spyder/viaa_workers")
#activate_this = '/home/tina/VIAA/Scripts/venv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))
#    sys.path.insert(0, "/home/tina/spyder/viaa_workers/")
#uwsgi --manage-script-name --mount /=workbench uwsgi_local.ini  

from inputOutputApi import APP 
#from apy_gateway import api




