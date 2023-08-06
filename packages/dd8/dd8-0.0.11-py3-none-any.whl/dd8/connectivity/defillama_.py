# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 08:37:00 2022

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union, Any, Dict, List
import datetime
from .base import AsyncConnection

class DefillamaInstrument(object):
    def __init__(self, attributes: Union[None, Dict[str, Any]] = None) -> None:
        if not attributes is None:
            self.from_api(attributes)

    def from_api(self, attributes: Dict[str, Any]) -> None:
        """
        Instantiates object with attributes from Deribit API output.

        Parameters
        ----------
        attributes : dict
            key-value pairs returned from Deribit endpoint
        """
        if isinstance(attributes, dict):
            for k, v in attributes.items():
                setattr(self, k, v)
        else:
            raise TypeError('`attributes` must be of `dict` type.')

class DefillamaRest(AsyncConnection):
    _END_POINT = 'https://api.llama.fi'
    _REQUEST_PER_SECOND = 10
    
    def __init__(self) -> None:
        super().__init__(DefillamaRest._REQUEST_PER_SECOND)
    
    def _process_time_series(self, data: Union[List[Dict], List[List]]) -> List[List]:
        first_row = data[0]
        if isinstance(first_row, dict):
            variable_name = ''
            for k in first_row.keys():
                if k != 'date':
                    variable_name = k
                    break            
            output = [[datetime.datetime.fromtimestamp(int(row['date'])), row[variable_name]]
                    for row in data]            
        elif isinstance(first_row, list):
            output = [ [datetime.datetime.fromtimestamp(int(row[0])), row[1]] 
                        for row in data]
        else:
            raise TypeError('`data` must of of `List[List]` or `List[Dict]` type.')
            return
        output.sort(key=lambda x: x[0])
        return output

    def get_protocols(self) -> List[DefillamaInstrument]:
        """
        Get all protocols on DefiLlama along with their tvl.

        Return
        ------
        list[DefillamaInstrument]
            list of `DefillamaInstrument` that have attributes
            equivalent to keys of API response. Example:
                [
                    DefillamaInstrument(
                        {
                            "id": "2269",
                            "name": "Binance CEX",
                            "address": null,
                            "symbol": "-",
                            "url": "https://www.binance.com",
                            "description": "Binance is a cryptocurrency exchange which is the largest exchange in the world in terms of daily trading volume of cryptocurrencies",
                            "chain": "Multi-Chain",
                            "logo": "https://icons.llama.fi/binance-cex.jpg",
                            "audits": "0",
                            "audit_note": null,
                            "gecko_id": null,
                            "cmcId": null,
                            "category": "CEX",
                            "chains": [
                            "Ethereum",
                            "Binance",
                            "Tron",
                            "Bitcoin"
                            ],
                            "module": "binance/index.js",
                            "twitter": "binance",
                            "forkedFrom": [],
                            "oracles": [],
                            "listedAt": 1668170565,
                            "slug": "binance-cex",
                            "tvl": 55953816171.60367,
                            "chainTvls": {
                            "Binance": 10029201603.586607,
                            "Ethereum": 29511764351.776558,
                            "Tron": 8552274414.027572,
                            "Bitcoin": 7860575802.212934
                            },
                            "change_1h": -0.09674996358737076,
                            "change_1d": -0.5980762513261197,
                            "change_7d": -7.42929508172395
                        }
                    )
                ]
        """
        url = self._END_POINT + '/protocols'
        responses = self.loop(self._get, url)
        instruments = []
        for response in responses:
            instrument = DefillamaInstrument()
            instrument.from_api(response)
            instruments.append(instrument)        
        return instruments

    def get_protocol(self, protocol_slug: str) -> DefillamaInstrument:
        """
        Get historical TVL of a protocol and breakdowns by token and chain.

        Return
        ------
        DefillamaInstrument
            an instance of `DefillamaInstrument` that has attributes
            equivalent to keys of API response. 
        """
        url = self._END_POINT + '/protocol/{protocol}'.format(protocol=protocol_slug)
        response = self.loop(self._get, url)
        instrument = DefillamaInstrument()
        instrument.from_api(response)
        return instrument
    
    def get_charts(self) -> List[List]:
        """
        Get historical TVL of DeFi on all chains.

        Return
        ------
        list[list]
            time series of TVL in chronological oder. Example:
                [
                    [datetime.datetime(2018, 11, 3, 8, 0), 34643.89060970875],
                    [datetime.datetime(2018, 11, 4, 8, 0), 41268.18310687588]
                ]        
        """
        url = self._END_POINT + '/charts'
        responses = self.loop(self._get, url)
        # data = [[datetime.datetime.fromtimestamp(int(response['date'])), response['totalLiquidityUSD']]
        #         for response in responses]
        # data.sort(key=lambda x: x[0])
        data = self._process_time_series(responses)
        return data
    
    def get_chart(self, chain_slug: str) -> List[List]:
        """
        Get historical TVL of a particular chain.

        Return
        ------
        list[list]
            time series of TVL in chronological oder. Example:
                [
                    [datetime.datetime(2018, 11, 3, 8, 0), 34643.89060970875],
                    [datetime.datetime(2018, 11, 4, 8, 0), 41268.18310687588]
                ]      
        """
        url = self._END_POINT + '/charts/{chain}'.format(chain=chain_slug)
        responses = self.loop(self._get, url)
        data = [[datetime.datetime.fromtimestamp(int(response['date'])), response['totalLiquidityUSD']]
                for response in responses]
        data.sort(key=lambda x: x[0])
        return data

    def get_chains(self) -> List:
        """
        Get current TVL of all chains.

        Return
        ------
        list[DefillamaInstrument]
            list of `DefillamaInstrument` that have attributes
            equivalent to keys of API response. Example:
                [
                    DefillamaInstrument(
                        {
                            "gecko_id": "optimism",
                            "tvl": 641696587.4735153,
                            "tokenSymbol": "OP",
                            "cmcId": "11840",
                            "name": "Optimism",
                            "chainId": 10
                        }
                    )
                ]
        """
        url = self._END_POINT + '/chains'
        responses = self.loop(self._get, url)
        instruments = []
        for response in responses:
            instrument = DefillamaInstrument()
            instrument.from_api(response)
            instruments.append(instrument)
        return instruments

    def get_fees(self, data_type: str, exclude_total_data_chart: bool = True,
                    exclude_total_data_chart_breakdown: bool = True) -> DefillamaInstrument:
        """
        Get fees and revenue data of all protocols.

        Return
        ------
        DefillamaInstrument
            an instance of `DefillamaInstrument` that has attributes
            equivalent to keys of API response. Example:
                Defillama(
                    {
                    "totalDataChart": [],
                    "totalDataChartBreakdown": [],
                    "protocols": [
                        {
                        "name": "0vix",
                        "disabled": false,
                        "displayName": "0vix",
                        "module": "0vix",
                        "category": "Lending",
                        "logo": "https://icons.llama.fi/0vix.png",
                        "change_1d": -9.84,
                        "change_7d": -12.69,
                        "change_1m": -13.98,
                        "change_7dover7d": -2.29,
                        "total24h": 459.295484973285,
                        "totalAllTime": 52632.92932103914,
                        "breakdown24h": {
                            "polygon": {
                            "0vix": 459.295484973285
                            }
                        },
                        "chains": [
                            "Polygon"
                        ],
                        "protocolsStats": null,
                        "protocolType": "protocol",
                        "methodologyURL": "https://github.com/DefiLlama/dimension-adapters/blob/master/fees/0vix.ts",
                        "methodology": {
                            "UserFees": "Interest paid by borrowers",
                            "Fees": "Interest paid by borrowers",
                            "Revenue": "% of interest going to treasury",
                            "ProtocolRevenue": "% of interest going to treasury",
                            "SupplySideRevenue": "Interest paid to lenders"
                        },
                        "latestFetchIsOk": true,
                        "dailyUserFees": null,
                        "dailyHoldersRevenue": null,
                        "dailyCreatorRevenue": null,
                        "dailySupplySideRevenue": null,
                        "dailyProtocolRevenue": null
                        },

                    }
                )
        """
        supported_data_type = ['totalFees', 'dailyFees', 'totalRevenus', 'dailyRevenus']
        if not data_type in supported_data_type:
            raise ValueError('unsupported `data_type`.')
            return
        else:
            url = self._END_POINT + '/overview/fees?excludeTotalDataChart={exclude_total_data_chart}&excludeTotalDataChartBreakdown={exclude_total_data_chart_breakdown}&dataType={data_type}'.format(
                exclude_total_data_chart=str(exclude_total_data_chart).lower(), 
                exclude_total_data_chart_breakdown=str(exclude_total_data_chart_breakdown).lower(),
                data_type = data_type
            )
            response = self.loop(self._get, url)
            instrument = DefillamaInstrument()
            instrument.from_api(response)
            return instrument

    def get_fees_for_chain(self, chain_name: str, data_type: str, exclude_total_data_chart: bool = True,
                                exclude_total_data_chart_breakdown: bool = True) -> DefillamaInstrument:
        """
        Get fees and revenue data of particular chain.

        Return
        ------
        Return
        ------
        DefillamaInstrument
            an instance of `DefillamaInstrument` that has attributes
            equivalent to keys of API response. Example:
                Defillama(
                    {
                    "totalDataChart": [],
                    "totalDataChartBreakdown": [],
                    "protocols": [
                        {
                        "name": "0vix",
                        "disabled": false,
                        "displayName": "0vix",
                        "module": "0vix",
                        "category": "Lending",
                        "logo": "https://icons.llama.fi/0vix.png",
                        "change_1d": -9.84,
                        "change_7d": -12.69,
                        "change_1m": -13.98,
                        "change_7dover7d": -2.29,
                        "total24h": 459.295484973285,
                        "totalAllTime": 52632.92932103914,
                        "breakdown24h": {
                            "polygon": {
                            "0vix": 459.295484973285
                            }
                        },
                        "chains": [
                            "Polygon"
                        ],
                        "protocolsStats": null,
                        "protocolType": "protocol",
                        "methodologyURL": "https://github.com/DefiLlama/dimension-adapters/blob/master/fees/0vix.ts",
                        "methodology": {
                            "UserFees": "Interest paid by borrowers",
                            "Fees": "Interest paid by borrowers",
                            "Revenue": "% of interest going to treasury",
                            "ProtocolRevenue": "% of interest going to treasury",
                            "SupplySideRevenue": "Interest paid to lenders"
                        },
                        "latestFetchIsOk": true,
                        "dailyUserFees": null,
                        "dailyHoldersRevenue": null,
                        "dailyCreatorRevenue": null,
                        "dailySupplySideRevenue": null,
                        "dailyProtocolRevenue": null
                        },

                    }
                )        
        """
        supported_data_type = ['totalFees', 'dailyFees', 'totalRevenus', 'dailyRevenus']
        if not data_type in supported_data_type:
            raise ValueError('unsupported `data_type`.')
            return
        else:
            url = self._END_POINT + '/overview/fees/{chain}?excludeTotalDataChart={exclude_total_data_chart}&excludeTotalDataChartBreakdown={exclude_total_data_chart_breakdown}&dataType={data_type}'.format(
                chain = chain_name,
                exclude_total_data_chart=str(exclude_total_data_chart).lower(), 
                exclude_total_data_chart_breakdown=str(exclude_total_data_chart_breakdown).lower(),
                data_type = data_type
            )
            response = self.loop(self._get, url)
            instrument = DefillamaInstrument()
            instrument.from_api(response)
            return instrument

    def get_fees_for_protocol(self, protocol_slug: str, data_type: str) -> DefillamaInstrument:
        """
        Get fees and revenue data of particular protocol.

        Return
        ------
        Return
        ------
        DefillamaInstrument
            an instance of `DefillamaInstrument` that has attributes
            equivalent to keys of API response. Example:
                Defillama(
                    {
                    "totalDataChart": [],
                    "totalDataChartBreakdown": [],
                    "protocols": [
                        {
                        "name": "0vix",
                        "disabled": false,
                        "displayName": "0vix",
                        "module": "0vix",
                        "category": "Lending",
                        "logo": "https://icons.llama.fi/0vix.png",
                        "change_1d": -9.84,
                        "change_7d": -12.69,
                        "change_1m": -13.98,
                        "change_7dover7d": -2.29,
                        "total24h": 459.295484973285,
                        "totalAllTime": 52632.92932103914,
                        "breakdown24h": {
                            "polygon": {
                            "0vix": 459.295484973285
                            }
                        },
                        "chains": [
                            "Polygon"
                        ],
                        "protocolsStats": null,
                        "protocolType": "protocol",
                        "methodologyURL": "https://github.com/DefiLlama/dimension-adapters/blob/master/fees/0vix.ts",
                        "methodology": {
                            "UserFees": "Interest paid by borrowers",
                            "Fees": "Interest paid by borrowers",
                            "Revenue": "% of interest going to treasury",
                            "ProtocolRevenue": "% of interest going to treasury",
                            "SupplySideRevenue": "Interest paid to lenders"
                        },
                        "latestFetchIsOk": true,
                        "dailyUserFees": null,
                        "dailyHoldersRevenue": null,
                        "dailyCreatorRevenue": null,
                        "dailySupplySideRevenue": null,
                        "dailyProtocolRevenue": null
                        },

                    }
                )        
        """        
        supported_data_type = ['totalFees', 'dailyFees', 'totalRevenus', 'dailyRevenus']
        if not data_type in supported_data_type:
            raise ValueError('unsupported `data_type`.')
            return
        else:
            url = self._END_POINT + '/overview/fees/{protocol}?dataType={data_type}'.format(
                protocol = protocol_slug,                
                data_type = data_type
            )
            response = self.loop(self._get, url)
            instrument = DefillamaInstrument()
            instrument.from_api(response)
            return instrument
            