#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : ipsocgen_cli.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson Ignacio da Silva (aignacio) <anderson@aignacio.com>
# Date              : 06.02.2023
# Last Modified Date: 08.04.2023
import logging
import argparse
import pathlib
import sys
import yaml
import pkg_resources
try: # When released as a package
    from ipsocgen.common.constants import options, CustomFormatter
    from ipsocgen.common.validate import validate_config
    from ipsocgen.common.modules import *
    from ipsocgen.common.generate import *
    from ipsocgen.common.version import __IPSOCGEN_VERSION__
except ImportError: # While in development
    from common.constants import options, CustomFormatter
    from common.validate import validate_config
    from common.modules import *
    from common.generate import *
    from common.version import __IPSOCGEN_VERSION__

def _gen(cfg, output, mmap):
    if cfg['type'] == 'soc':
        soc_gen(cfg['soc_desc'], cfg['proj_name'], cfg['desc'], output, mmap)
    else:
        mpsoc_gen(cfg['mpsoc_desc'], cfg['proj_name'], cfg['desc'], output, mmap)

    return True

def main():
    version = __IPSOCGEN_VERSION__
    parser = argparse.ArgumentParser(description='IP SoC Generator CLI v'+version)

    parser.add_argument('-c','--cfg',
                        nargs='?',
                        type=argparse.FileType('r'),
                        help='YAML file with the configuration of the MP/SoC')

    parser.add_argument('-o','--output',
                        nargs='?',
                        type=pathlib.Path,
                        help='Output directory of the generated design',
                        default='./output')

    parser.add_argument('-v','--validate',
                        action='store_true',
                        help='Validate only configuration file')

    parser.add_argument('-d','--debug',
                        action='store_true',
                        help='Enable debug mode')

    parser.add_argument('-m','--mmap',
                        action='store_true',
                        help='Print memory map of each SoC')


    in_args = {}
    in_args['config']   = parser.parse_args().cfg
    in_args['output']   = parser.parse_args().output
    in_args['validate'] = parser.parse_args().validate
    in_args['debug']    = parser.parse_args().debug
    in_args['mmap']     = parser.parse_args().mmap

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=logging.DEBUG if in_args['debug'] == True else logging.INFO,
                        handlers=[handler])
    # print(in_args)
    if in_args['config'] == None:
            logging.warning("No valid configuration was specified, exiting now...")
            sys.exit(0)
    else:
        status, cfg = validate_config(in_args)
        if status == False:
            logging.error('Aborting generation...')
            sys.exit(1)
        else:
            if in_args['validate'] == True:
                logging.info('Validate only enabled, exiting now...')
                sys.exit(0)
            _gen(cfg, in_args['output'], in_args['mmap'])

if __name__ == '__main__':
    main()
