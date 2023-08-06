import pandas as pd


class PriceMetrics:
    def __init__(self, prices):
        self.prices = prices
        self.base_price = prices[0]
        self.min_price = min(prices)
        self.max_price = max(prices[1:])
        self.max_price_before_min = self._get_max_price_before_min()
        self.mae = self._calculate_mae()
        self.bmfe = self._calculate_bmfe()
        self.gmfe = self._calculate_gmfe()
        self.edge_ratio = self._calculate_edge_ratio()

    def _get_max_price_before_min(self):
        if (
            self.min_price is None
            or self.prices[: self.prices.index(self.min_price)] == []
        ):
            return None
        return max(self.prices[: self.prices.index(self.min_price)])

    def _calculate_mae(self):
        if self.min_price is None or self.min_price >= self.base_price:
            return 0
        return (self.min_price - self.base_price) / self.base_price * 100

    def _calculate_bmfe(self):
        if (
            self.max_price_before_min is None
            or self.base_price >= self.max_price_before_min
        ):
            return 0
        return ((self.max_price_before_min - self.base_price) / self.base_price) * 100

    def _calculate_gmfe(self):
        if self.max_price is None or self.max_price <= self.base_price:
            return 0
        return ((self.max_price - self.base_price) / self.base_price) * 100

    def _calculate_edge_ratio(self):
        if self.mae == 0:
            return self._calculate_gmfe()
        return ((self.gmfe - abs(self.mae)) / abs(self.mae)) * 100

    def get_max_drawdown(self):
        df = pd.DataFrame(self.prices, columns=["Close"])
        df["Max"] = df["Close"].cummax()
        df["Drawdown"] = df["Close"] / df["Max"] - 1
        df["Max Drawdown"] = df["Drawdown"].cummin()
        mdd = df["Max Drawdown"].min()
        return mdd * 100


if __name__ == "__main__":
    # prices = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
    prices = [10, 20, 15, 25, 18, 30, 12]
    metrics = PriceMetrics(prices)
    print(metrics.mae)
    print(metrics.bmfe)
    print(metrics.gmfe)
    print(metrics.edge_ratio)
    print(metrics.get_max_drawdown())
