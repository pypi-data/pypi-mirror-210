

import urllib.parse
import hashlib
import hmac
import requests
import time
import json
from datetime import datetime

api_url         = "https://open-api.bingx.com"

API_key         = 'yourAPI_Key'
Secrect_Key     = 'yourSecrect_Key'

infoGet         = 'GET'
infoPost        = 'POST'
infoDelete      ='DELETE'

url_balance             =     '/openApi/swap/v2/user/balance'
url_new_order           =     '/openApi/swap/v2/trade/order'
url_cancel_order        =     '/openApi/swap/v2/trade/order'
url_getopenorder        =     '/openApi/swap/v2/trade/openOrders'
url_getIdopenorder      =     '/openApi/swap/v2/trade/order'
url_getpositions        =     '/openApi/swap/v2/user/positions'
url_cancelall_order     =     '/openApi/swap/v2/trade/allOpenOrders'
url_getKlines           =     '/openApi/swap/v2/quote/klines'
url_closeorder          =     '/openApi/swap/v2/trade/closeAllPositions'
url_all_contrats        =     '/openApi/swap/v2/quote/contracts'

class Client:
        def __init__(self,API_key,Secrect_Key):
            self.API_key = API_key
            self.Secrect_Key = Secrect_Key


        
        


        def getbalance(self):

            """Parametros:
            --------------

            Retorno:
            -------

                    >>> {
                        "code": 0,
                        "msg": "",
                        "data": {
                            "balance": {
                            "asset": "USDT",
                            "balance": "15.6128",
                            "equity": "15.6128",
                            "unrealizedProfit": "0.0000",
                            "realisedProfit": "0.0000",
                            "availableMargin": "15.6128",
                            "usedMargin": "0.0000",
                            "freezedMargin": "0.0000"
                                 }
                            }
                        }
            """
           
            time_stamp=int(time.time() * 10 ** 3) 
            data = {
                        'recvWindow':   15000,
                        "timestamp": time_stamp
                    }
            
            return self.xbingx_request(url_balance, data, self.API_key, self.Secrect_Key,infoGet) 



        def neworder(self,typ,side,symbol,**params):

            """Parametros:
            --------------  
                        
                                symbol	:	string	trading pair, for example: BTC-USDT, please use capital letters	\n
                                type	:	string	order type LIMIT, MARKET, STOP_MARKET, TAKE_PROFIT_MARKET, TRIGGER_LIMIT, TRIGGER_MARKET	\n
                                side	:	string	buying and selling direction SELL, BUY	\n
                                positionSide	:	string	Position direction, and only LONG or SHORT can be selected, the default is LONG	\n
                                price	:	float64	Order price	\n
                                quantity	:	float64	The order quantity	\n
                                stopPrice	:	float64	Trigger price, only required for STOP_MARKET, TAKE_PROFIT_MARKET, TRIGGER_LIMIT, TRIGGER_MARKET	\n
                                timestamp	:	int64	request timestamp, unit: millisecond	\n
                                recvWindow	:	int64	Request valid time window value, unit: millisecond	\n
                                timeInForce	:	string	Time in Force, currently supports PostOnly, GTC, IOC, and FOK	\n

                           
                            
                            
            Retorno:
            -------
                            Um dicionario do tipo:
                                                   >>> {
                                                        "code": 0,
                                                        "msg": "",
                                                        "data": {
                                                            "orderId": "11141",
                                                        }
                                                    }


            """
            
            time_stamp=int(time.time() * 10 ** 3) 
            data = {
                    'recvWindow':   15000,
                    'timestamp' :   time_stamp,
                    'symbol'    :   symbol,
                    'type'      :   typ,
                    'side'      :   side,
                    **params  
                    
                    }
            return self.xbingx_request(url_new_order, data,self.API_key, self.Secrect_Key,infoPost) 
            
        

        def getopenorder(self,symbol):
            """Parametros:
            --------------
                            symbol:	string	No	Trading pair, for example: BTC-USDT, please use capital letters
            Retorno:
            --------
                        Um dicionadio:

                                       >>> {
                                        "code": 0,
                                        "msg": "",
                                        "data": {
                                            "orders": [
                                            {
                                                "symbol": "LINK-USDT",
                                                "orderId": 1597783850786750464,
                                                "side": "BUY",
                                                "positionSide": "LONG",
                                                "type": "TRIGGER_MARKET",
                                                "origQty": "5.0",
                                                "price": "5.0000",
                                                "executedQty": "0.0",
                                                "avgPrice": "0.0000",
                                                "cumQuote": "0",
                                                "stopPrice": "5.0000",
                                                "profit": "0.0",
                                                "commission": "0.0",
                                                "status": "NEW",
                                                "time": 1669776330000,
                                                "updateTime": 1669776330000
                                            },
                                            {
                                                "symbol": "LINK-USDT",
                                                "orderId": 1597783835095859200,
                                                "side": "BUY",
                                                "positionSide": "LONG",
                                                "type": "TRIGGER_LIMIT",
                                                "origQty": "5.0",
                                                "price": "9.0000",
                                                "executedQty": "0.0",
                                                "avgPrice": "0.0000",
                                                "cumQuote": "0",
                                                "stopPrice": "9.5000",
                                                "profit": "0.0",
                                                "commission": "0.0",
                                                "status": "NEW",
                                                "time": 1669776326000,
                                                "updateTime": 1669776326000
                                            }
                                            ]
                                        }
                                        }


            """
            
            time_stamp=int(time.time() * 10 ** 3) 

        
            
            data = {
                            
                            "timestamp": time_stamp,
                            'recvWindow':   15000,
                            'symbol'    :   symbol
                            
                        }
                
            return self.xbingx_request(url_getopenorder, data,self.API_key, self.Secrect_Key,infoGet) 


        def getoIDopenorder(self,symbol,orderId):
            """Parametros:
            --------------
                            symbol:	    string	yes	trading pair, for example: BTC-USDT, please use capital letters
                            orderId:	int64	yes	order number

            
            Retorno:
            --------
                        Um dicionario:
                                        >>> {
                                            "code": 0,
                                            "msg": "",
                                            "data": {
                                                "order": {
                                                "symbol": "BTC-USDT",
                                                "orderId": 1597597642269917184,
                                                "side": "SELL",
                                                "positionSide": "LONG",
                                                "type": "TAKE_PROFIT_MARKET",
                                                "origQty": "1.0000",
                                                "price": "0.0",
                                                "executedQty": "0.0000",
                                                "avgPrice": "0.0",
                                                "cumQuote": "",
                                                "stopPrice": "16494.0",
                                                "profit": "",
                                                "commission": "",
                                                "status": "FILLED",
                                                "time": 1669731935000,
                                                "updateTime": 1669752524000
                                                }
                                            }
                                            }

            """
            
            time_stamp=int(time.time() * 10 ** 3) 

        
            
            data = {
                            
                            "timestamp" :   time_stamp,
                            'recvWindow':   15000,
                            'symbol'    :   symbol,    
                            'orderId'   :   orderId
                        }
                
            return self.xbingx_request(url_getIdopenorder, data,self.API_key, self.Secrect_Key,infoGet)     



        def Closeordens(self):
            """Parametros:
            --------------

            Retorno:
            --------
                        Um dicionario:
                                       >>> {
                                            "code": 0,
                                            "msg": "",
                                            "data": {
                                                "success": [
                                                1608667648466354176
                                                ],
                                                "failed": null
                                            }
                                            }
            """
            time_stamp=int(time.time() * 10 ** 3) 

            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        
                    
                    }
            
            return self.xbingx_request(url_closeorder, data, self.API_key, self.Secrect_Key,infoPost)



        def cancelarIDorder(self,orderId,symbol):
            """Parametros:
            --------------
                            orderId:	int64	yes	order number
                            symbol:	    string	yes	trading pair, for example: BTC-USDT, please use capital letters
            
            Retorno:
            ----------
                        Um dicionario:

                                       >>> {
                                            "code": 0,
                                            "msg": "",
                                            "data": {
                                                "order": {
                                                "symbol": "LINK-USDT",
                                                "orderId": 1597783850786750464,
                                                "side": "BUY",
                                                "positionSide": "LONG",
                                                "type": "TRIGGER_MARKET",
                                                "origQty": "5.0",
                                                "price": "5.0000",
                                                "executedQty": "0.0",
                                                "avgPrice": "0.0000",
                                                "cumQuote": "0",
                                                "stopPrice": "5.0000",
                                                "profit": "",
                                                "commission": "",
                                                "status": "CANCELLED",
                                                "time": 1669776330000,
                                                "updateTime": 1669776330000
                                                }
                                            }
                                            }

            """
            
            time_stamp=int(time.time() * 10 ** 3) 


            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        'symbol'    :   symbol,
                        'orderId'   :   orderId
                    
                    }
        
            return self.xbingx_request(url_cancel_order, data,self.API_key, self.Secrect_Key,infoDelete) 



        def cancelallordens(self,symbol):
            """Parametros:
            --------------
                            symbol:	string	yes	trading pair, for example: BTC-USDT, please use capital letters
            Retorno:
            ---------
                        Um dicionario:
                                        >>> {
                                            "code": 0,
                                            "msg": "",
                                            "data": {
                                                "success": [
                                                {
                                                    "symbol": "LINK-USDT",
                                                    "orderId": 1597783835095859200,
                                                    "side": "BUY",
                                                    "positionSide": "LONG",
                                                    "type": "TRIGGER_LIMIT",
                                                    "origQty": "5.0",
                                                    "price": "9.0000",
                                                    "executedQty": "0.0",
                                                    "avgPrice": "0.0000",
                                                    "cumQuote": "0",
                                                    "stopPrice": "9.5000",
                                                    "profit": "",
                                                    "commission": "",
                                                    "status": "NEW",
                                                    "time": 1669776326000,
                                                    "updateTime": 1669776326000
                                                }
                                                ],
                                                "failed": null
                                            }
                                            }


            """

            time_stamp=int(time.time() * 10 ** 3) 


            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        'symbol'    :   symbol
                        
                    
                    }
            
            return self.xbingx_request(url_cancelall_order, data, self.API_key, self.Secrect_Key,infoDelete) 



        def getpositions(self,symbol):
            """Parametros:
            --------------
                            symbol:	string	No	Trading pair, for example: BTC-USDT, please use capital letters
            Retorno:
            --------

                            Um dicionario:
                                           >>> {
                                                "code": 0,
                                                    "msg": "",
                                                    "data": [
                                                    {
                                                        "symbol": "BTC-USDT",
                                                        "positionId": "12345678",
                                                        "positionSide": "LONG",
                                                        "isolated": true,
                                                        "positionAmt": "123.33",
                                                        "availableAmt": "128.99",
                                                        "unrealizedProfit": "1.22",
                                                        "realisedProfit": "8.1",
                                                        "initialMargin": "123.33",
                                                        "avgPrice": "2.2",
                                                        "leverage": 10,
                                                    }
                                                ]
                                            }
            """
            
            time_stamp=int(time.time() * 10 ** 3) 
            
            data={
                    "timestamp": time_stamp,
                    'recvWindow':   15000,
                    'symbol':symbol
                }
            return self.xbingx_request(url_getpositions, data,self.API_key, self.Secrect_Key,infoGet) 
            
        
        def get_all_contracts(self):
            time_stamp=int(time.time() * 10 ** 3) 


            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        
                }
            
            return self.xbingx_request(url_all_contrats, data, self.API_key, self.Secrect_Key,infoGet) 
            

        def xbingx_request(self,uri_path, data, api_key, api_sec,info):

        
            req=''
            headers = {}
            headers['X-BX-APIKEY'] = api_key
            signature = self.get_xbingx_signature(data, api_sec)
        
            params={
                    **data, 
                    "signature": signature
                    }
            
            if info=="GET":
                req = requests.get((api_url + uri_path), params=params, headers=headers)
                return req.json()

            elif info=='DELETE':
                req = requests.delete((api_url + uri_path), headers=headers, params=params)
                return req.json()


            elif info=='POST':

                req = requests.post((api_url + uri_path), headers=headers, data=params)
                return req.json()
               

        def get_xbingx_signature(self,data, secret):
            postdata = urllib.parse.urlencode(data)
            message = postdata.encode()
            byte_key = bytes(secret, 'UTF-8')
            mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
            return mac

