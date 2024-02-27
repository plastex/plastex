#!/usr/bin/env python3

import os, sys
import importlib, pkgutil
import traceback, pdb
import plasTeX
from plasTeX import __version__
from argparse import ArgumentParser
from plasTeX.Logging import getLogger
from plasTeX.Compile import run
from plasTeX.Config import defaultConfig

log = getLogger()

def list_installed_plastex_plugins():
    knownPlugins = []
    for aFinder, name, _ in pkgutil.iter_modules():
        if name.startswith('plastex_') and name.endswith('_plugin'):
            knownPlugins.append(name)
    return knownPlugins

def collect_plastex_renderer_plugins_config(config):
    for _, name, _ in pkgutil.walk_packages():
        if name.startswith('plastex_') and '_plugin' in name  and name.endswith('Config'):
            try:
                conf = importlib.import_module(name)
            except ImportError:
                #print(f"Loading Renderers Options from {name}: "+traceback.format_exc(limit=-1))
                continue

            if hasattr(conf, 'addConfig') and callable(getattr(conf, 'addConfig')):
                #print(f"loading Renderers Options from: {name}")
                try:
                    conf.addConfig(config)
                except Exception:
                    print(traceback.format_exc(limit=-1))

def collect_renderer_config(config):
    plastex_dir = os.path.dirname(os.path.realpath(plasTeX.__file__))
    renderers_dir = os.path.join(plastex_dir, 'Renderers')
    renderers = next(os.walk(renderers_dir))[1]
    for renderer in renderers:
        try:
            conf = importlib.import_module('plasTeX.Renderers.'+renderer+'.Config')
        except ImportError as msg:
            continue

        conf.addConfig(config)

def main(argv):
    """ Main program routine """
    print('plasTeX version %s' % __version__)

    config = defaultConfig()
    collect_renderer_config(config)
    collect_plastex_renderer_plugins_config(config)

    parser = ArgumentParser("plasTeX")

    group = parser.add_argument_group("External Configuration Files")
    group.add_argument("--config", "-c", dest="config", help="Config files to load. Non-existent files are silently ignored", action="append")

    config.registerArgparse(parser)

    parser.add_argument("file", help="File to process")

    data = parser.parse_args(argv)
    data = vars(data)
    if data["config"] is not None:
        config.read(data["config"])

    if data['add-plugins'] :
        knownPlugins = list_installed_plastex_plugins()
        if not data['plugins']:
            data['plugins'] = [knownPlugins]
        else:
            # NOTE: not sure why the extra `[0]` is needed...
            # but it seems that the argparse data places lists inside a list.
            data['plugins'][0].extend(knownPlugins)

    config.updateFromDict(data)

    filename = data["file"]

    run(filename, config)

def info(type, value, tb):
   if hasattr(sys, 'ps1') or not sys.stderr.isatty():
      # we are in interactive mode or we don't have a tty-like
      # device, so we call the default hook
      sys.__excepthook__(type, value, tb)
   else:
      # we are NOT in interactive mode, print the exception...
      traceback.print_exception(type, value, tb)
      print()
      # ...then start the debugger in post-mortem mode.
      pdb.pm()

#sys.excepthook = info

#sys.setrecursionlimit(10000)

def plastex():
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
