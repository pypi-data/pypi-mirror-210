#!/usr/bin/env python3

"""
Modbus/TCP server with start/stop schedule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run this as root to listen on TCP privileged ports (<= 1024).

Default Modbus/TCP port is 502, so we prefix call with sudo. With argument
"--host 0.0.0.0", server listen on all IPv4 of the host. Instead of just
open tcp/502 on local interface.
$ sudo ./server_schedule.py --host 0.0.0.0
"""

import argparse
from datetime import datetime
from random import randint
import time
from pyModbusTCP.server import ModbusServer, DataBank
# need https://github.com/dbader/schedule
import schedule


class MyDataBank(DataBank):
    """A custom ModbusServerDataBank for override get_holding_registers method."""

    def __init__(self):
        # turn off allocation of memory for standard modbus object types
        # only "holding registers" space will be replaced by dynamic build values.
        super().__init__(virtual_mode=True)

    def get_holding_registers(self, address, number=1, srv_info=None):
        """Get virtual holding registers."""
        try:
            print('getting holding_registers')
            return [randint(0,65535) for a in range(address, address+number)]
        except KeyError:
            return


# parse args
parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str, default='127.0.0.1', help='Host (default: 127.0.0.1)')
parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
args = parser.parse_args()
# init modbus server and start it
# server = ModbusServer(host=args.host, port=args.port, data_bank=MyDataBank())
server = ModbusServer(host=args.host, port=args.port, no_block=True,data_bank=MyDataBank())
server.start()
print('Modbus TCP server is running on 127.0.0.1...')


# init scheduler
# schedule a daily downtime (from 18:00 to 06:00)
# schedule.every().day.at('18:00').do(server.stop)
# schedule.every().day.at('06:00').do(server.start)
# update life word at @0
# schedule.every(10).seconds.do(server.data_bank.set_holding_registers)

# main loop
while True:
    schedule.run_pending()
    time.sleep(1)