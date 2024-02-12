from dotenv import load_dotenv
import info_functions
import coin_functions
import bot_functions
import json
import os
from binance.um_futures import UMFutures
from time import sleep

load_dotenv()
client = UMFutures(key=os.getenv('api'), secret=os.getenv('secret'))
save_path = "save.json"

#funcion para agregar una nueva moneda
def new_coin():
    print("********new coin********")
    print()
    c = False
    while c == False:
        symbol = input("write the name of the coin --> ").upper()
        if os.path.exists(save_path):
            c = info_functions.find_saved_coin(save_path, symbol)     
            if c == False:
                print()
                print("The coin that you are trying to add is already listed, please add a new coin")
                print()
                new_coin()               
        for i in info_functions.get_tickers_usdt(client):   
            if symbol == i:
                c = True
                break
        if c == False:
            print()
            print("we couldn't find any coin with that name, make sure to write it right or try another coin")
            print()
    print()
    while True:
        try:
            volume = float(input("write the available size percentage for the first LONG position --> "))
            if volume > 0 and volume <= 100:
                break
            else:
                print()
                print("you must put a value greater than 0 and smaller or equal to 100")
                print()

        except ValueError:
            print()
            print("you must enter a number")
            print()

    print()
    size = coin_functions.new_size(client, symbol, volume)
    while True:
        try:
            percentage_stop_market = float(input("write the percentage that will be used to place the stop market orders --> "))/100
            if percentage_stop_market > 0:
                break
            else:
                print()
                print("you must put a value greater than 0")
                print()

        except ValueError:
            print()
            print("you must enter a number")
            print()

    print()
    percentage_trailing_stop_callback = percentage_stop_market * 2
    while True:
        try:
            percentage_trailing_stop = float(input("write the percentage that will be used to place the trailing stop orders --> "))/100
            if percentage_trailing_stop > 0:
                break
            else:
                print()
                print("you must put a value greater than 0")
                print()

        except ValueError:
            print()
            print("you must enter a number")
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
    info_functions.add_new_dict_json(save_path, coin)
    print("the coin has been added successfully!")
    print()
    sleep(1)
    os.system('cls')
    choose_option()

#funcion menu para modificar una moneda
def coin_option_menu():
    print("********Coin options********")
    print()
    c = True
    while c == True:
        symbol = input("write the name of the coin to modify --> ").upper()
        c = info_functions.find_saved_coin(save_path, symbol)
        if c == True:
            print()
            print("The coin that you are looking for is not on the list, try again or use another coin")
            print()
            coin_option_menu()

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
        coin_functions.info(save_path, symbol)
    elif option == 2:
        coin_functions.modify(client, save_path, symbol, "stop_market_per")
    elif option == 3:
        coin_functions.modify(client, save_path, symbol, "trailing_stop_per")
    elif option == 4:
        coin_functions.modify(client, save_path, symbol, "size")
    elif option == 5:
        coin_functions.delete(client, save_path, symbol)
    os.system("cls")
    choose_option()        

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
                print("bebop... working coin --> ", i['symbol'])    

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
        try:
            option = int(input())
            print()
            if option >= 1 and option <= 3:
                break
            else:
                print("please choose a valid option")
                print()

        except ValueError:
            print()
            print("you must enter a full number")
            print()

    os.system('cls')
    if option == 1:
        new_coin()
    elif option == 2:
        coin_option_menu()
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