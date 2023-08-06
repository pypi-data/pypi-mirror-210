#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : constants.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson Ignacio da Silva (aignacio) <anderson@aignacio.com>
# Date              : 06.02.2023
# Last Modified Date: 26.05.2023
import logging
import os
import abc
from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader

class options:
    TYPES               = ['soc', 'mpsoc']
    sch_cfg             = os.path.join(os.path.dirname(__file__),'schemas/schema_config.yaml')
    sch_master          = os.path.join(os.path.dirname(__file__),'schemas/schema_master.yaml')
    sch_slave           = os.path.join(os.path.dirname(__file__),'schemas/schema_slave.yaml')
    tmpl_folder         = os.path.join(os.path.dirname(__file__),'templates')
    tmpl_axi4_cross_bar = 'axi4_crossbar.txt'
    tmpl_nox            = 'nox_wrapper.txt'
    tmpl_vex            = 'vex_wrapper.txt'
    tmpl_axi4_mem_ram   = 'axi4_mem_ram.txt'
    tmpl_axi4_mem_rom   = 'axi4_mem_rom.txt'
    tmpl_axi4_dma       = 'axi4_dma.txt'
    tmpl_axi4_uart      = 'axi4_uart.txt'
    tmpl_axi4_irq       = 'axi4_irq_ctrl.txt'
    tmpl_axi4_timer     = 'axi4_timer.txt'
    tmpl_axi4_custom_s  = 'axi4_custom_slave.txt'
    tmpl_axi4_custom_m  = 'axi4_custom_master.txt'
    tmpl_axi4_rst_ctrl  = 'axi4_rst_ctrl.txt'
    tmpl_axi4_ethernet  = 'axi4_ethernet.txt'
    tmpl_clk_pll_xlnx   = 'clk_pll_xilinx.txt'
    tmpl_clk            = 'clk_simple.txt'
    tmpl_rst            = 'rst_simple.txt'
    tmpl_module_header  = 'module_header.txt'
    tmpl_ravenoc        = 'ravenoc.txt'
    tmpl_module_inst    = 'module_instance.txt'
    tmpl_defines        = 'module_defines.txt'

    acc_addr_width              = {}
    acc_addr_width['acc_uart']  = 13
    acc_addr_width['acc_timer'] = 13
    acc_addr_width['acc_dma']   = 13
    acc_addr_width['acc_irq']   = 13
    acc_addr_width['acc_rst']   = 13
    acc_addr_width['acc_noc']   = 15
    acc_addr_width['acc_eth']   = 12
    allowed_size_kib_acc        = ('ram_mem', 'rom_mem', 'acc_custom_slave')

class CustomFormatter(logging.Formatter):
    white = "\x1b[97;20m"
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s - {}%(levelname)-8s{} - %(name)s.%(funcName)s - %(message)s"

    FORMATS = {
        logging.DEBUG: fmt.format(grey, reset),
        logging.INFO: fmt.format(green, reset),
        logging.WARNING: fmt.format(yellow, reset),
        logging.ERROR: fmt.format(red, reset),
        logging.CRITICAL: fmt.format(bold_red, reset),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class base_module:
    def __init__(self, name, clk, rst, tmpl):
        self.name      = name
        self.clk       = clk
        self.rst       = rst
        self.tmpl      = tmpl
        self.signals   = []
        self.io        = {}
        self.io['in']  = []
        self.io['out'] = []
        self.acc_type  = None

    def get_acc_type(self):
        return self.acc_type

    def get_io(self):
        return self.io

    def get_signals(self):
        return self.signals

    def get_params(self):
        params = []
        for attr_name, attr_value in self.__dict__.items():
            params.append([attr_name, attr_value])
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            print(tabulate(params, tablefmt="double_outline"))

    def get_hdl(self):
        file_loader = FileSystemLoader(options.tmpl_folder)
        env = Environment(loader=file_loader)
        template = env.get_template(self.tmpl)
        output = template.render(tmpl=self)
        # if logging.getLogger().isEnabledFor(logging.DEBUG):
            # print(output)
        return output
