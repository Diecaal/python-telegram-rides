from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import calendar
from datetime import datetime
from dotenv import load_dotenv
import os, json, random

load_dotenv()

DATA_FILE = 'data.json'

# Function to create a calendar keyboard
def create_calendar(year, month, file_name):
    users_data = read_users(file_name)
    cal = calendar.Calendar()
    keyboard = []

    # Header showing the month and year
    header = [InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore")]
    keyboard.append(header)

    # Days of the week header
    days = [InlineKeyboardButton(day, callback_data="ignore") for day in calendar.day_abbr]
    keyboard.append(days)

    # Calendar days
    for week in cal.monthdayscalendar(year, month):
        week_row = []
        for day in week:
            if day == 0:
                week_row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                display_text = str(day)
                formatted_date = f"{year}-{month:02d}-{day:02d}"  # Updated format here
                user_with_date = None
                # Check if the date is taken by a user
                for user, data in users_data.items():
                    if formatted_date in data.get('dates', []):
                        user_with_date = user
                        break
                # Use the first letter of the username if the date is taken
                if user_with_date:
                    display_text = user_with_date[0]  # First letter of username
                week_row.append(InlineKeyboardButton(display_text, callback_data=f"{year}-{month}-{day}"))
        keyboard.append(week_row)
        
    # Navigation buttons
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    navigation = [
        InlineKeyboardButton("<", callback_data=f"month-{prev_year}-{prev_month}"),
        InlineKeyboardButton(">", callback_data=f"month-{next_year}-{next_month}")
    ]
    keyboard.append(navigation)

    return InlineKeyboardMarkup(keyboard)

# Handler for /dates command
async def dates_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        await update.message.reply_text("Y dale, que no lo vas a romper")
        return
    
    if not user_is_registered(update.effective_user.username, DATA_FILE):
        await update.message.reply_text("First, register with '/register' command")  
        return  
    now = datetime.now()
    keyboard = create_calendar(now.year, now.month, DATA_FILE)
    await update.message.reply_text("Choose a date:", reply_markup=keyboard)
    # Display user stats
    stats_message = display_users_and_date_counts(DATA_FILE)
    await update.message.reply_text(stats_message)

# Callback query handler
async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    # Check if the callback data is for month navigation
    if data.startswith("month-"):
        _, year_month = data.split('-', 1)
        year, month = map(int, year_month.split('-'))
        keyboard = create_calendar(year, month, DATA_FILE)
        await query.edit_message_text(text="Choose a date:", reply_markup=keyboard)

    # Check if the callback data is for a specific date
    elif "-" in data and not data.startswith("month-"):
        # Print the selected date
        await query.edit_message_text(text=f"Selected date: {data}")
        user = update.effective_user
        if user.username:
            add_date_for_user(DATA_FILE, user.username, data)
        
# Function to check and initialize the JSON file
def init_json_file(file_name):
    if not os.path.isfile(file_name):
        with open(file_name, 'w') as file:
            json.dump({"users": {}}, file)

# Function to read user data from the JSON file
def read_users(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data['users']  # Corrected from 'data' to 'users'

def user_is_registered(username, file_name):
    return username in read_users(file_name)

# Function to add a new user with a color to the JSON file
def add_user(file_name, username):
    with open(file_name, 'r+') as file:
        data = json.load(file)
        if username not in data['users']:
            data['users'][username] = {"color": generate_random_color(), "dates": []}
            file.seek(0)
            json.dump(data, file)
            file.truncate()
    
def add_date_for_user(file_name, username, date):
    with open(file_name, 'r+') as file:
        data = json.load(file)
        user_data = data['users'].get(username, None)
        if user_data:
            user_data['dates'].append(date)
            file.seek(0)
            json.dump(data, file)
            file.truncate()
            
def display_users_and_date_counts(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        users = data.get('users', {})
        
        message = "Registered Users and Date Counts:\n"
        for user, user_data in users.items():
            date_count = len(user_data.get('dates', []))
            if date_count == 0:
                message += f"- {user}: {date_count}, te parecerá bonito\n"
            elif date_count == 1:
                message += f"- {user}: {date_count} día\n"
            else:
                message += f"- {user}: {date_count} días\n"

        return message
    
# Handler for /userstats command
async def userstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        await update.message.reply_text("Otra mas y llamo a Fabi")
        return
    
    stats_message = display_users_and_date_counts('data.json')
    await update.message.reply_text(stats_message)

# Handler for /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        await update.message.reply_text("Este script es inquebrantable mi pana")
        return
    
    user = update.effective_user
    if user.username:
        add_user(DATA_FILE, user.username)
        await update.message.reply_text(f"Now you are registered, {user.username}!")
    else:
        await update.message.reply_text("Welcome, anonymous user!")
        
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🛺 Comandos disponibles 🛺\n"
        "/start - Si es la primera vez usando el bot, pulsa aquí, suscribirse y dale a la campanita\n"
        "/dates - Muestra un calendario donde selecciones la fecha que vas a llevar el coche\n"
        "/count - Stats de usuarios registrados y días que han llevado/llevaran el coche\n"
        "/help - No es necesario porque esto es intuitivo al siguiente nivel\n"
    )
    await update.message.reply_text(help_text)
        
# Function to generate a random color in hexadecimal format
def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Main function to run the bot
def main():
    file_name = DATA_FILE
    init_json_file(file_name)
    
    application = Application.builder().token(os.getenv("TOKEN")).build()
    application.add_handler(CommandHandler("register", start_command))
    application.add_handler(CommandHandler("dates", dates_command))
    application.add_handler(CommandHandler("count", userstats_command))
    application.add_handler(CallbackQueryHandler(calendar_callback))
    application.add_handler(CommandHandler("help", help_command))
    
    application.run_polling()

if __name__ == "__main__":
    main()