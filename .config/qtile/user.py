#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sh
import subprocess
from shlex import split
from io import StringIO

from libqtile import hook
from rescuetime import allDistractingTime, productivityPulse


def getOutput(command, empty=''):
    # print(f'Running command {command}')
    out = subprocess.check_output(command, shell=True)
    # print(f"Got output '{out}'")
    if out.decode().strip() == empty:
        return ''
    return out.decode().strip()


def fuzClock():
    return getOutput('fuzClock')


def usedMem():
    return getOutput(''' free -h | awk '/Mem/{print $3}' ''')


def inbox():
    inbox = int(getOutput('''wunderline list inbox | wc -l''')) - 2
    if inbox >= 1:
        return 'Inbox: ' + str(inbox)
    else:
        return ''


def pacmanUpdates():
    s = getOutput(
        ''' pacman -Sy &>/dev/null ; pacman -Qu | wc -l ''', empty='0')
    if s == '' or int(s) <= 5:
        return ''
    else:
        return 'Updates: ' + s


@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.call([home])


# thanks to rogerduran for the implementation of my idea (borrowed
# from stumpwm)


class PrevFocus(object):
    """Store last focus per group and go back when called"""

    def __init__(self):
        self.groups_focus = {}
        hook.subscribe.client_focus(self.on_focus)

    def on_focus(self, window):
        group = window.group
        # only store focus if the group is set
        if not group:
            return
        group_focus = self.groups_focus.setdefault(group.name, {
            "current": None,
            "prev": None
        })
        # don't change prev if the current focus is the same as before
        if group_focus["current"] == window:
            return
        group_focus["prev"] = group_focus["current"]
        group_focus["current"] = window

    def __call__(self, qtile):
        group = qtile.currentGroup
        group_focus = self.groups_focus.get(group.name, {"prev": None})
        prev = group_focus["prev"]
        try:
            if prev and group.name == prev.group.name:
                group.focus(prev, False)
        except:
            pass
