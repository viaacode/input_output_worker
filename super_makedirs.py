#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 10:26:11 2017
Creates dir structure with permissions of underlaying dir
@author: tina

make_dir().supermakedirs('/tmp/9/8/9/985/8')

"""
import os
import logging

logger = logging.getLogger(__name__)
LOG_FORMAT = ('%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

class make_dir(object):
    def __init__(self):
  
        self.file_permission = 0o770

    def supermakedirs(self, path):
            try:
                if not path or os.path.exists(path):
                    stat_info = os.stat(path)
                    uid = stat_info.st_uid
                    gid = stat_info.st_gid
                    self.user = uid
                    self.group = gid
                    logging.info('Found: {} - {} - {}'.format(self.user, self.group, path))
                    # Break recursion
                    return []
                (head, tail) = os.path.split(path)
                res = self.supermakedirs(head)
                try :
                    os.mkdir(path)
                    os.chmod(path, self.file_permission)
                    os.chown(path, self.user, self.group)
                    logging.info('Created: {} - {} - {}'.format(self.user, self.group, path))
                    res += [path]
                # Falback to running user
                except PermissionError:
                    self.user = os.getegid()
                    self.group = os.getegid()
                    os.mkdir(path)
                    os.chmod(path, self.file_permission)
                    os.chown(path, self.user, self.group)
                    logging.info('Created: {} - {} - {}'.format(self.user, self.group, path))
                    res += [path]
                return res
            except OSError as e:
                if e.errno == 17:
                    logging.info('Directory existed when creating. Ignoring')
                    res += [path]
                    return res
                raise
