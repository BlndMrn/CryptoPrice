from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union

from CryptoPrice.utils.time import TIMEFRAME


@dataclass
class Price:
    value: float
    asset: str
    ref_asset: str
    timestamp: int
    source: str


@dataclass
class MetaPrice:
    value: float
    asset: str
    ref_asset: str
    prices: List[Union[Price, MetaPrice]]
    source: str = ''

    @staticmethod
    def mean_from_meta_price(meta_prices: List[MetaPrice]) -> MetaPrice:
        """
        Return the mean price from a list of meta price

        :param meta_prices: list of meta price with the same asset and ref assets
        :type meta_prices:
        :return: the mean Meta price
        :rtype: MetaPrice
        """
        if len(meta_prices) == 0:
            raise ValueError("at least one MetaPrice is needed")
        asset = meta_prices[0].asset
        ref_asset = meta_prices[0].ref_asset
        cum_value = 0
        for meta_price in meta_prices:
            if (asset, ref_asset) != (meta_price.asset, meta_price.ref_asset):
                raise ValueError("asset and ref asset are inconsistent")
            cum_value += meta_price.value
        return MetaPrice(cum_value / len(meta_prices), asset, ref_asset, meta_prices, source="mean_meta")

    @staticmethod
    def from_price_path(assets: List[str], price_path: List[Price]) -> MetaPrice:
        """
        Construct a MetaPrice instance from a price path

        :param assets: list of assets seen on the path (in order)
        :type assets: List[str]
        :param price_path: list of price used to go from the first asset to the last one
        :type price_path: List[Price]
        :return: the MetaPrice representing the price between the first and the last asset
        :rtype: MetaPrice
        """
        if len(assets) < 2:
            raise ValueError(f"at least two assets are required, {len(assets)} were received")
        if len(assets) != len(price_path) + 1:
            raise ValueError(f"the number of assets and prices are not coherent")
        cumulated_price = 1.
        for i, price in enumerate(price_path):
            current_asset, next_asset = assets[i:i + 2]
            if price.asset == next_asset:
                cumulated_price /= price.value
            else:
                cumulated_price *= price.value
        return MetaPrice(cumulated_price, assets[0], assets[-1], price_path, source='price_path')


@dataclass
class Kline:
    open_timestamp: int
    open: float
    high: float
    low: float
    close: float
    asset: str
    ref_asset: str
    timeframe: TIMEFRAME
    source: str