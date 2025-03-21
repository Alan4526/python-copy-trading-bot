import MetaTrader5 as mt5
import time
import os
import json
from datetime import datetime as dt

# Clear screen and set title
os.system('cls')
os.system('title CopyTrading')

# Account credentials
file_path = "accounts.json"
default_data = {
    "master": {
        "login": "YOUR_LOGIN",
        "password": "YOUR_PASSWORD",
        "server": "YOUR_SERVER"
    },
    "slaves": [
        {
            "login": "YOUR_LOGIN",
            "password": "YOUR_PASSWORD",
            "server": "YOUR_SERVER"
        }
    ]
}

def log_status(msg):
    now_ = dt.now()
    current_time = now_.strftime("%Y-%m-%d %H:%M:%S:%MS")
    print(str(current_time) + " - " + str(msg))

if not os.path.exists(file_path):
    with open(file_path, 'w') as json_file:
        json.dump(default_data, json_file, indent=4)
    log_status(f"{file_path} created.\nPlease enter the accounts' credentials!")
    time.sleep(20)
else:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    log_status(f"Data loaded from {file_path}")

master = data["master"]
slaves = data["slaves"]

# Login to MetaTrader 5 account
def login_to_mt5_account(account):
    if not mt5.initialize():
        log_status(f"initialize() failed, error code: {mt5.last_error()}")
        return False
    if not mt5.login(account['login'], account['password'], account['server']):
        log_status(f"Failed to connect to account {account['login']}")
        return False
    log_status(f"Connected to account {account['login']}")
    return True

# Monitor trades on master account and copy to all slaves
def monitor_trades(master):
    
    # Login to the master account
    if not login_to_mt5_account(master):
        return

    # Get initial trades and store their IDs
    initial_trades_master = mt5.positions_get()
    initial_trade_ids_master = {trade.ticket for trade in initial_trades_master}

    # Dictionary to keep track of copied trades (master ID -> slave ID -> copied trade ID)
    copied_trades = {slave['login']: {} for slave in slaves}


    while True:
        if master['login'] != mt5.account_info().login:
            if not login_to_mt5_account(master):
                return
        current_trades_master = mt5.positions_get()
        current_trade_ids_master = {trade.ticket for trade in current_trades_master}

        # Determine new trades by removing initial trades from the current trades
        new_trade_ids = current_trade_ids_master - initial_trade_ids_master

        # Iterate through new trades and check conditions
        for trade_id in new_trade_ids:
            trade = next((trade for trade in current_trades_master if trade.ticket == trade_id), None)
            if trade:
                for slave in slaves:
                    # if trade_id not in copied_trades[slave['login']] and trade.sl != 0 and trade.tp != 0:
                    if trade_id not in copied_trades[slave['login']]:
                        if not login_to_mt5_account(slave):
                            return
                        copied_trade_id = copy_trade_to_slave(trade, slave)
                        if copied_trade_id:
                            copied_trades[slave['login']][trade_id] = copied_trade_id
                        else:
                            copied_trades[slave['login']][trade_id] = "Failed to copy trading"

            if master['login'] != mt5.account_info().login:
                if not login_to_mt5_account(master):
                    return

        # Check for closed trades on master account
        for slave in slaves: 
            closed_trade_ids = set(copied_trades[slave['login']].keys()) - current_trade_ids_master

        # Iterate through copied trades to check if any trade has been closed on master account
            for trade_id in closed_trade_ids:
                if not login_to_mt5_account(slave):
                    return
                result = close_trade_on_slave(copied_trades[slave['login']][trade_id], slave['login'])
                # if result is not None:
                del copied_trades[slave['login']][trade_id]

        if master['login'] != mt5.account_info().login:
            if not login_to_mt5_account(master):
                return

        time.sleep(1)

# Copy trade to a specific slave account
def copy_trade_to_slave(trade, slave):
    symbol = trade.symbol
    volume = trade.volume
    order_type = mt5.ORDER_TYPE_BUY if trade.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_SELL
    price = trade.price_current
    sl = trade.sl
    tp = trade.tp

    if not mt5.symbol_select(symbol, True):
        log_status(f"Failed to select symbol {symbol}")
        return None

    maxAttempCount = 0
    while maxAttempCount < 10:
        bidOrAsk = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
        log_status(f"current bid: {mt5.symbol_info_tick(symbol).bid}, current ask: { mt5.symbol_info_tick(symbol).ask}")
        # price = min(price, bidOrAsk) if order_type == mt5.ORDER_TYPE_BUY else max(price, bidOrAsk)

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': volume,
            'type': order_type,
            'price': bidOrAsk,
            'sl': sl,
            'tp': tp,
            'deviation': 30,
            'magic': 0,
            'comment': 'Copied trade',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            log_status(f"Failed to copy trade to {slave['login']}: {result.comment}")
            log_status(f"Retcode: {result.retcode}")
            maxAttempCount += 1
            time.sleep(0.3)
        else:
            log_status(f"Trade copied to {slave['login']} successfully with ticket {result.order}")
            return result.order

    return None

# Close trade on a specific slave account
def close_trade_on_slave(trade_id, logId):
    positions = mt5.positions_get()
    if positions is None:
        log_status(f"Failed to get positions for {logId}: {mt5.last_error()}")
        return None

    for position in positions:
        if position.ticket == trade_id:
            symbol = position.symbol
            volume = position.volume
            order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

            maxCount = 0
            while maxCount < 10:
                price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
                request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'position': position.ticket,
                    'symbol': symbol,
                    'volume': volume,
                    'type': order_type,
                    'price': price,
                    'deviation': 30,
                    'magic': 0,
                    'comment': 'Close copied trade',
                    'type_time': mt5.ORDER_TIME_GTC,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                }
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    log_status(f"Failed to close trade on {logId}: {result.comment}")
                    maxCount += 1
                    time.sleep(0.3)
                else:
                    log_status(f"Trade {trade_id} closed on {logId} successfully")
                    return result.order

            return None

    log_status(f"Trade {trade_id} not found on {logId}")
    return None

if __name__ == "__main__":
    monitor_trades(master)
