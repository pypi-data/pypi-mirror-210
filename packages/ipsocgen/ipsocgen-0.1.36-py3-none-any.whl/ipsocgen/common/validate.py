import logging
import argparse
import pathlib
import sys
import yaml
from cerberus import Validator
try:
    from ipsocgen.common.constants import options, CustomFormatter
except ImportError:
    from common.constants import options, CustomFormatter

def validate_config(args):
    try:
        cfg = yaml.safe_load(args['config'])
    except yaml.YAMLError as exc:
        logging.error('Error while parsing YAML file:')
        if hasattr(exc, 'problem_mark'):
            if exc.context != None:
                logging.error('  parser says\n'+str(exc.problem_mark)+'\n  '+
                              str(exc.problem)+' '+str(exc.context)+
                              '\nPlease correct data and retry.')
                sys.exit(1)
            else:
                logging.error('  parser says\n'+str(exc.problem_mark)+'\n  '+
                              str(exc.problem)+
                              '\nPlease correct data and retry.')
                sys.exit(1)
        else:
            logging.error('Something went wrong while parsing yaml file')
            sys.exit(1)
    logging.debug('YAML file parse done without errors')

    sch_cfg = Validator(yaml.safe_load(open(options.sch_cfg,'r')))
    sch_cfg.allow_unknown = True
    sch_cfg.require_all = True

    # Validate all main entries
    if sch_cfg.validate(cfg) == False:
        logging.error(sch_cfg.errors)
        return False, cfg

    # Check number of masters/slaves
    if cfg['type'] == 'soc':
        if 'soc_desc' not in cfg.keys():
            logging.error('soc_desc not present in the cfg file')
            return False, cfg

        status = _val_soc(cfg['soc_desc'], 'soc')

        if status == False:
            return False, cfg

        logging.info('Valid YAML configuration - basic check')
        return True, cfg
    else:
        if 'mpsoc_desc' not in cfg.keys():
            logging.error('mpsoc_desc not present in the cfg file')
            return False, cfg

        if _val_mpsoc(cfg) == False:
            logging.error('Illegal MPSoC yaml configuration file!')
            return False, cfg

        for tile, tile_desc in cfg['mpsoc_desc']['tiles'].items():
            logging.debug('Checking cfg for tile no '+str(tile))
            status = _val_soc(tile_desc, 'mpsoc')
            if status == False:
                return False, cfg

        logging.info('Valid YAML configuration - basic check')
        return True, cfg

def _val_mpsoc(cfg):
    cfg = cfg['mpsoc_desc']
    # First check if we have mandatory fields
    if 'clk' not in cfg:
        logging.error('Missing clk info on MPSoC desc')
        return False
    if 'rst' not in cfg:
        logging.error('Missing rst info on MPSoC desc')
        return False
    if 'noc' not in cfg:
        logging.error('Missing NoC info on MPSoC desc')
        return False

    # Check if number of tiles aligns with NoC size
    noc_size = cfg['noc']['size_x']*cfg['noc']['size_y']
    if  noc_size != len(cfg['tiles']):
        logging.error('No of Tiles != from NoC size, '+str(noc_size)+' != '+str(len(cfg['tiles'])))
        return False

    # Check if all NoC slaves exist and that are aligned
    noc_slv_id = 0
    first = False
    exist = False
    for tile, tile_desc in cfg['tiles'].items():
        exist = False
        if first == False:
            first = True
            for slave, slave_desc in tile_desc['slaves'].items():
                if slave_desc['type'] == 'acc_noc':
                    noc_slv_id = slave
                    exist = True
            if exist == False:
                logging.error('Missing NoC slave on tile '+str(tile))
                return False
        else:
            if tile_desc['slaves'][noc_slv_id]['type'] != 'acc_noc':
                logging.error('Missing NoC slave on tile '+str(tile))
                return False

    return True

def _val_soc(cfg, cfg_type):
    soc = cfg
    there_is_a_dma = 0
    # Check if there is a proc_required tag
    if 'proc_required' not in cfg:
        logging.error('Missing proc_required tag: yes or no')
        return False

    if soc['proc_required'] == 'y':
        # Check if boot addr exist in case of boot.type == slave
        if soc['proc']['boot']['type'] == 'slave':
            if soc['proc']['boot']['slave'] >= soc['num_slaves']:
                logging.error('Boot Address of unknown slave')
                return False

    if soc['num_masters'] != len(soc['masters']):
        logging.error('Missing master declaration num_master is '+
                      str(soc['num_masters'])+
                      ' but only '+str(len(soc['masters']))+
                      ' were declared!')
        return False
    if soc['num_slaves'] != len(soc['slaves']):
        logging.error('Missing slave declaration num_slaves is '+
                      str(soc['num_slaves'])+
                      ' but only '+str(len(soc['slaves']))+
                      ' were declared!')
        return False
    # Master check
    sch_master = Validator(yaml.safe_load(open(options.sch_master,'r')))
    sch_master.allow_unknown = True
    sch_master.require_all = True
    unique_master_name = []
    for master, master_desc in soc['masters'].items():
        if master_desc['type'] == 'acc_dma':
            there_is_a_dma = 1
        if sch_master.validate(master_desc) == False:
            logging.error('Error on master '+str(master_desc))
            logging.error(sch_master.errors)
            return False
        else:
            if master_desc['name'] not in unique_master_name:
                unique_master_name.append(master_desc['name'])
            else:
                logging.error('Error on master '+str(master)+' not unique name!')
                return False

    logging.debug('Valid master configuration')

    # If there's a DMA, check if the number of master == slaves
    if there_is_a_dma != 0:
        if _val_dma(soc) != 0:
            logging.error('Number of m.dma != s.dma!')
            return False

    # Slave check
    sch_slave = Validator(yaml.safe_load(open(options.sch_slave,'r')))
    sch_slave.allow_unknown = True
    sch_slave.require_all = True
    unique_slave_name = []
    acc_rst_found = 0
    acc_eth_found = 0
    for slave, slave_desc in soc['slaves'].items():
        if sch_slave.validate(slave_desc) == False:
            logging.error('Error on slave '+str(slave_desc))
            logging.error(sch_slave.errors)
            return False
        else:
            if slave_desc['name'] not in unique_slave_name:
                unique_slave_name.append(slave_desc['name'])
                acc_rst_found += 1 if slave_desc['type'] == 'acc_rst' else 0
                if acc_rst_found > 1:
                    logging.error('More than one RST Controller is not supported')
                    return False
            else:
                logging.error('Error on slave '+str(slave)+' not unique name!')
                return False

            # If acc == ethernet, need to ensure there are at least 3x slaves (CSR, INFIFO, OUTFIFO)
            if slave_desc['type'] == 'acc_eth':
                acc_eth_found += 1

            # If NoC is found on SoC configuration, throw an error
            if slave_desc['type'] == 'acc_noc' and cfg_type == 'soc':
                logging.error('NoC detected on SoC configuration, please remove the NoC on slave: '+str(slave))
                return False

    if (acc_eth_found != 0) and (acc_eth_found != 3):
        logging.error('Number of ethernet acc is illegal, need to be either 0 or 3!')
        return False

    logging.debug('Valid slave configuration')
    return True

def _val_dma(cfg):
    dma_count = 0

    for m in cfg['masters']:
        if cfg['masters'][m]['type'] == 'acc_dma':
            dma_count += 1
    for s in cfg['slaves']:
        if cfg['slaves'][s]['type'] == 'acc_dma':
            dma_count -= 1
    return dma_count


