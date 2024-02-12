import json
import os
import info_functions

#funcion para calcular el tamaño de la operacion de la nueva moneda
def new_size(client, symbol, volume):
    volume = (info_functions.get_availableBalance_usdt(client) * (volume/100)) * 10
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = info_functions.get_qty_precision(client, symbol)
    return round(volume/price, qty_precision)

#funcion para conocer la informacion de la moneda
def info(save_path, symbol):
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
def modify(client, save_path, symbol, mod):
    if mod == 'stop_market_per':
        print("enter the new value for the PERCENTAGE STOP MARKET")
    elif mod == 'trailing_stop_per':
        print("enter the new value for the PERCENTAGE TRAILING STOP")
    elif mod == 'size':
        print("enter the new value for the main SIZE")    
    while True:
        if mod == 'size':
            qty_precision = info_functions.get_qty_precision(client, symbol)
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
def delete(save_path, symbol):
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