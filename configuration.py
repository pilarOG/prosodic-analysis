# -*- coding: utf-8 -*-
#!/usr/bin/env python2
# Based on https://github.com/oliverwatts/ophelia

import imp
import os
import inspect

DEFAULTS = [
    ('analyse_f0', True),
    ('analyse_int', True),
    ('analyse_dur', True),
    ('analyse_rate', True),
    ('analyse_voc', True),
    ('analyse_pau', True),
    ('stats_sample', ''),
    ('stats_corpora', ''),
    ('use_gender', ''),
    ('use_align', '')
    ]

class Config(object):
    def __init__(self, module_object):
        for (key, value) in module_object.__dict__.items():
            if key.startswith('_'):
                continue
            if inspect.ismodule(value): # e.g. from os imported at top of config
                continue
            setattr(self, key, module_object.__dict__[key])
    def validate(self):
        for (varname, default_value) in DEFAULTS:
            if not hasattr(self, varname):
                setattr(self, varname, default_value)

def load_config(config_fname):
    config = os.path.abspath(config_fname)
    assert os.path.isfile(config), 'Config file %s does not exist'%(config)
    config_file = imp.load_source('config', config)
    settings = Config(config_file)
    settings.validate()
    return settings
