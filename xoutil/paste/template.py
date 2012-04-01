#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.paste.template
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# Author: Manuel Vázquez Acosta <mva.led@gmail.com>
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 2012-04-01

"A very simple template structure for Merchise packages"

from __future__ import (division as _py3_division,
                        print_function as _py3_print)

__docstring_format__ = 'rst'
__version__ = '0.1.0'
__author__ = 'Manuel Vázquez Acosta <mva.led@gmail.com>'


from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer

from functools import partial


class MerchisePackageTemplate(Template):
    _template_dir = 'templates/merchise_package'
    summary = "Un paquete sencillo para Merchise"

    vars = [
        var('version', 'Version (like 0.1.0)', default='0.1.0'),
        var('description', 'One-line description of the package'),
        var('keywords', 'Space-separated keywords/tags'),
    ]

    @staticmethod
    def stringify_entry_points(vars, eps=None, pad=' '*8):
        eps = vars.get('entry_points', {}) if not eps else eps
        result = ''
        for group, group_eps in eps.items():
            result += '{pad}[{group}]\n'.format(pad=pad, group=group)
            for ep_name, ep_ref in group_eps.items():
                result += '{pad}{name} = {ref}\n'.format(pad=pad,
                                                         name=ep_name,
                                                         ref=ep_ref)
        return result

    @staticmethod
    def get_basename(filename):
        import os
        basename = os.path.basename(filename)
        if basename.endswith('_tmpl'):
            basename = basename[:-5]
        if basename.endswith('.py'):
            basename = basename[:-3]
        return basename

    @staticmethod
    def get_module_name(project, filename):
        basename = MerchisePackageTemplate.get_basename(filename)
        t = '{project}.{basename}' if project else '{basename}'
        return t.format(project=project, basename=basename)

    #~ template_renderer = staticmethod(paste_script_template_renderer)
    @staticmethod
    def template_renderer(contents, vars, filename=None):
        import datetime
        if filename:
            project = vars.get('project', None)
            module = MerchisePackageTemplate.get_module_name(project, filename)
            vars.setdefault('module', module)
            vars.setdefault('filename',
                            MerchisePackageTemplate.get_basename(filename))
        else:
            vars.setdefault('module', 'unknown')
        now = datetime.datetime.now()
        vars.setdefault('date', now.date())
        vars.setdefault('now', now)
        vars.setdefault('datetime', now)
        vars.setdefault('entry_points', {})
        vars.setdefault('stringify_entry_points',
                        partial(MerchisePackageTemplate.stringify_entry_points,
                                vars))
        return paste_script_template_renderer(contents, vars, filename)