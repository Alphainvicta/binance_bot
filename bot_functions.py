from binance.error import ClientError
import json
import info_functions

#funcion para abrir una nueva posicion en market
def bot_create_market_order(client, coin, side, positionSide, size):
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
def bot_open_stop_market_order(client, coin, side, positionSide, helper, entry, first = False):
    qty_precision = info_functions.get_qty_precision(client, coin['symbol'])
    price_precision = info_functions.get_price_precision(client, coin['symbol'])
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
            stop_price = round(info_functions.get_market_price(client, coin['symbol']) * helper, price_precision)
        else:
            stop_price = round(info_functions.get_market_price(client, coin['symbol']) / helper, price_precision)

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
def bot_open_trailing_stop_order(client, coin, side, positionSide, helper, entry = 'stop_market'):
    if entry == 'stop_market':
        if side == 'BUY':
            last_stop_market_position = info_functions.get_last_stop_market(client, coin, 'SELL', positionSide)
        else:
            last_stop_market_position = info_functions.get_last_stop_market(client, coin, 'BUY', positionSide)
    
    elif entry == 'entry':
        if side == 'BUY':
            last_stop_market_position = info_functions.get_entry_price(client, coin['symbol'], positionSide)
        else:
            last_stop_market_position = info_functions.get_entry_price(client, coin['symbol'], positionSide)
    
    elif entry == 'market_price':
        last_stop_market_position = info_functions.get_market_price(client, coin['symbol'])

    qty_precision = info_functions.get_qty_precision(coin['symbol'])
    price_precision = info_functions.get_price_precision(coin['symbol'])
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
def bot_cancel_order_list(client, coin, positionSide):
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

#funcion para cerrar todas las operaciones de la moneda
def bot_cancel_all_order_list(client, save_path, coin, data):
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