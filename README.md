# Aiogram Bot Template

This repository provides a comprehensive template for creating Telegram bots using the Aiogram framework. It includes a powerful admin panel accessible via the `/admin` command, making it ideal for managing bot functionalities and user interactions.

## Table of Contents

1. [About the Project](#about-the-project)
2. [Project Features](#project-features)
   1. [Admin Panel](#admin-panel)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Installation and Usage](#installation-and-usage)
6. [Contributing](#contributing)
7. [Reporting Issues](#reporting-issues)
8. [License](#license)
9. [Contact](#contact)

## About the Project

This template is designed for developers looking to create Telegram bots using the Aiogram framework. It comes with an integrated admin panel that allows bot administrators to manage users, send advertisements, add new admins, and more, directly from the bot interface.

## Project Features

- **Admin Management:** Add, remove, and manage admins.
- **Advertisement Sending:** Send ads with a speed of approximately 100 messages per minute.
- **User Management:** Block, check, and manage users.
- **Mandatory Channels:** Add and manage mandatory channels for users.
- **Statistics:** View bot usage statistics.
- **Language Support:** The bot operates in the user's Telegram device language.
- **Permission Control:** Admins have different levels of control over the bot and other admins.

### Admin Panel

The admin panel is accessible by sending the `/admin` command in the bot. It allows the following functionalities:

- **Admin Control:** Full rights for the main admin to manage other admins.
- **Channel Management:** Control only the channels added by the respective admin.
- **Role-Based Access:** Admins can only perform actions based on their permissions.
- **Send advertisement:** Send advertisement message for all user.
- **Control bot:** Admin can control bot and bot user.
- **View Statistika:** Vaev real Statistika.

## Technologies Used

- **Programming Language:** Python (3+), Cython (3+)
- **Framework:** Aiogram 3.5
- **Database:** Mysql 8+
- **Dependencies:**
  - `aiogram==3.5.0` - [Aiogram Documentation](https://docs.aiogram.dev/en/latest/)
  - `deep-translator==1.11.4` - [Deep Translator Documentation](https://deep-translator.readthedocs.io/en/latest/)
  - `environs==11.0.0` - [Environs Documentation](https://pypi.org/project/environs/)
  - `mysql-connector-python==9.0.0` - [MySQL Connector/Python Documentation](https://dev.mysql.com/doc/connector-python/en/)
  - `numpy==2.0.1` - [NumPy Documentation](https://numpy.org/doc/stable/)
  - `openpyxl==3.1.5` - [OpenPyXL Documentation](https://openpyxl.readthedocs.io/en/stable/)
  - `pandas==2.2.2` - [Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/)
  - `pydantic==2.7.4` - [Pydantic Documentation](https://docs.pydantic.dev/latest/)
  - `pydantic_core==2.18.4` - [Pydantic Core Documentation](https://docs.pydantic.dev/pydantic-core/)
  - `python-dotenv==1.0.1` - [Python Dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)
  - `Cython==3.0.11` - [Cython Documentation](https://cython.readthedocs.io/en/latest/)
  - `requests==2.32.3` - [Requests Documentation](https://docs.python-requests.org/en/latest/)
  - `urllib3==2.2.2` - [urllib3 Documentation](https://urllib3.readthedocs.io/en/stable/)

## Project Structure

```plaintext
Aiogram-Bot-Template/
│
├── README.md                      # Project documentation
├── main.py                        # Entry point for the bot
├── loader.py                      # Bot loader
├── setup.py                       # Setup script for the project
├── requirements.txt               # Project dependencies
├── LICENSE                        # License file
│
├── cython_code/                   # Cython optimized code
│   ├── file_db.pyx                # class for working with data in files
│   ├── my_translator.pyx          # Tranlator class
│   ├── send_ads.pyx               # Advertisement sender for all user
│   ├── throttling_middleware.pyx  # Middleware class to manage throttling of requests to prevent overloading.
│   └── user_check.pyx             # Check user has joined the required channels
│
├── data/                          # Data-related modules
│   └── config.py                  # A collection of necessary variables
│
├── filters/                       # Custom filters for the bot
│   ├── admin.py                   # Filters for admin
│   └── ban.py                     # Filters banned user
│
├── function/                      # Core bot functionalities
│   ├── function.py                # A collection of some functions
│   ├── send_ads.py                # Chaged to cython_code/send_ads.pyx 
│   └── translator.py              # Tanslator function
│
├── handlers/                      # Request handlers
│   ├── __init__.py                # file that gathers all handlers
│   ├── admins/                    # all admins file
│   └── users/
│       ├── __init__.py
│       ├── check_ban.py           # Handles incoming messages from banned users.
│       ├── check_join.py          # Handles the 'check_join' callback query to verify
│       ├── check_usr.py           # Handles the text to check if the user has joined the required channels
│       ├── close.py               # handlers for colse button
│       ├── help.py                # handlers for command /help
│       └── start.py               # handlers for command /start
│
├── keyboards/                     # Bot keyboards
│   ├── inline/                    # Inline keyboards
│       ├── admin_btn.py           # Inline keyboards for admins
│       ├── button.py              # Base inline keyboards
│       ├── close_btn.py
│       └── user.py
│
├── middlewares/                   # Middlewares for processing requests
│   ├── __init__.py              
│   ├── check_user.py              # Not be used, Changed to cython_code/user_check.pyx
│   └── throttling.py              # Not be used, Changed to cython_code/throttling_middleware.pyx
│
├── states/                        # State management
│   └── admin_state.py             # Class state for admin
│
└── utils/                         # Utility scripts
    ├── notify_admins.py           # The admin will receive information about the bot being started
    ├── set_bot_commands.py        # Sets up the necessary commands (/) for the bot
    └── db_api/
        ├── bot_db.py              # Not be used, Changed to cython_code/file_db.pyx
        └── mysql_db.py            # Class for working with MySQL database
```

## Installation and Usage

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/UznetDev/Aiogram-Bot-Template.git
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd Aiogram-Bot-Template
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Create a .env file:**
   - On Windows:
     ```sh
     wsl nano .env
     ```
   - On macOS and Linux:
     ```sh
     nano .env
     ```
7. **Write in the .env file:**
  ```
BOT_TOKEN=<Your Bot token from @BotFather>
ADMIN=<Admin Id>
HOST=<host default localhost>
MYSQL_USER=<your MySQL user>
MYSQL_PASSWORD=<your MySQL password>
MYSQL_DATABASE=<your MySQL database>
```
6. **Run the setup.py:**
   ```bash
   python setup.py build_ext --inplace
   ```
6. **Run the Bot:**
   ```bash
   python main.py
   ```

### Ensuring Continuous Operation

#### Windows Service

To run the bot as a Windows Service, you can use tools like NSSM (Non-Sucking Service Manager):
1. Download and install NSSM.
2. Create a service using NSSM and point it to `python main.py` in the project directory.

#### Linux Systemd

To run the bot as a systemd service on Linux:
1. Create a service file:
    ```sh
    nano /etc/systemd/system/tikme_uzbot.service
   ```
    ```ini
    [Unit]
    Description=Aiogram-Bot-Template Service
    After=network.target

    [Service]
    User=yourusername
    WorkingDirectory=/path/to/Aiogram-Bot-Template
    ExecStart=/usr/bin/python3 /path/to/Aiogram-Bot-Template/start.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
   
   ```sh
    sudo systemctl start Aiogram-Bot-Template
    sudo systemctl enable Aiogram-Bot-Template
    ```


## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.
## Reporting Issues

If you find any issues with the bot or have suggestions, please open an issue in this repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## <i>Contact</i>

If you have any questions or suggestions, please contact:
- Email: uznetdev@example.com
- GitHub Issues: [Issues section](https://github.com/UznetDev/TikMe_UzBot/issues)
- GitHub Profile: [UznetDev](https://github.com/UznetDev/)
- Telegram: [UZNet_Dev](https://t.me/UZNet_Dev)
- Linkedin: [Abdurahmon Niyozaliev](https://www.linkedin.com/in/abdurakhmon-niyozaliyev-%F0%9F%87%B5%F0%9F%87%B8-66545222a/)


### <i>Thank you for your interest in the project!</i>
