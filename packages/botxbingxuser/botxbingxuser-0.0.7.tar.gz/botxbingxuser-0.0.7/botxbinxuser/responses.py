
from enum import Enum

class ParametrosGetPosition(Enum):

    symbol          =   1
    positionId      =   2
    positionSide    =   3
    isolated        =   4
    positionAmt     =   5
    availableAmt    =   6
    unrealizedProfit=   7
    realisedProfit  =   8
    initialMargin   =   9
    avgPrice        =   10
    leverage        =   11

    
class ParametrosGetBalance(Enum):

    asset               =   1
    balance             =   2
    equity              =   3
    unrealizedProfit    =   4
    realisedProfit      =   5
    availableMargin     =   6
    usedMargin          =   7
    freezedMargin       =   8

    
class ParametrosGetNewOrder(Enum):
    
    code                =   0
    msg                 =   1
    data                =   2
    order               =   3
    symbol              =   4
    orderId             =   5   
    side                =   6
    positionSide        =   7
    type                =   8
   

def negativa(response):
    return f'Não foi obtida a resposta: {response}'



def response_position(response:dict):
    if response['code']==0:
        return list(response['data'])
    else:
        return negativa(response=response)
            



def response_balance(response:dict):
    if response['code']==0:
        return dict(response['data']['balance'])
    else:
        return negativa(response=response)



def response_neworder(response:dict):
    if response['code']==0:
        return dict(response['data']['order'])
    else:
        return negativa(response=response)    



def response_cancellorder(response:dict):
    if response['code']==0:
        return dict(response['data'])
    else:
        return negativa(response=response)
    


def response_closeorders(response:dict):
    if response['code']==0:
        return response['data']['orders']

    else:
        return negativa(response=response)
    
def response_openorder(response:dict):
    if response['code']==0:
        return response['data']['orders']
    else:
        return negativa(response=response)