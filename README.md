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
  - `openpyxl==3.1.5` - [OpenPyXL Documentation](https://openpyxl.readthedocs.io/en/stable/)
  - `pandas==2.2.2` - [Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/)
  - `Cython==3.0.11` - [Cython Documentation](https://cython.readthedocs.io/en/latest/)
  - `requests==2.32.3` - [Requests Documentation](https://docs.python-requests.org/en/latest/)
  - `urllib3==2.2.2` - [urllib3 Documentation](https://urllib3.readthedocs.io/en/stable/)

## Project Structure

```plaintext
Aiogram-Bot-Template/
│
├── README.md                            # Project documentation
├── main.py                              # Entry point for the bot
├── loader.py                            # Bot loader
├── setup.py                             # Setup script for the project
├── requirements.txt                     # Project dependencies
├── LICENSE                              # License file
│
├── cython_code/                         # Cython optimized code 
│   ├── file_db.pyx                      # Class for working with data in files
│   ├── my_translator.pyx                # Translator class
│   ├── send_ads.pyx                     # Advertisement sender for all users 
│   ├── throttling_middleware.pyx        # Middleware class to manage throttling of requests to prevent overloading
│   └── user_check.pyx                   # Check if user has joined the required channels
│
├── data/                                # Data-related modules
│   └── config.py                        # A collection of necessary variables
│
├── filters/                             # Custom filters for the bot
│   ├── admin.py                         # Filters for admin
│   └── ban.py                           # Filters for banned users
│
├── function/                            # Core bot functionalities
│   ├── function.py                      # A collection of various functions
│   ├── send_ads.py                      # Moved to cython_code/send_ads.pyx 
│   └── translator.py                    # Translator function
│ 
├── handlers/                            # Request handlers
│   ├── __init__.py                      # Initialize the handlers module
│   ├── admins/                          # Admin-specific handlers
│   │   ├── super_admin.py               # Super admin functionalities
│   │   ├── main_panel.py                # Main admin panel operations
│   │   ├── admin_settings/              # Admin settings submodule
│   │   │   ├── attach_admins.py         # Attach admin functionalities
│   │   │   └── add_admin_first_step.py  # Steps to add a new admin
│   │   ├── statistika/                  # Statistical data management for admins
│   │   │   ├── statistika.py            # Main statistics functionalities
│   │   │   └──  download_statistics.py  # Download statistics data
│   │   ├── check_usr/                   # Admin user check functionalities│ 
│   │   │   ├── block_users.py           # Block users functionalities
│   │   │   ├── attach_usr.py            # Attach users to specific operations
│   │   │   ├── send_message.py          # Sending messages to users
│   │   │   └──  send_ads_message.py     # Sending advertisement messages
│   │   ├── send_ads/                    # Admin advertisement functionalities
│   │       ├── send_ads.py              # Send ads functionalities
│   │       ├── stop_ads.py              # Stop advertisements functionalities
│   │       └──  get_message.py          # Get messages for advertisements
│   ├── users/                           # User-specific handlers
│   │   ├── check_ban.py                 # Check if a user is banned
│   │   ├── check_join.py                # Check if a user has joined required channels
│   │   ├── check_usr.py                 # General user check functionalities
│   │   ├── close.py                     # Close user sessions
│   │   ├── help.py                      # Help command for users
│   │   └── start.py                     # Start command for users
│   ├── errors/                          # Error handling module
│       └── error_handler.py             # General error handler functionalities
│ 
├── keyboards/                           # Bot keyboards
│   ├── inline/                          # Inline keyboards
│   │   ├── admin_btn.py                 # Inline keyboards for admins
│   │   ├── button.py                    # Base inline keyboards
│   │   ├── close_btn.py                 # Close button functionality
│       └── user.py                      # User-specific inline keyboards
│
├── middlewares/                         # Middlewares for processing requests
│   ├── __init__.py                      # Initialize middlewares
│   ├── check_user.py                    # Not used, moved to cython_code/user_check.pyx
│   └── throttling.py                    # Not used, moved to cython_code/throttling_middleware.pyx
│
├── states/                              # State management
│   └── admin_state.py                   # Class state for admin
│
└── utils/                               # Utility scripts
    ├── notify_admins.py                 # Notify admins when the bot is started
    ├── set_bot_commands.py              # Set up the necessary commands (/) for the bot
    └── db_api/
        ├── bot_db.py                    # Not used, moved to cython_code/file_db.pyx
        └── mysql_db.py                  # Class for working with MySQL database
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
