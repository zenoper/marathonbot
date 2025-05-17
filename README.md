# Marathon Bot

A Telegram bot for managing SAT preparation marathon events with referral system functionality. The bot helps manage user registrations, track referrals, and provide access to private channels based on referral achievements.

## Features

- **Referral System**: Users can generate unique invite links to refer others
- **Automatic Join Request Handling**: Automatically processes and tracks new member joins
- **Referral Tracking**: Keeps track of each user's referrals and rewards
- **Private Channel Access**: Automatically grants access to private channels when users reach referral goals
- **Admin Commands**: Special commands for administrators to check user statistics
- **Top Referrers**: Leaderboard system to show top performing referrers
- **Anti-Spam**: Built-in throttling middleware to prevent spam

## Commands

- `/start` - Start the bot and get your referral link
- `/check_my_referrals` - Check your referral statistics
- `/top_referrers` - View the leaderboard of top referrers
- `/admin_check [username/id]` - (Admin only) Check specific user's referral details

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd marathonbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following configuration:
```env
# Bot Configuration
BOT_TOKEN=
MAIN_CHANNEL_ID=
PRIVATE_CHANNEL_ID=
REQUIRED_REFERRALS=5  # Number of referrals needed for private access

# Admin Configuration
ADMIN=["123456789"]  # List of admin user IDs

# Database Configuration
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
```

4. Set up PostgreSQL database and create the required database

5. Run the bot:
```bash
python run.py
```

## Database Schema

The bot uses PostgreSQL with the following tables:

- **users**: Stores user information and referral counts
- **invite_links**: Tracks generated invite links and their usage
- **referrals**: Records all successful referrals

## Development

The project structure:
```
marathonbot/
├── app/
│   ├── handlers/
│   │   └── start.py
│   ├── keyboards.py
│   ├── middlewares.py
│   └── states.py
├── utils/
│   ├── bot_commands.py
│   ├── notify_admin.py
│   └── postgresql.py
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Notes

- Never commit the `.env` file to version control
- Regularly rotate bot tokens and database credentials
- Keep the admin list updated and secure
