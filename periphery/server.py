import threading

from periphery.ledger_server import LedgerServer
from periphery.simulator_execution_server import SimulatorExecutionServer


class PeripheryServer:

    def __init__(self):
        self.ledger_server = LedgerServer()
        self.simulation_execution_server = SimulatorExecutionServer()

    def start_servers(self):
        t1 = threading.Thread(target=self.ledger_server.start_server)
        t1.start()

        t2 = threading.Thread(target=self.simulation_execution_server.start_server)
        t2.start()


if __name__ == '__main__':
    ps = PeripheryServer()
    ps.start_servers()