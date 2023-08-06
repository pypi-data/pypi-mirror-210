#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : modules.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson Ignacio da Silva (aignacio) <anderson@aignacio.com>
# Date              : 06.02.2023
# Last Modified Date: 26.05.2023
import logging
import os
import sys
from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
try:
    from ipsocgen.common.constants import options,base_module
    from ipsocgen.common.modules import *
except ImportError:
    from common.constants import options,base_module

class Axi4Bus(base_module):
    def __init__(self, cfg, mmap):
        super().__init__(cfg['bus_name'], 0, 0, options.tmpl_axi4_cross_bar)
        self.b_addr_width  = cfg['addr_width']
        self.b_data_width  = cfg['data_width']
        self.num_masters   = cfg['num_masters']
        self.num_slaves    = cfg['num_slaves']
        self.mmap_type     = cfg['mmap_type']
        self.txn_id_width  = cfg['txn_id_width']
        self.bus_name      = cfg['bus_name']
        slaves_dict        = cfg['slaves']

        curr_addr        = 0x00
        self.base_addr   = {}
        self.base_addr_h = {}
        self.end_addr    = {}
        self.addr_width  = {}
        self.description = {}
        self.type        = {}
        self.mem_size    = {}
        self.clk         = cfg['clk']['clk_int']
        self.rst         = cfg['rst']['rst_int']
        self.desc        = "AXI4 Crossbar"
        self.noc_addr    = 0x00
        # self.tmpl        = options.tmpl_axi4

        logging.debug('Generating AXI4 Bus...')
        if self.mmap_type == 'auto':
            for slave in range(self.num_slaves):
                slave_type = slaves_dict[slave]['type']
                if slave_type in options.acc_addr_width:
                    self.addr_width[slave]  = options.acc_addr_width[slave_type]
                    self.base_addr[slave]   = self._get_base_addr(curr_addr,
                                                                  2**options.acc_addr_width[slave_type])
                    curr_addr = self.base_addr[slave] + (2**options.acc_addr_width[slave_type])
                else:
                    if slave_type not in options.allowed_size_kib_acc:
                        logging.error('Slave ' + str(slave) + ' - Unknown type for AXI4 bus gen')
                        sys.exit(1)
                    self.addr_width[slave]  = self._get_addr_width(slaves_dict[slave]['mem_size_kib'])
                    self.base_addr[slave]   = self._get_base_addr(curr_addr, 2**self.addr_width[slave])
                    curr_addr = self.base_addr[slave] + (2**self.addr_width[slave])
                self.description[slave] = slaves_dict[slave]['desc']
                self.type[slave]        = slaves_dict[slave]['type']
                self.mem_size[slave]    = (2**self.addr_width[slave])//1024
                if (self.type[slave] == 'ram_mem') or (self.type[slave] == 'rom_mem'):
                    self.mem_size[slave] = slaves_dict[slave]['mem_size_kib']
                self.base_addr_h[slave] = hex(self.base_addr[slave])[2:]
                self.end_addr[slave]    = (self.base_addr[slave]+(2**self.addr_width[slave])-1)
                if slave_type == 'acc_noc':
                    self.noc_addr = self.base_addr_h[slave]
        else:
            for slave in range(self.num_slaves):
                base_addr_exist = 'base_addr' in slaves_dict[slave]
                addr_width_exist = 'addr_width' in slaves_dict[slave]

                if (base_addr_exist and addr_width_exist):
                    base_addr = slaves_dict[slave]['base_addr']
                    addr_width = slaves_dict[slave]['addr_width']

                    if (base_addr % (2**addr_width)) != 0:
                        logging.error('Slave base_addr=' + str(base_addr) + ' addr_width=' + str(addr_width))
                        logging.error('Slave ' + str(slave) + ' - base_addr%(2**addr_width) != 0')
                        sys.exit(1)
                    else:
                        self.addr_width[slave]  = slaves_dict[slave]['addr_width']
                        self.base_addr[slave]   = slaves_dict[slave]['base_addr']
                        self.end_addr[slave]    = (self.base_addr[slave]+(2**self.addr_width[slave])-1)
                        self.description[slave] = slaves_dict[slave]['desc']
                        self.base_addr_h[slave] = hex(self.base_addr[slave])[2:]
                        if slaves_dict[slave]['type'] == 'acc_noc':
                            self.noc_addr = self.base_addr_h[slave]
                        self.type[slave]        = slaves_dict[slave]['type']
                        self.mem_size[slave]    = (2**self.addr_width[slave])//1024
                        if (self.type[slave] == 'ram_mem') or (self.type[slave] == 'rom_mem'):
                            self.mem_size[slave] = slaves_dict[slave]['mem_size_kib']

                else:
                    logging.error('Slave ' + str(slave) + ' - Missing addr_width and/or base_addr')
                    sys.exit(1)

        # Creating print tables
        # -------------
        # SLAVES
        # -------------
        self.headers_slaves = ['Slave ID', 'Base Addr', 'End Addr', 'Size (KiB)',
                               'Description']
        self.table_slaves = []
        for slv in range(self.num_slaves):
            self.table_slaves.append([slv,
                               hex(self.base_addr[slv]),
                               hex(self.end_addr[slv]),
                               str((2**self.addr_width[slv])//1024),
                               self.description[slv]])
        self.table_slaves_c = [['// Slave ID', 'Base Addr', 'End Addr',
                                'Size (KiB)', 'Description']]
        for slv in range(self.num_slaves):
            self.table_slaves_c.append(['// '+str(slv),
                                 hex(self.base_addr[slv]),
                                 hex(self.end_addr[slv]),
                                 str((2**self.addr_width[slv])//1024),
                                 self.description[slv]])
        # -------------
        # MASTERS
        # -------------
        self.headers_masters = [' Master ID', 'Description']
        self.table_masters = []
        for mst in range(self.num_masters):
            self.table_masters.append([str(mst), cfg['masters'][mst]['desc']])

        self.table_masters_c = [['// Master ID', 'Description']]
        for mst in range(self.num_masters):
            self.table_masters_c.append(['// '+str(mst), cfg['masters'][mst]['desc']])

        if mmap:
            print(tabulate(self.table_masters, self.headers_masters, tablefmt="double_outline"))
            print(tabulate(self.table_slaves, self.headers_slaves, tablefmt="double_outline"))

    def get_noc_addr(self):
        return self.noc_addr

    def _get_base_addr(self, curr_addr, size):
        val = curr_addr
        if (val % size) == 0:
            return val
        else:
            while (val % size) != 0:
                val += 1
            return val

    def _get_addr_width(self, size_kib):
        val = 0
        while ((2**val) < (size_kib*1024)):
            val += 1
        return val

    def _is_power_of_2(self, n):
        return ((n & (n-1) == 0) and n != 0)

    def print_axi4_cfg(self):
        print(tabulate(self.table_slaves, self.headers_slaves, tablefmt="double_outline"))

    def get_hdl(self):
        file_loader = FileSystemLoader(options.tmpl_folder)
        env = Environment(loader=file_loader)
        template = env.get_template(options.tmpl_axi4_cross_bar)
        output = '\n'
        output +=  tabulate(self.table_masters_c, tablefmt="plain")
        output += '\n\n'
        output += tabulate(self.table_slaves_c, tablefmt="plain")
        output += template.render(axi4bus=self)
        # if logging.getLogger().isEnabledFor(logging.DEBUG):
            # print(output)
        return output

    def get_mmap(self):
        return self.base_addr

class RISCVCpu(base_module):
    def __init__(self, cfg, mmap, cpu_type):
        super().__init__(cfg['proc']['name'], cfg['proc']['clk']['clk_int'],
                         cfg['proc']['rst']['rst_int'], options.tmpl_nox if cpu_type == 'nox'
                                                                         else options.tmpl_vex)
        self.boot_addr  = self._get_boot_addr(cfg, mmap)
        self.irq_vector = self._get_irq_vec(cfg)
        self.mosi_instr = self._get_master_if(cfg, 'mosi', cpu_type+'_instr_bus')
        self.miso_instr = self._get_master_if(cfg, 'miso', cpu_type+'_instr_bus')
        self.mosi_lsu   = self._get_master_if(cfg, 'mosi', cpu_type+'_lsu_bus')
        self.miso_lsu   = self._get_master_if(cfg, 'miso', cpu_type+'_lsu_bus')
        self.signals.append('  logic [31:0] '+self.boot_addr+';')
        self.acc_type = 'cpu_nox' if cpu_type == 'nox' else 'cpu_vex'

    def _get_boot_addr(self, cfg, mmap):
        if cfg['proc']['boot']['type'] == 'value':
            return '\'h'+hex(cfg['proc']['boot']['value'])[2:]
        elif cfg['proc']['boot']['type'] == 'slave':
            slv = cfg['slaves']
            slv_id = cfg['proc']['boot']['slave']
            if slv[slv_id]['type'] == 'acc_rst':
                return 'rst_addr'
            else:
                return '\'h'+hex(mmap[cfg['proc']['boot']['slave']])[2:]
        else:
            return cfg['proc']['boot']['signal']

    def _get_irq_vec(self, cfg):
        tmr   = cfg['proc']['irq_mapping']['timer']
        tmr   = str(0) if tmr == 'zero' else tmr
        sw    = cfg['proc']['irq_mapping']['software']
        sw    = str(0) if sw == 'zero' else sw
        ext   = cfg['proc']['irq_mapping']['external']
        ext   = str(0) if ext == 'zero' else ext
        return '{'+tmr+','+sw+','+ext+'}'

    def _get_master_if(self, cfg, direction, type_if):
        for master, master_desc in cfg['masters'].items():
            if master_desc['type'] == 'cpu_nox' or master_desc['type'] == 'cpu_vex':
                if master_desc['if'] == type_if:
                    if direction == 'mosi':
                        return master
                    else:
                        return master
        logging.error('Missing CPU I/F '+type_if)
        sys.exit(1)

class Axi4MemRAM(base_module):
    def __init__(self, cfg, soc_common, slv_id):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_mem_ram)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.mem_size_kib = cfg['mem_size_kib']
        self.acc_type     = 'ram_mem'

class Axi4MemROM(base_module):
    def __init__(self, cfg, soc_common, slv_id):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_mem_rom)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.mem_size_kib = cfg['mem_size_kib']
        self.acc_type     = 'rom_mem'

class Axi4DMA(base_module):
    def __init__(self, cfg, soc_common, slv_id, mst_id):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_dma)
        self.txn_id_w      = soc_common['txn_id']
        self.slv_id        = slv_id
        self.desc          = cfg['desc']
        self.mst_id        = mst_id
        self.irq_dma_done  = cfg['irq_dma_done']
        self.irq_dma_error = cfg['irq_dma_error']
        self.signals.append('  logic '+self.irq_dma_done+';')
        self.signals.append('  logic '+self.irq_dma_error+';')
        self.acc_type     = 'acc_dma'

class Axi4UART(base_module):
    def __init__(self, cfg, soc_common, slv_id):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_uart)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.io_rx        = cfg['io_rx']
        self.io_tx        = cfg['io_tx']
        self.irq_uart_rx  = cfg['irq_uart_rx']
        self.signals.append('  logic '+self.irq_uart_rx+';')
        # self.signals.append('  logic '+self.io_tx+'; // IO Pin')
        # self.signals.append('  logic '+self.io_rx+'; // IO Pin')
        self.io['in'].append(['logic', cfg['io_rx']])
        self.io['out'].append(['logic', cfg['io_tx']])
        self.acc_type     = 'acc_uart'

class Axi4Irq(base_module):
    def __init__(self, cfg, soc_common, slv_id, base_addr):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_irq)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.irq_type     = '\'h'+hex(cfg['irq_type'])[2:]
        self.irq_summary  = cfg['irq_summary']
        self.vec_mapping  = cfg['vec_mapping']
        self.max_irq      = 0
        if len(self.vec_mapping) > 32:
            logging.error('Number of IRQs is bigger than supported (>32)')
        if len(self.vec_mapping) < 32:
            self.all_irq_filled = 0
            self.max_irq = len(self.vec_mapping)
        else:
            self.all_irq_filled = 1
        self.base_addr    = '\'h'+hex(base_addr[slv_id])[2:]
        self.signals.append('  logic '+self.irq_summary+';')
        self.acc_type     = 'acc_irq'

class Axi4Timer(base_module):
    def __init__(self, cfg, soc_common, slv_id, base_addr):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_timer)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.irq_timer    = cfg['irq_timer']
        self.base_addr    = '\'h'+hex(base_addr[slv_id])[2:]
        self.signals.append('  logic '+self.irq_timer+';')
        self.acc_type     = 'acc_timer'

class Axi4AccCustomSlave(base_module):
    def __init__(self, cfg, soc_common, slv_id, base_addr):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_custom_s)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = slv_id
        self.desc         = cfg['desc']
        self.base_addr    = '\'h'+hex(base_addr[slv_id])[2:]
        self.acc_type     = 'acc_custom_slave'

class Axi4AccCustomMaster(base_module):
    def __init__(self, cfg, soc_common, mst_id):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_custom_m)
        self.txn_id_w     = soc_common['txn_id']
        self.slv_id       = mst_id
        self.desc         = cfg['desc']
        self.acc_type     = 'acc_custom_master'

class Axi4RstCtrl(base_module):
    def __init__(self, cfg, soc_common, slv_id, base_addr):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_rst_ctrl)
        self.txn_id_w        = soc_common['txn_id']
        self.slv_id          = slv_id
        self.desc            = cfg['desc']
        self.base_addr       = '\'h'+hex(base_addr[slv_id])[2:]
        self.rst_def_addr    = '\'h'+hex(base_addr[cfg['rst_def_addr']])[2:]
        self.rst_pulse_width = cfg['rst_pulse_width']
        self.rst_addr_out    = cfg['rst_addr_out']
        self.bootloader_type = cfg['bootloader_type']
        self.io_bootloader   = cfg['io_bootloader']
        self.io_in_rst       = cfg['io_in_rst']
        self.rst_in_type     = cfg['rst_in_type']
        # self.signals.append('  logic '+self.io_bootloader+'; // IO Pin')
        self.io['in'].append(['logic', cfg['io_bootloader']])
        self.io['in'].append(['logic', cfg['io_in_rst']])
        self.acc_type        = 'acc_rst'

class Clock(base_module):
    def __init__(self, cfg):
        clk_cfg = cfg['clk']
        if clk_cfg['type'] == 'pll':
            super().__init__(clk_cfg['name'], 0, 0, options.tmpl_clk_pll_xlnx)
            self.rst_in_type   = clk_cfg['pll']['rst_in_type']
            self.io_rst_pin    = clk_cfg['pll']['io_rst_pin']
            self.divclk_divide = clk_cfg['pll']['divclk_divide']
            self.clkfbout_mult = clk_cfg['pll']['clkfbout_mult']
            self.clkout_divide = clk_cfg['pll']['clkout_divide']
            self.clkin_period  = clk_cfg['pll']['clkin_period']
            self.io_in_clk     = clk_cfg['io_in_clk']
            self.clk_int       = clk_cfg['clk_int']
            self.signals.append('  logic '+self.clk_int+';')
            self.io['in'].append(['logic', clk_cfg['io_in_clk']])
            self.io['in'].append(['logic', clk_cfg['pll']['io_rst_pin']])
        else:
            super().__init__(clk_cfg['name'], 0, 0, options.tmpl_clk)
            self.io_in_clk     = clk_cfg['io_in_clk']
            self.clk_int       = clk_cfg['clk_int']
            self.signals.append('  logic '+clk_cfg['clk_int']+';')
            self.io['in'].append(['logic', clk_cfg['io_in_clk']])

class RaveNoC(base_module):
    def __init__(self, cfg, soc_common, slv_id, noc_type):
        super().__init__(cfg['name'], soc_common['clk'], soc_common['rst'], options.tmpl_ravenoc)
        if noc_type == 'slave':
            self.txn_id_w     = soc_common['txn_id']
            self.slv_id       = slv_id
            self.noc_type     = noc_type
            self.acc_type     = 'acc_noc'
            self.desc         = cfg['desc']
            self.irq_noc      = cfg['irq_noc']
            self.io['in'].append(['s_irq_ni_t', self.irq_noc])
            self.io['in'].append(['s_axi_miso_t', 'noc_axi_miso_i'])
            self.io['out'].append(['s_axi_mosi_t', 'noc_axi_mosi_o'])

class Reset(base_module):
    def __init__(self, cfg):
        rst_cfg = cfg['rst']
        self.rst_type = rst_cfg['type']
        if rst_cfg['type'] == 'direct':
            super().__init__(rst_cfg['name'], 0, 0, options.tmpl_rst)
            self.rst_int = rst_cfg['rst_int']
            self.io_in_rst = rst_cfg['io_in_rst']
            self.rst_in_type = rst_cfg['rst_in_type']
            self.io['in'].append(['logic', rst_cfg['io_in_rst']])
        else:
            super().__init__(rst_cfg['name'], 0, 0, options.tmpl_rst)
            self.io['in'].append(['logic', rst_cfg['io_in_rst']])
            self.signals.append('  logic '+rst_cfg['rst_int']+';')

class ModuleHeader(base_module):
    def __init__(self, type_cfg, name, desc, io_list):
        super().__init__(0, 0, 0, options.tmpl_module_header)
        if type_cfg == 'soc':
            self.name = name
            self.type = 'soc'
            for i in io_list:
                if 'noc_axi_mosi_o' in i:
                    self.type = 'mpsoc'
                    break
            self.io_list = io_list
            self.desc = desc
            self.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        elif type_cfg == 'mpsoc':
            self.name = name
            self.type = 'mpsoc'
            self.io_list = io_list
            self.desc = desc
            self.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        else:
            logging.error('Illegal ModuleHeader type')

class ModuleDefines(base_module):
    def __init__(self, name, desc, defines):
        super().__init__(0, 0, 0, options.tmpl_defines)
        self.defines = defines
        self.name = name
        self.type = 'mpsoc'
        self.desc = desc
        self.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

class ModuleInstance(base_module):
    def __init__(self, module_info):
        super().__init__(0, 0, 0, options.tmpl_module_inst)
        self.name           = module_info['name']
        self.io_clk         = module_info['io_clk']
        self.io_rst         = module_info['io_rst']
        self.io_clk_mpsoc   = module_info['io_clk_mpsoc']
        self.io_rst_mpsoc   = module_info['io_rst_mpsoc']
        self.io_noc_miso    = module_info['io_noc_mosi']
        self.io_noc_mosi    = module_info['io_noc_miso']
        self.io_noc_irq     = module_info['io_noc_irq']

class Axi4AccEthernet(base_module):
    def __init__(self, soc_common, eth_info):
        super().__init__(eth_info['name'], soc_common['clk'], soc_common['rst'], options.tmpl_axi4_ethernet)
        #self.clk_ext       = soc_common['clk_ext']
        self.clk_ext       = eth_info['clk_ext']
        self.desc          = eth_info['desc']
        self.csr_slv_id    = eth_info['csr_slv_id']
        self.inf_slv_id    = eth_info['inf_slv_id']
        self.out_slv_id    = eth_info['out_slv_id']
        self.pkt_recv_irq  = eth_info['pkt_recv_irq']
        self.pkt_sent_irq  = eth_info['pkt_sent_irq']
        self.pkt_recv_full_irq = eth_info['pkt_recv_full_irq']

        self.signals.append('  logic '+self.pkt_recv_irq+';')
        self.signals.append('  logic '+self.pkt_sent_irq+';')
        self.signals.append('  logic '+self.pkt_recv_full_irq+';')
        self.signals.append('  s_rgmii_tx_t phy_tx;')
        self.signals.append('  s_rgmii_rx_t phy_rx;')

        self.io['in'].append(['logic','phy_rx_clk'])
        self.io['in'].append(['logic [3:0]','phy_rxd'])
        self.io['in'].append(['logic','phy_rx_ctl'])
        self.io['in'].append(['logic','phy_int_n'])
        self.io['in'].append(['logic','phy_pme_n'])
        self.io['in'].append(['logic',self.clk_ext])
        self.io['out'].append(['logic','phy_tx_clk'])
        self.io['out'].append(['logic [3:0]','phy_txd'])
        self.io['out'].append(['logic','phy_tx_ctl'])
        self.io['out'].append(['logic','phy_reset_n'])
