
# Fullstack Stock Trading App

## Overview
The **Fullstack Stock Trading App** is a comprehensive web application that allows users to simulate stock trading activities in real time. It integrates both frontend and backend technologies to deliver a seamless user experience for managing portfolios, executing trades, and tracking stock performance.

---

## Features
- **Real-Time Stock Data**: Fetch and display live stock prices and performance metrics.
- **User Authentication**: Secure login and registration with JWT-based authentication.
- **Portfolio Management**: Track holdings, balances, and trading history.
- **Trade Execution**: Buy and sell stocks with dynamic pricing updates.
- **Responsive UI**: Optimized for both desktop and mobile devices.
- **Historical Data Visualization**: Charts and graphs to analyze stock trends.
- **Automated Stock Breakout Detection**: Real-time breakout identification using Alpaca's API.

---

## Tech Stack
### Frontend
- **HTML** - Markup for structured content.
- **Semantic UI** - Framework for responsive and professional UI design.

### Backend
- **Python** - Core programming language.
- **FastAPI** - High-performance API framework.
- **SQL** - Database management and querying.
- **Alpaca.V2 API** - Paper-trading and stock data integration.
- **Polygon API** - Real-time market data.
- **Cron Jobs** - Scheduling automated tasks.

### Deployment
- **Docker** - Containerized deployment.
- **AWS EC2** - Hosting backend and frontend.
- **Nginx** - Reverse proxy server.

---

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/AgastyaKro/Fullstack-Stock-Trading-App.git
cd Fullstack-Stock-Trading-App
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and specify:
```
DB_URI=<Your SQL Database URI>
ALPACA_API_KEY=<Your Alpaca API Key>
ALPACA_SECRET_KEY=<Your Alpaca Secret Key>
POLYGON_API_KEY=<Your Polygon API Key>
```

### 4. Start the Application
```bash
uvicorn main:app --reload
```

---

## Usage
1. **Sign Up or Login**: Create an account or log in with existing credentials.
2. **Search Stocks**: Use the search bar to find stocks.
3. **Execute Trades**: Buy and sell stocks with real-time data.
4. **Analyze Performance**: View charts and graphs to evaluate portfolio growth.
5. **Automated Breakout Detection**: Monitor stock breakouts with real-time alerts.

---

## API Endpoints
### User Authentication
- **POST** `/api/auth/register` - Register a new user.
- **POST** `/api/auth/login` - Authenticate user.

### Portfolio Management
- **GET** `/api/portfolio` - Retrieve portfolio details.
- **POST** `/api/portfolio/trade` - Execute a buy or sell order.

### Stock Data
- **GET** `/api/stocks/:symbol` - Fetch stock details for a given symbol.

---

## Screenshots
![Dashboard](screenshots/dashboard.png)
![Portfolio](screenshots/portfolio.png)

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with detailed changes.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

## Contact
**Author**: Agastya Krothapalli  
**Email**: agastyakro06@gmail.com  
**GitHub**: [AgastyaKro](https://github.com/AgastyaKro)

