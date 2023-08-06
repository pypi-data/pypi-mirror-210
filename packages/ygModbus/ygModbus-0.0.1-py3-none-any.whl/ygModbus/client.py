import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine
from pyModbusTCP.client import ModbusClient

c = ModbusClient(host="127.0.0.1", port=502, auto_open=True)
regs = c.read_holding_registers(reg_addr=40001,reg_nb=4)
regs