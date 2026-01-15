# 💰 Expenses Tracker

A desktop application for tracking personal expenses with multi-currency support and real-time exchange rates. Built with Python as part of my journey learning programming fundamentals.

## 📸 Project Overview

This is my first complete GUI application using Python! The Expenses Tracker helps users manage their expenses across different currencies, automatically converting everything to EGP (Egyptian Pounds) for unified tracking.

## ✨ Features

- **Multi-Currency Support**: Track expenses in any currency (USD, SAR, EUR, etc.)
- **Real-Time Exchange Rates**: Automatic currency conversion using CurrencyFreaks API
- **Smart Currency Autocomplete**: Quick currency selection with intelligent suggestions
- **Expense Categories**: Organize expenses by type (Food, Transportation, Utilities, etc.)
- **Multiple Payment Methods**: Track how you paid (Cash, Credit Card, Mobile Payment, etc.)
- **Data Persistence**: Save and load your expenses automatically
- **Visual Data Table**: Clean, organized display with alternating row colors
- **Running Total**: Real-time calculation of total expenses in EGP
- **Date Tracking**: Record expense dates with an easy-to-use date picker

## 🛠️ Technologies Used

- **Python 3.x** - Core programming language
- **tkinter** - Standard GUI framework
- **customtkinter** - Modern UI components and themes
- **tksheet** - Spreadsheet-like data table
- **tkcalendar** - Date picker widget
- **pycountry** - ISO currency codes database
- **requests** - API calls for exchange rates
- **python-dotenv** - Environment variable management

## 📋 Prerequisites

Before running this application, make sure you have Python 3.x installed on your system.

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/expenses-tracker.git
cd expenses-tracker
```

2. **Install required packages**
```bash
pip install customtkinter
pip install tksheet
pip install tkcalendar
pip install pycountry
pip install requests
pip install python-dotenv
```

3. **Set up your API key**
   - Get a free API key from [CurrencyFreaks](https://currencyfreaks.com/)
   - Create a `.env` file in the project root
   - Add your API key:
   ```
   MY_SECRET_KEY=your_api_key_here
   ```

## 💻 Usage

Run the application:
```bash
python ExpensesTracker.py
```

### Adding an Expense

1. Enter the amount
2. Type the currency code (e.g., USD, SAR, EUR) - autocomplete will help you
3. Select a category from the dropdown
4. Choose your payment method
5. Pick the date (defaults to today)
6. Click "Add Expense"

The application will automatically convert the amount to EGP and add it to your tracker!

### Viewing Your Data

- All expenses are displayed in the table below
- The total amount (in EGP) is shown at the bottom
- Data is automatically saved to `expenses.txt`

## 🎨 Features Explained

### Currency Autocomplete
Start typing a currency code and get instant suggestions based on ISO 4217 currency codes.

### Automatic Conversion
When you add an expense in a foreign currency:
1. The app fetches the latest exchange rate
2. Converts to USD as an intermediate step
3. Then converts to EGP for the final amount

### Data Persistence
Your expenses are automatically saved and will load when you restart the app.

## 📂 Project Structure

```
expenses-tracker/
│
├── ExpensesTracker.py          # Main application file
├── ExpensesTrackerGPT.py       # Enhanced version with validation
├── .env                         # API key (not tracked in git)
├── .gitignore                   # Git ignore rules
├── expenses.txt                 # Data storage file
└── README.md                    # This file
```

## 🎓 Learning Journey

This project represents my first steps into GUI programming with Python. Through building it, I learned:

- **GUI Development**: Creating windows, forms, and interactive elements
- **Event Handling**: Responding to user clicks, keyboard input, and selections
- **API Integration**: Making HTTP requests and handling JSON responses
- **Data Persistence**: Reading from and writing to files
- **Error Handling**: Managing user input validation and API failures
- **Code Organization**: Structuring functions and managing global state
- **Third-Party Libraries**: Working with external packages and documentation

## 🐛 Known Issues

- Internet connection required for currency conversion
- API rate limits may apply (check CurrencyFreaks free tier limits)
- Date format is fixed to YYYY-MM-DD

## 🔮 Future Improvements

Ideas for future versions:
- [ ] Add expense editing and deletion
- [ ] Export to CSV/Excel
- [ ] Charts and analytics
- [ ] Budget limits and warnings
- [ ] Expense search and filtering
- [ ] Multiple currency display options
- [ ] Offline mode with cached rates

## 🤝 Contributing

This is a learning project, but suggestions and feedback are welcome! Feel free to open an issue or submit a pull request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Mostafa Gamal Bisher**
- Email: mgb.self.esteem@gmail.com
- Location: Dammam, Saudi Arabia
- LinkedIn: [Your LinkedIn Profile]
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Thanks to [CurrencyFreaks](https://currencyfreaks.com/) for the free exchange rates API
- Inspired by the need to track expenses across multiple currencies while working abroad
- Built as part of my self-learning journey in software development

---

**Note**: This is a learning project created during my transition from accounting to software development. The code may not follow all best practices, but it represents my progress and understanding at this stage of my learning journey.

---

*Made with ❤️ and lots of learning by Mostafa Gamal Bisher*
