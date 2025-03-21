# Copy Trading Bot

## Overview
This is a Copy Trading Bot implemented in Python using the MetaTrader5 (MT5) API. It allows users to synchronize trades between a Master account and multiple Slave accounts. The Master account monitors trades and replicates them on the Slave accounts.

## Features
- Master mode monitors trades in real-time.
- Slave accounts automatically copy trades from the Master account.
- Supports trade opening, modification, and closing.
- Implements error handling for trade execution failures.

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/copy-trading-bot.git
   ```
2. Install required dependencies:
   ```sh
   pip install MetaTrader5
   ```
3. Copy the script to your working directory.
4. Modify `accounts.json` to include your MetaTrader 5 credentials.
5. Run the script:
   ```sh
   python copy_trading_bot.py
   ```

## Usage
### Setup Accounts
1. Edit `accounts.json` to configure the Master and Slave accounts( as many as you want):
   ```json
   {
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
           },
           {
               "login": "YOUR_LOGIN",
               "password": "YOUR_PASSWORD",
               "server": "YOUR_SERVER"
           }
       ]
   }
   ```

### Running the Bot
1. Ensure `accounts.json` is configured correctly.
2. Run the script:
   ```sh
   python copy_trading_bot.py
   ```
3. The bot will automatically monitor trades and copy them to Slave accounts.

## Dependencies
- Python 3.x
- MetaTrader5 (`pip install MetaTrader5`)

## Error Handling
- If the bot fails to log in, it will print an error message.
- If trade execution fails, the bot will retry up to 10 times.
- Errors will be logged in the console with timestamps.

## Contribution
1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push to your branch and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any questions or issues, open an issue in the repository or contact the project maintainer. Email: ms0606.papa@gmail.com

