#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Walter Bender <walter@sugarlabs.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging

import os
import glob
import json

from gettext import gettext as _

from sugar import env
from sugar import profile

DIROFINTEREST = 'datastore'


class ParseJournal():
    ''' Simple parser of datastore '''

    def __init__(self):
        self._dsdict = {}
        self._activity_name = []
        self._activity_launch_times = []
        homepath = os.environ['HOME']

        for path in glob.glob(os.path.join(homepath, '.sugar', '*')):
            if isdsdir(path):
                self._dsdict[os.path.basename(path)] = []
                dsobjdirs = glob.glob(
                    os.path.join(path, DIROFINTEREST, '??'))
                for dsobjdir in dsobjdirs:
                    dsobjs = glob.glob(os.path.join(dsobjdir, '*'))
                    for dsobj in dsobjs:
                        self._dsdict[os.path.basename(path)].append({})
                        activity = isactivity(dsobj)
                        launch = launch_times(dsobj)
                        if not activity:
                            self._dsdict[os.path.basename(path)][-1][
                                'activity'] = 'media object'
                        else:
                            self._dsdict[os.path.basename(path)][-1][
                                'activity'] = activity
                        self._dsdict[os.path.basename(path)][-1][
                            'launch'] = launch

        for k, v in self._dsdict.iteritems():
            for a in v:
                if 'activity' in a:
                    if a['activity'] in self._activity_name:
                        i = self._activity_name.index(a['activity'])
                        if 'launch' in a:
                            self._activity_launch_times[i] += ', '
                            self._activity_launch_times[i] +=  a['launch']
                    else:
                        self._activity_name.append(a['activity'])
                        if 'launch' in a:
                            self._activity_launch_times.append(a['launch'])
                        else:
                            self._activity_launch_times.append('0')

    def get_sorted(self):
        activity_tuples = []
        for i in range(len(self._activity_name)):
            launch_times = self._activity_launch_times[i].split(', ')
            sorted_launch_times = sorted(launch_times, key=lambda x: int(x))
            activity_tuples.append((self._activity_name[i].replace('Activity',
                                                                   ''),
                                    sorted_launch_times))
        sorted_tuples = sorted(activity_tuples, key=lambda x: len(x[1]))
        activity_list = []
        count = 0
        length = len(sorted_tuples)
        for i in range(length):
            activity_list.append([sorted_tuples[length - i - 1][0],
                                  sorted_tuples[length - i - 1][1]])
        return activity_list


def hascomponent(path, component):
    ''' Return metadata attribute, if any '''
    if not os.path.exists(os.path.join(path, 'metadata')):
        return False
    if not os.path.exists(os.path.join(path, 'metadata', component)):
        return False
    fd = open(os.path.join(path, 'metadata', component))
    data = fd.readline()
    fd.close()
    if len(data) == 0:
        return False
    return data


def launch_times(path):
    ''' Return activity launch times '''
    launchtimes = hascomponent(path, 'launch-times')
    if not launchtimes:
        return '0'
    else:
        return launchtimes


def isactivity(path):
    ''' Return activity name '''
    activity = hascomponent(path, 'activity')
    if not activity:
        return False
    else:
        return activity.split('.')[-1]


def isdsdir(path):
    ''' Only interested if it is a datastore directory '''
    if not os.path.isdir(path):
        return False
    if not os.path.exists(os.path.join(path, DIROFINTEREST)):
        return False
    return True


class JournalReader():
    """Reader for Journal activity

    Import chart data from journal activity analysis
    """

    def __init__(self, mypath=None):
        if mypath is None:
            mypath = os.path.join(os.path.abspath('.'), 'journalstats')

        stats = ParseJournal().get_sorted()
        f = open(mypath, 'w')
        try:
            json.dump(stats, f)
        finally:
            f.close()


if __name__ == '__main__':
    JournalReader()
