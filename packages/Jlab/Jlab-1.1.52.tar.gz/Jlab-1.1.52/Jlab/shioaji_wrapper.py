import datetime
import pandas as pd


class ContractFinder:
    def __init__(self, api):
        self.api = api

    def get_latest_option_contract(self):
        wednesday_time = self._get_next_wednesday()
        contracts_df = self._get_tx_options_contracts()
        return self._get_next_contract(contracts_df, wednesday_time)

    def _get_next_wednesday(self):
        today = datetime.datetime.today()
        wednesday = (today + datetime.timedelta(days=(2 - today.weekday()))).date()
        wednesday_time = datetime.datetime.combine(
            wednesday, datetime.datetime.min.time()
        ) + datetime.timedelta(
            hours=13, minutes=45, seconds=0
        )  # Adjusted to 13:45 due to 14:50 activation time
        return wednesday_time

    def _get_tx_options_contracts(self):
        # Get all TX options contracts
        contracts = []
        for option in self.api.Contracts.Options:
            for contract in option:
                if "TX" in contract.category:
                    contracts.append(
                        [
                            contract.symbol,
                            contract.name,
                            contract.update_date,
                            contract.delivery_date,
                        ]
                    )
        # Convert contracts data to DataFrame
        df = pd.DataFrame(
            contracts, columns=["symbol", "name", "update_date", "delivery_date"]
        )

        # Convert date columns to datetime format
        df["update_date"] = pd.to_datetime(df["update_date"])
        df["delivery_date"] = pd.to_datetime(df["delivery_date"])

        # Calculate date differences
        df["date_diff"] = (df["delivery_date"] - df["update_date"]).dt.days

        # Sort by date differences in ascending order
        df = df.sort_values(by="date_diff")
        return df

    def _get_next_contract(self, contracts_df, wednesday_time):
        now = datetime.datetime.now()

        if now < wednesday_time:
            return contracts_df.iloc[0]
        else:
            # Remove contracts with zero date difference
            contracts_df = contracts_df[contracts_df["date_diff"] != 0]
            contracts_df.reset_index(drop=True, inplace=True)
            return contracts_df.iloc[0]


class ShioajiWrapper:
    def __init__(self, api):
        self.api = api

    def login(self, api_key, api_secret, contracts_timeout=10000):
        self.api.login(api_key, api_secret, contracts_timeout=contracts_timeout)

    def get_api(self):
        return self.api

    def get_stock_list(self):
        stock_list = [
            s
            for stock in self.api.Contracts.Stocks
            for s in stock
            if s["symbol"][:3] != "OES" and len(s["code"]) == 4
        ]
        code_list = sorted([i.code for i in stock_list])
        return code_list

    def get_snapshots(self, stock_list):
        contracts_dict = self.api.Contracts.Stocks
        contracts = [contracts_dict[i] for i in stock_list]
        snapshots = self.api.snapshots(contracts)
        df = pd.DataFrame(s.__dict__ for s in snapshots)
        df.ts = pd.to_datetime(df.ts)
        return df

    def get_near_month_txf_contract(self):
        contract = min(
            [
                x
                for x in self.api.Contracts.Futures.TXF
                if x.code[-2:] not in ["R1", "R2"]
            ],
            key=lambda x: x.delivery_date,
        )
        return contract

    def is_trading_day(self, now=datetime.datetime.now()):
        kbars = self.api.kbars(
            contract=self.api.Contracts.Indexs.TSE.TSE001,
            start=now.strftime("%Y-%m-%d"),
            end=now.strftime("%Y-%m-%d"),
        )
        return len(kbars.Open) > 0

    def get_latest_option_contract(self):
        contract_finder = ContractFinder(self.api)
        return contract_finder.get_latest_option_contract()
