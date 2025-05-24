# 📊 SEC Financial Data Extractor

A powerful Streamlit web application that extracts and analyzes financial data from SEC filings using the official SEC EDGAR API.

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Features

- **Interactive Web Interface**: Easy-to-use Streamlit GUI
- **40+ Major Companies**: Pre-configured with popular stock tickers
- **Multi-Year Analysis**: Extract 1-10 years of financial data
- **Interactive Visualizations**: Dynamic charts using Plotly
- **Multiple Export Formats**: Download as CSV or Excel
- **Real-time Data**: Direct from SEC EDGAR database
- **Financial Metrics**: Revenue, Net Income, Assets, Cash, Equity, and more

## 🏢 Supported Companies

The app includes major companies from various sectors:

**Technology**: AAPL, MSFT, GOOGL, META, NVDA, TSLA, ADBE, CRM, INTC, CSCO
**Finance**: JPM, BAC, WFC, V, MA, BRK-A
**Healthcare**: JNJ, PFE, UNH, ABBV, ABT, MRK
**Consumer**: WMT, HD, KO, PEP, NKE, COST
**And many more...**

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sec-financial-extractor.git
   cd sec-financial-extractor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🌐 Online Deployment

### Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Deploy your forked repository
5. Your app will be live at `https://your-app-name.streamlit.app`

### Deploy to Heroku

1. Create a `Procfile`:
   ```
   web: sh setup.sh && streamlit run app.py
   ```

2. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [general]\n\
   email = \"your-email@domain.com\"\n\
   " > ~/.streamlit/credentials.toml
   echo "\
   [server]\n\
   headless = true\n\
   enableCORS=false\n\
   port = $PORT\n\
   " > ~/.streamlit/config.toml
   ```

3. Deploy to Heroku using Git or GitHub integration

## 📖 Usage

### Basic Usage

1. **Select Companies**: Choose from the dropdown or search by ticker
2. **Set Time Range**: Select 1-10 years of historical data
3. **Click Analyze**: Process the selected companies
4. **Explore Results**: View charts, tables, and detailed metrics
5. **Download Data**: Export as CSV or Excel for further analysis

### Advanced Features

- **Interactive Charts**: Hover over data points for detailed information
- **Company Comparison**: Analyze multiple companies side-by-side
- **Detailed View**: Deep dive into individual company metrics
- **Historical Trends**: Track financial performance over time

## 📊 Data Sources

This application uses the official SEC EDGAR API:
- **Source**: [SEC EDGAR Database](https://www.sec.gov/edgar)
- **API Endpoint**: `https://data.sec.gov/api/xbrl/`
- **Data Types**: 10-K (Annual) and 10-Q (Quarterly) filings
- **Update Frequency**: Real-time as companies file reports

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Data Processing**: Pandas for data manipulation
- **Visualizations**: Plotly for interactive charts
- **API Requests**: Python requests library
- **Export**: Excel/CSV generation

### Key Components
- `SECDataExtractor`: Core class for API interactions
- `create_financial_charts()`: Generates interactive visualizations
- `main()`: Streamlit application interface

### Financial Metrics Extracted
- Revenue/Sales
- Net Income
- Total Assets
- Current Assets
- Total Liabilities
- Stockholders' Equity
- Cash and Cash Equivalents
- Operating Cash Flow
- Earnings Per Share (Basic & Diluted)

## 📄 File Structure

```
sec-financial-extractor/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
└── assets/              # Screenshots and images
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Ideas for Contributions
- Add more companies and sectors
- Implement additional financial ratios
- Add export to other formats (PDF, JSON)
- Create industry comparison features
- Add email alerts for new filings

## 📋 TODO

- [ ] Add more financial metrics and ratios
- [ ] Implement caching for faster load times
- [ ] Add industry benchmarking
- [ ] Create automated report generation
- [ ] Add support for international companies
- [ ] Implement user authentication
- [ ] Add real-time alerts for new filings

## ⚠️ Disclaimer

This application is for informational and educational purposes only. The financial data provided should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors and conduct your own research before making investment decisions.

## 📞 Support

If you encounter any issues or have questions:

1. **Check the Issues**: Look for existing solutions in the [GitHub Issues](https://github.com/yourusername/sec-financial-extractor/issues)
2. **Create an Issue**: Report bugs or request features
3. **Documentation**: Review the SEC EDGAR API documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SEC**: For providing free access to financial data through EDGAR
- **Streamlit**: For the amazing web framework
- **Plotly**: For interactive visualization capabilities
- **Pandas Community**: For powerful data manipulation tools

---

**Made with ❤️ by [Your Name]**

*Star ⭐ this repo if you find it helpful!*