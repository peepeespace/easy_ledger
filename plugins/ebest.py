from plugins.client import LedgerPluginClient


class EbestLedgerPlugin(LedgerPluginClient):

    def __init__(self, ledger_name, strategy_name):
        super().__init__(ledger_name, strategy_name)

    def stream(self, data):
        data_type = data.get('type')

        if data_type == '주문접수':
            pass

        elif data_type == '주문취소':
            pass

        elif data_type == '주문체결':
            pass