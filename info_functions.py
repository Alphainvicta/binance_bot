from binance.error import ClientError
import pandas as pd
import json
import os

#funcion para dar el balance de usdt del usuario
def get_balance_usdt(client):
    try:
        response = client.balance(recvWindow=6000)
        for i in response:
            if i['asset'] == 'USDT':
                return float(i['balance'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para dar el disponible de usdt del usuario
def get_availableBalance_usdt(client):
    try:
        response = client.balance(recvWindow=6000)
        for i in response:
            if i['asset'] == 'USDT':
                return float(i['availableBalance'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )      

#funcion para dar la lista de monedas donde hacer trading es posible con usdt
def get_tickers_usdt(client):
    tickers = []
    resp = client.ticker_price()
    for i in resp:
        if 'USDT' in i['symbol']:
            tickers.append(i['symbol'])
    return tickers

#funcion de la informacion de las ultimas 500 velas
def get_klines(client, symbol, time):
    try:
        resp = pd.DataFrame(client.klines(symbol, time))
        resp = resp.iloc[:,:6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para obtener los decimales del precio con precision
def get_price_precision(client, symbol):
    resp = client.exchange_info()['symbols']
    for i in resp:
        if i['symbol'] == symbol:
            return i['pricePrecision']        

#funcion para obtener los decimales de la cantidad con precision        
def get_qty_precision(client, symbol):
    resp = client.exchange_info()['symbols']
    for i in resp:
        if i['symbol'] == symbol:
            return i['quantityPrecision']  
        
#funcion para buscar una moneda en la lista json
def find_saved_coin(save_path, symbol):
    with open(save_path) as json_file:
        data = json.load(json_file)
        for i in data:
            if i['symbol'] == symbol:
                return False
        return True
    
#funcion para agregar datos al archivo json
def add_new_dict_json(save_path, dict):
    data = []
    if os.path.exists(save_path):
        with open(save_path) as json_file:
            helper =  json.load(json_file)
            for i in helper:
                data.append(i) 
            data.append(dict)
    else:
        data.append(dict)
    with open(save_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

#funcion para checar operaciones abiertas en la moneda
def get_coin_position_checker(client, save_path, coin, data):
    helper = client.get_position_risk(symbol=coin['symbol'])
    for h in helper:
        if float(h['positionAmt']) == 0 and h['positionSide'] == 'LONG':
            coin['long_open_position'] = False
        elif float(h['positionAmt']) > 0 and h['positionSide'] == 'LONG':
            coin['long_open_position'] = True
        if float(h['positionAmt']) == 0 and h['positionSide'] == 'SHORT':
            coin['short_open_position'] = False
        elif float(h['positionAmt']) < 0 and h['positionSide'] == 'SHORT':
            coin['short_open_position'] = True
    with open(save_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  

#funcion para checar ordenes restantes de la moneda
def get_coin_order_checker(client, save_path, coin, data):
    helper = client.get_position_risk(symbol=coin['symbol'])
    for h in helper:
        if h['positionSide'] == 'LONG':
            if float(h['positionAmt']) > coin['size']:
                coin['stop_market_orders_long'] = 1 + int(((float(h['positionAmt']) - coin['size'])/coin['size'])*10)
            else:
                coin['stop_market_orders_long'] = 1
        if h['positionSide'] == 'SHORT':
            if float(h['positionAmt']) < 0:
                coin['stop_market_orders_short'] = 1 + int((coin['size'] / (float(h['positionAmt'])*-1))/10)
            elif float(h['positionAmt']) == 0:
                coin['stop_market_orders_short'] = 1
    with open(save_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)   

#funcion para obtener el precio de mercado
def get_market_price(client, symbol):
    try:
        response = client.mark_price(symbol)
        return float(response['markPrice'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        ) 

#funcion para obtener el precio de entrada
def get_entry_price(client, symbol, positionSide):
    try:
        entry_price = client.get_position_risk(symbol=symbol)
        for i in entry_price:
            if i['positionSide'] == positionSide:
                return float(i['entryPrice'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )   

#funcion para obtener el primer stop market en la moneda
def get_first_stop_market(client, coin, side, positionSide):
    try:
        position = client.get_all_orders(symbol=coin['symbol'])

        for j in position:
            if j['positionSide'] == positionSide and j['side'] == side and j['origType'] == 'STOP_MARKET' and j['status'] == 'NEW':
                return float(j['stopPrice'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para obtener el ultimo stop market en la moneda
def get_last_stop_market(client, coin, side, positionSide):
    try:
        position = client.get_all_orders(symbol=coin['symbol'])

        for j in reversed(position):
            if j['positionSide'] == positionSide and j['side'] == side and j['origType'] == 'STOP_MARKET' and j['status'] == 'NEW':
                return float(j['stopPrice'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )  

#funcion para obtener el tamaño actual de la operacion
def get_position_size(client, symbol, positionSide):
    try:
        positionAmt = client.get_position_risk(symbol=symbol)
        for i in positionAmt:
            if i['positionSide'] == positionSide:
                return float(i['positionAmt'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        ) 

#funcion para verificar si hay operaciones abiertas en la moneda
def get_open_order_count(client, coin, side, positionSide):
    try:
        orders = client.get_all_orders(symbol=coin['symbol'])
        helper = False
        for j in orders:
            if j['positionSide'] == positionSide and j['side'] == side and j['origType'] == 'STOP_MARKET' and j['status'] == 'NEW':
                helper = True
                return helper
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para retornar la cantidad de operaciones abiertas de una posicion
def get_open_order_length(client, coin, positionSide):
    try:
        orders = client.get_all_orders(symbol=coin['symbol'])
        helper = 0
        for j in orders:
            if j['positionSide'] == positionSide and j['status'] == 'NEW':
                helper += 1
        return helper
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para obtener el punto mas alto/bajo en un periodo de tiempo
def get_klane_end_points(client, coin, interval, side):
    result = []
    klist = client.klines(coin, interval)
    klist.reverse()
    if side == "HIGH":
        for i in range(2, len(klist) - 2):
            if klist[i][2] > klist[i-1][2] and klist[i][2] > klist[i-2][2] and klist[i][2] > klist[i+1][2] and klist[i][2] > klist[i+2][2]:
                result.append(klist[i])
    else:
        for i in range(2, len(klist) - 2):
            if klist[i][3] < klist[i-1][3] and klist[i][3] < klist[i-2][3] and klist[i][3] < klist[i+1][3] and klist[i][3] < klist[i+2][3]:
                result.append(klist[i])

    return result

#funcion para obtener emas
def get_ema(coin, time, leng):
    kl = get_klines(coin, time)
    kl['Ema'] = kl['Close'].ewm(span=leng).mean()
    return kl