from keys import api, secret
import json
import os
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError

client = UMFutures(key=api, secret=secret)
save_path = "save.json"

#funcion para dar el balance de usdt del usuario
def get_balance_usdt():
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
def get_availableBalance_usdt():
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
def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for i in resp:
        if 'USDT' in i['symbol']:
            tickers.append(i['symbol'])
    return tickers

#funcion de la informacion de las ultimas 500 velas
def klines(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, '1h'))
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
def get_price_precision(symbol):
    resp = client.exchange_info()['symbols']
    for i in resp:
        if i['symbol'] == symbol:
            return i['pricePrecision']        

#funcion para obtener los decimales de la cantidad con precision        
def get_qty_precision(symbol):
    resp = client.exchange_info()['symbols']
    for i in resp:
        if i['symbol'] == symbol:
            return i['quantityPrecision']  

#funcion para calcular el tamaño de la operacion de la nueva moneda
def new_coin_size(symbol, volume):
    volume = (get_availableBalance_usdt() * (volume/100)) * 10
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = get_qty_precision(symbol)
    return round(volume/price, qty_precision)

#funcion para buscar una moneda en la lista json
def find_saved_coin(symbol):
    with open(save_path) as json_file:
        data = json.load(json_file)
        for i in data:
            if i['symbol'] == symbol:
                return False
        return True

#funcion para agregar datos al archivo json
def add_new_dict_json(dict):
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

#funcion para agregar una nueva moneda
def new_coin():
    print("********new coin********")
    print()
    c = False
    while c == False:
        symbol = input("write the name of the coin --> ").upper()
        if os.path.exists(save_path):
            c = find_saved_coin(symbol)     
            if c == False:
                print()
                print("The coin that you are trying to add is already listed, please add a new coin")
                print()
                new_coin()               
        for i in get_tickers_usdt():   
            if symbol == i:
                c = True
                break
        if c == False:
            print()
            print("we couldn't find any coin with that name, make sure to write it right or try another coin")
            print()
    print()
    while True:
        volume = float(input("write the available size percentage for the first LONG position --> "))
        if volume > 0 and volume <= 100:
            break
        else:
            print()
            print("you must put a value greater than 0 and smaller or equal to 100")
            print()
    print()
    size = new_coin_size(symbol, volume)
    while True:
        percentage_stop_market = float(input("write the percentage that will be used to place the stop market orders --> "))/100
        if percentage_stop_market > 0:
            break
        else:
            print()
            print("you must put a value greater than 0")
            print()
    print()
    percentage_trailing_stop_callback = percentage_stop_market * 2
    while True:
        percentage_trailing_stop = float(input("write the percentage that will be used to place the trailing stop orders --> "))/100
        if percentage_trailing_stop > 0:
            break
        else:
            print()
            print("you must put a value greater than 0")
            print()
    print()
    coin = {"symbol": symbol, 
            "size": size, 
            "stop_market_per": percentage_stop_market, 
            "trailing_stop_per": percentage_trailing_stop,
            "trailing_stop_callback_per": percentage_trailing_stop_callback,
            "long_open_position": False, 
            "short_open_position": False, 
            "stop_market_orders_long": 0, 
            "trailing_stop_orders_long": False,
            "stop_market_orders_short": 0, 
            "trailing_stop_orders_short": False}
    add_new_dict_json(coin)
    print("the coin has been added successfully!")
    print()
    sleep(1)
    os.system('cls')
    choose_option()

#funcion para conocer la informacion de la moneda
def coin_info(symbol):
    print("these are the coin details")
    print()
    with open(save_path) as json_file:
        data = json.load(json_file)
        for i in data:
            if i['symbol'] == symbol:
                for key, value in i.items():
                    print(f"{key}: {value}")
    print()
    os.system("pause")

#funcion para modificar un valor de la moneda
def modify_coin(symbol, mod):
    if mod == 'stop_market_per':
        print("enter the new value for the PERCENTAGE STOP MARKET")
    elif mod == 'trailing_stop_per':
        print("enter the new value for the PERCENTAGE TRAILING STOP")
    elif mod == 'size':
        print("enter the new value for the main SIZE")    
    while True:
        if mod == 'size':
            qty_precision = get_qty_precision(symbol)
            helper = round(float(input("--> ")), qty_precision)
        else:
            helper = float(input("--> "))/100
        if helper > 0:
            break
        else:
            print()
            print("you must put a value greater than 0")
            print()
    print()
    with open(save_path) as json_file:
        data = json.load(json_file)
        for i in data:
            if i['symbol'] == symbol:
                i[mod] = helper
                break
    with open(save_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("the", mod, "has been modified successfully!")
    print()
    os.system("pause")

#funcion para eliminar monedas
def delete_coin(symbol):
    print("do you want to delete ", symbol, "coin?")
    print()
    while True:
        confirm = input("y: yes, n: no --> ").lower()
        if confirm == "y" or confirm == "n":
            break
        else:
            print()
            print("please choose a valid option")
            print()
    print()
    with open(save_path) as json_file:
        data = json.load(json_file)
        j = 0
        for i in data:
            if i['symbol'] == symbol:
                data.pop(j)
                break
            j+=1
    with open(save_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("the coin ", symbol, "has been removed successfully!")
    print()
    os.system("pause")


#funcion para modificar una moneda
def coin_option():
    print("********Coin options********")
    print()
    c = True
    while c == True:
        symbol = input("write the name of the coin to modify --> ").upper()
        c = find_saved_coin(symbol)
        if c == True:
            print()
            print("The coin that you are looking for is not on the list, try again or use another coin")
            print()
            coin_option()

    print()
    print("select one option from below")
    print("________________________________________________________")
    print()
    print("1: coin information, 2: change stop market percentage, 3: change trailing stop percentage, 4: change coin size, 5: delete coin")
    print("________________________________________________________")
    print()
    while True:
        option = int(input())
        if option >= 1 and option <= 5:
            break
        else:
            print()
            print("please choose a valid option")
            print()
    print()
    if option == 1:
        coin_info(symbol)
    elif option == 2:
        modify_coin(symbol, "stop_market_per")
    elif option == 3:
        modify_coin(symbol, "trailing_stop_per")
    elif option == 4:
        modify_coin(symbol, "size")
    elif option == 5:
        delete_coin(symbol)
    os.system("cls")
    choose_option()


#funcion para checar operaciones abiertas en la moneda
def bot_coin_position_checker(coin, data):
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

#funcion para checar ordenes restantes
def bot_coin_order_checker(coin, data):
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

#funcion para abrir una nueva posicion en market
def bot_create_market_order(coin, side, positionSide, size):
    try:
        client.new_order(symbol=coin['symbol'], side=side, positionSide=positionSide, type='MARKET', quantity=size)
        print(positionSide, "position created successfully!")
        print()
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para abrir una orden de market stop
def bot_open_stop_market_order(coin, side, positionSide, helper, entry, first = False):
    qty_precision = get_qty_precision(coin['symbol'])
    price_precision = get_price_precision(coin['symbol'])
    if first == True:
        size = coin['size']
    else:
        size = round(coin['size']/10, qty_precision)
    if entry == 'position':
        entry_price = client.get_position_risk(symbol=coin['symbol'])
        for i in entry_price:
            if i['positionSide'] == positionSide:
                if side == 'BUY':
                    stop_price = round(float(i['entryPrice']) * helper, price_precision)
                else:
                    stop_price = round(float(i['entryPrice']) / helper, price_precision)
    else:
        if side == 'BUY':
            stop_price = round(bot_market_price(coin['symbol']) * helper, price_precision)
        else:
            stop_price = round(bot_market_price(coin['symbol']) / helper, price_precision)

    try:
        client.new_order(symbol=coin['symbol'], side=side, positionSide=positionSide, type='STOP_MARKET', quantity=size, stopPrice=stop_price)
        print(positionSide, "stop market order created successfully!")
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para abrir una orden de trailing stop
def bot_open_trailing_stop_order(coin, side, positionSide, helper, entry = 'stop_market'):
    if entry == 'stop_market':
        if side == 'BUY':
            last_stop_market_position = bot_last_stop_market(coin, 'SELL', positionSide)
        else:
            last_stop_market_position = bot_last_stop_market(coin, 'BUY', positionSide)
    
    elif entry == 'entry':
        if side == 'BUY':
            last_stop_market_position = bot_entry_price(coin['symbol'], positionSide)
        else:
            last_stop_market_position = bot_entry_price(coin['symbol'], positionSide)
    
    elif entry == 'market_price':
        last_stop_market_position = bot_market_price(coin['symbol'], positionSide)

    qty_precision = get_qty_precision(coin['symbol'])
    price_precision = get_price_precision(coin['symbol'])
    if positionSide == 'LONG':
        size = round(coin['size'] * 1.5, qty_precision)
    else:
        size = round(coin['size'] / 2, qty_precision)

    if side == 'BUY':
        activation_price = round(last_stop_market_position / helper, price_precision)
    else:
        activation_price = round(last_stop_market_position * helper, price_precision)

    try:
        client.new_order(symbol=coin['symbol'], side=side, positionSide=positionSide, type='TRAILING_STOP_MARKET', quantity=size, activationPrice=activation_price, callbackRate=coin['trailing_stop_callback_per']*100)
        print(positionSide, "trailing stop order created successfully!")
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para cancelar ordenes abiertas seleccionadas
def bot_cancel_order_list(coin, positionSide):
    try:
        position = client.get_all_orders(symbol=coin['symbol'])
        for i in reversed(position):
            if i['positionSide'] == positionSide and i['status'] == 'NEW':
                client.cancel_order(symbol=coin['symbol'], orderId=i['orderId'])
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        ) 

#funcion para obtener el precio de mercado
def bot_market_price(symbol):
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
def bot_entry_price(symbol, positionSide):
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

#funcion para obtener el primer stop market
def bot_first_stop_market(coin, side, positionSide):
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

#funcion para obtener el ultimo stop market
def bot_last_stop_market(coin, side, positionSide):
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
def bot_get_size_position(symbol, positionSide):
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
def bot_open_order_count(coin, side, positionSide):
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

#funcion para cerrar todas las operaciones de la moneda
def bot_cancel_all_order_list(coin, data):
    try:
        client.cancel_open_orders(coin['symbol'])
        coin['stop_market_orders_short'] = 0
        coin['trailing_stop_orders_short'] = False
        coin['stop_market_orders_long'] = 0
        coin['trailing_stop_orders_long'] = False
        with open(save_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message {}".format(
                error.status_code, error.error_code, error.error_message                     
            )
        )

#funcion para retornar la cantidad de operaciones abiertas de una posicion
def bot_open_order_length(coin, positionSide):
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


#funcion principal del bot
def bot_main_loop():
    print("remember, you can stop the bot by presing ctrl + c")
    print()
    os.system("pause")
    os.system("cls")
    with open(save_path) as json_file:
        data = json.load(json_file)
    try:
        while True:
            for i in data:
                qty_precision = get_qty_precision(i['symbol'])
                print("checking all positions at --> ", i['symbol'])
                print()
                bot_coin_position_checker(i, data)
                print("checking all orders at --> ", i['symbol'])
                print()
                bot_coin_order_checker(i, data)

                if i['long_open_position'] == False and i['short_open_position'] == False:
                    ########################  1.1  #########################
                    print("closing all open orders remaining on the coin")
                    print()
                    bot_cancel_all_order_list(i, data)
                    ########################  1.2  #########################
                    print("opening new LONG position at --> ", i['symbol'])
                    print()
                    bot_create_market_order(i, 'BUY', 'LONG', i['size'])
                    i['long_open_position'] = True
                    with open(save_path, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    ########################  1.3  #########################
                    print("adding all the LONG stop markets at --> ", i['symbol'])
                    print()
                    count = i['stop_market_orders_long']
                    multiply_by = 1
                    while count <= 5:
                        bot_open_stop_market_order(i, 'BUY', 'LONG', 1+(i['stop_market_per']*multiply_by), 'position')
                        print()
                        count += 1
                        multiply_by += 1
                    ########################  1.4  #########################
                    print("adding all the SHORT stop markets at --> ", i['symbol'])
                    print()
                    count = i['stop_market_orders_short']
                    multiply_by = 1
                    while count <= 5:
                        bot_open_stop_market_order(i, 'SELL', 'SHORT', 1+(i['stop_market_per']*multiply_by), 'position')
                        print()
                        count += 1
                        multiply_by += 1
                    ########################  1.5  #########################
                    print("adding LONG trailing stop at --> ", i['symbol'])
                    print()
                    bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'])
                    i['trailing_stop_orders_long'] = True
                    with open(save_path, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    ########################  1.6  #########################
                    print("adding SHORT trailing stop at --> ", i['symbol'])
                    print()
                    bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                    i['trailing_stop_orders_short'] = True
                    with open(save_path, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                
                elif i['long_open_position'] == True and i['short_open_position'] == False:
                    ########################  2.1  #########################
                    if bot_open_order_count(i, 'SELL', 'SHORT') == True:
                        ########################  2.1.1  #########################
                        difference = bot_market_price(i['symbol']) / (1+(i['stop_market_per']*2)) 
                        if difference > bot_first_stop_market(i, 'SELL', 'SHORT'):
                            ########################  2.1.1.1  #########################
                            print("canceling all SHORT open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'SHORT')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'SHORT')
                            i['trailing_stop_orders_short'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  2.1.1.2  #########################
                            print("adding all the SHORT stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_short']
                            multiply_by = 1
                            while count <= 5:
                                bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  2.1.1.3  #########################
                            print("adding SHORT trailing stop at --> ", i['symbol'])
                            print()
                            bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    ########################  2.2  #########################
                    else:
                        ########################  2.2.1  #########################
                        print("adding all the SHORT stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_short']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  2.2.2  #########################    
                        print("adding SHORT trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_short'] == 5:
                            if bot_market_price(i['symbol']) < bot_entry_price(i['symbol'], 'SHORT'):
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                    ########################  2.3  #########################
                    if i['stop_market_orders_long'] == 5:
                        ########################  2.3.2.1  #########################
                        safe_spot = bot_entry_price(i['symbol'], 'LONG') * 1+i['stop_market_per']
                        if bot_market_price(i['symbol']) > bot_entry_price(i['symbol'], 'LONG') and bot_market_price(i['symbol']) < safe_spot:
                            ########################  2.3.2.1.1  #########################
                            print("emergency CLOSE for a LONG position at --> ", i['symbol'])
                            bot_create_market_order(i, 'SELL', 'LONG', round(i['size']*1.5, qty_precision))
                    ########################  2.4  #########################
                    if bot_open_order_count(i, 'BUY', 'LONG') == True:
                        ########################  2.4.1  #########################
                        difference = bot_market_price(i['symbol']) * (1+(i['stop_market_per']*2))
                        if difference < bot_first_stop_market(i, 'BUY', 'LONG'):
                            ########################  2.4.1.1  #########################
                            print("canceling all LONG open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'LONG')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'LONG')
                            i['trailing_stop_orders_long'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  2.4.1.2  #########################
                            print("adding all the LONG stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_long']
                            multiply_by = 1
                            while count <= 5:
                                bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  2.4.1.3  #########################    
                            print("adding LONG trailing stop at --> ", i['symbol'])
                            print()
                            if bot_last_stop_market(i, 'BUY', 'LONG') > bot_entry_price(i['symbol'], 'LONG'):
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'])
                            else:
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    else:
                        ########################  2.4.2  #########################
                        print("adding all the LONG stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_long']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  2.4.3  #########################    
                        print("adding LONG trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_long'] == '5':
                            if bot_last_stop_market(i, 'BUY', 'LONG') > bot_entry_price(i['symbol'], 'LONG'):
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4) 

                elif i['long_open_position'] == False and i['short_open_position'] == True: 
                    ########################  3.1  #########################
                    if bot_open_order_count(i, 'BUY', 'LONG') == True:
                        ########################  3.1.1  #########################
                        difference = bot_market_price(i['symbol']) * (1+(i['stop_market_per']*2))
                        if difference < bot_first_stop_market(i, 'BUY', 'LONG'):
                            ########################  3.1.1.1  #########################
                            print("canceling all LONG open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'LONG')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'LONG')
                            i['trailing_stop_orders_short'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  3.1.1.2  #########################
                            print("adding all the LONG stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_long']
                            multiply_by = 1
                            while count <= 5:
                                if count == 1:
                                    bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark', True)
                                else:
                                    bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  3.1.1.3  #########################    
                            print("adding LONG trailing stop at --> ", i['symbol'])
                            print()
                            bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    ########################  3.2  #########################
                    else:
                        ########################  3.2.1  #########################
                        print("adding all the LONG stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_long']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  3.2.2  #########################    
                        print("adding LONG trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_long'] == '5':
                            if bot_last_stop_market(i, 'BUY', 'LONG') > bot_entry_price(i['symbol'], 'LONG'):
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                    ########################  3.3  #########################
                    if i['stop_market_orders_short'] == 5:
                        ########################  3.3.2.1  #########################
                        safe_spot = bot_entry_price(i['symbol'], 'SHORT') / 1+i['stop_market_per']
                        if bot_market_price(i['symbol']) < bot_entry_price(i['symbol'], 'SHORT') and bot_market_price(i['symbol']) > safe_spot:
                            ########################  3.3.2.1.1  #########################
                            print("emergency CLOSE for a SHORT position at --> ", i['symbol'])
                            bot_create_market_order(i, 'BUY', 'SHORT', round(i['size']/2, qty_precision))        
                    ########################  3.4  #########################
                    if bot_open_order_count(i, 'SELL', 'SHORT') == True:
                        ########################  3.4.1  #########################
                        difference = bot_market_price(i['symbol']) / (1+(i['stop_market_per']*2)) 
                        if difference > bot_first_stop_market(i, 'SELL', 'SHORT'):
                            ########################  3.4.1.1  #########################
                            print("canceling all SHORT open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'SHORT')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'SHORT')
                            i['trailing_stop_orders_short'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  3.4.1.2  #########################
                            print("adding all the SHORT stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_short']
                            multiply_by = 1
                            while count <= 5:
                                bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  3.4.1.3  #########################    
                            print("adding SHORT trailing stop at --> ", i['symbol'])
                            print()
                            print()
                            if bot_last_stop_market(i, 'SELL', 'SHORT') < bot_entry_price(i['symbol'], 'SHORT'):
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                            else:
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'entry')
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    else:
                        ########################  3.4.2  #########################
                        print("adding all the SHORT stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_short']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  3.4.3  #########################    
                        print("adding SHORT trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_short'] == 5:
                            if bot_market_price(i['symbol']) < bot_entry_price(i['symbol'], 'SHORT'):
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                
                elif i['long_open_position'] == True and i['short_open_position'] == True:
                    ########################  4.1  #########################
                    if i['stop_market_orders_long'] == 5:
                        ########################  4.1.2.1  #########################
                        safe_spot = bot_entry_price(i['symbol'], 'LONG') * 1+i['stop_market_per']
                        if bot_market_price(i['symbol']) > bot_entry_price(i['symbol'], 'LONG') and bot_market_price(i['symbol']) < safe_spot:
                            ########################  4.1.2.1.1  #########################
                            print("emergency CLOSE for a LONG position at --> ", i['symbol'])
                            bot_create_market_order(i, 'SELL', 'LONG', round(i['size']*1.5, qty_precision))
                    ########################  4.2  #########################
                    if bot_open_order_count(i, 'BUY', 'LONG') == True:
                        ########################  4.2.1  #########################
                        difference = bot_market_price(i['symbol']) * (1+(i['stop_market_per']*2))
                        if difference < bot_first_stop_market(i, 'BUY', 'LONG'):
                            ########################  4.2.1.1  #########################
                            print("canceling all LONG open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'LONG')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'LONG')
                            i['trailing_stop_orders_long'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  4.2.1.2  #########################
                            print("adding all the LONG stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_long']
                            multiply_by = 1
                            while count <= 5:
                                bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  4.2.1.3  #########################    
                            print("adding LONG trailing stop at --> ", i['symbol'])
                            print()
                            if bot_last_stop_market(i, 'BUY', 'LONG') > bot_entry_price(i['symbol'], 'LONG'):
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    else:
                        ########################  4.2.2  #########################
                        print("adding all the LONG stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_long']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'BUY', 'LONG', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  4.2.3  #########################    
                        print("adding LONG trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_long'] == '5':
                            if bot_last_stop_market(i, 'BUY', 'LONG') > bot_entry_price(i['symbol'], 'LONG'):
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'SELL', 'LONG', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                    ########################  4.3  #########################
                    if i['stop_market_orders_short'] == 5:
                        ########################  4.3.2.1  #########################
                        safe_spot = bot_entry_price(i['symbol'], 'SHORT') / 1+i['stop_market_per']
                        if bot_market_price(i['symbol']) < bot_entry_price(i['symbol'], 'SHORT') and bot_market_price(i['symbol']) > safe_spot:
                            ########################  4.3.2.1.1  #########################
                            print("emergency CLOSE for a SHORT position at --> ", i['symbol'])
                            bot_create_market_order(i, 'BUY', 'SHORT', round(i['size']/2, qty_precision))  
                    ########################  4.4  #########################
                    if bot_open_order_count(i, 'SELL', 'SHORT') == True:
                        ########################  4.4.1  #########################
                        difference = bot_market_price(i['symbol']) / (1+(i['stop_market_per']*2)) 
                        if difference > bot_first_stop_market(i, 'SELL', 'SHORT'):
                            ########################  4.4.1.1  #########################
                            print("canceling all SHORT open orders at --> ", i['symbol'])
                            print()
                            c = bot_open_order_length(i, 'SHORT')
                            for orders in range(c):
                                bot_cancel_order_list(i, 'SHORT')
                            i['trailing_stop_orders_short'] = False
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            ########################  4.4.1.2  #########################
                            print("adding all the SHORT stop markets at --> ", i['symbol'])
                            print()
                            count = i['stop_market_orders_short']
                            multiply_by = 1
                            while count <= 5:
                                bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                                print()
                                count += 1
                                multiply_by += 1
                            ########################  4.4.1.3  #########################    
                            print("adding SHORT trailing stop at --> ", i['symbol'])
                            print()
                            if bot_last_stop_market(i, 'SELL', 'SHORT') < bot_entry_price(i['symbol'], 'SHORT'):
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                            else:
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'entry')
                            i['trailing_stop_orders_short'] = True
                            with open(save_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                    else:
                        ########################  4.4.2  #########################
                        print("adding all the SHORT stop markets at --> ", i['symbol'])
                        print()
                        count = i['stop_market_orders_short']
                        multiply_by = 1
                        while count <= 5:
                            bot_open_stop_market_order(i, 'SELL', 'SHORT', (1+(i['stop_market_per']*2)*multiply_by), 'mark')
                            print()
                            count += 1
                            multiply_by += 1
                        ########################  4.4.3  #########################    
                        print("adding SHORT trailing stop at --> ", i['symbol'])
                        print()
                        if i['stop_market_orders_short'] == 5:
                            if bot_market_price(i['symbol']) < bot_entry_price(i['symbol'], 'SHORT'):
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'market')
                            else:
                                bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'], 'entry')
                        else:
                            bot_open_trailing_stop_order(i, 'BUY', 'SHORT', 1+i['trailing_stop_per'])
                        i['trailing_stop_orders_short'] = True
                        with open(save_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)

            print()
            print('waiting 1 minute...')
            print()
            sleep(60)    

    except KeyboardInterrupt:
        with open(save_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print()
        print("Key pressed. The bot is shut down")
        print()
        sleep(1)
        os.system("cls")
        choose_option()        

#funcion para elegir opciones
def choose_option():
    with open(save_path) as json_file:
        data = json.load(json_file)
    if not data:
        print("due to have 0 coins remaining on the list you must add at least one to continue")
        print()
        os.system("pause")
        os.system("cls")
        new_coin()

    print("Select one option from below")
    print("________________________________________________________")
    print()
    print("1: add new coin, 2: modify coin, 3: start bot")
    print("________________________________________________________")
    print()

    while True:
        option = int(input())
        if option >= 1 and option <= 3:
            break
        else:
            print()
            print("please choose a valid option")
            print()
    os.system('cls')
    if option == 1:
        new_coin()
    elif option == 2:
        coin_option()
    elif option == 3:
        bot_main_loop()
    
def main():
    if os.path.exists(save_path):
        print("welcome back!")
        print()
    
    else:
        print("welcome!")
        print()
        print("Lets add a coin to begin!")
        print()
        new_coin()
    
    choose_option()       

if __name__ == "__main__":
    os.system('cls')
    main()