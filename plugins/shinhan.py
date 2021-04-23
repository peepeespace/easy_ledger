from plugins.client import LedgerPluginClient


class ShinhanLedgerPlugin(LedgerPluginClient):

    def __init__(self, ledger_name, strategy_name):
        super().__init__(ledger_name, strategy_name)

    def stream(self, data):
        data_type = data.get('type')

        if data_type in ['실시간잔고(선물/옵션)']:
            pass

        elif data_type in ['선물옵션실시간주문체결']:
            status_code = data.get('처리구분')

            if status_code == '00':
                pass

            elif status_code == '03':
                pass

            elif status_code == '04':
                pass

            elif status_code == '05':
                pass

        elif data_type in ['선물옵션체결/미체결내역조회']:
            pass

        elif data_type in ['실시간잔고조회(선물/옵션)']:
            pass

        elif data_type in ['선물옵션예수금내역조회']:
            pass

        elif data_type in ['선물옵션매매일손익조회']:
            pass

