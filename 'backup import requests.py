'backup import requests
import json
import pandas as pd
from datetime import datetime
import time
import re

class SECDataExtractor:
    def __init__(self, email="your-email@domain.com"):
        """
        Initialize SEC data extractor
        Args:
            email: Your email for SEC API requests (required by SEC)
        """
        self.base_url = "https://data.sec.gov/api/xbrl"
        self.headers = {
            'User-Agent': f'Financial Data Extractor {email}',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
    def get_company_cik(self, ticker):
        """Get CIK number for a company ticker"""
        try:
            # Expanded mapping of common tickers to CIKs
            ticker_to_cik = {
                'AAPL': '0000320193',   # Apple Inc
                'MSFT': '0000789019',   # Microsoft Corp
                'GOOGL': '0001652044',  # Alphabet Inc
                'GOOG': '0001652044',   # Alphabet Inc (Class A)
                'AMZN': '0001018724',   # Amazon.com Inc
                'TSLA': '0001318605',   # Tesla Inc
                'META': '0001326801',   # Meta Platforms Inc
                'NVDA': '0001045810',   # NVIDIA Corp
                'BRK-A': '0001067983',  # Berkshire Hathaway Inc
                'BRK-B': '0001067983',  # Berkshire Hathaway Inc
                'V': '0001403161',      # Visa Inc
                'JNJ': '0000200406',    # Johnson & Johnson
                'WMT': '0000104169',    # Walmart Inc
                'JPM': '0000019617',    # JPMorgan Chase & Co
                'MA': '0001141391',     # Mastercard Inc
                'PG': '0000080424',     # Procter & Gamble Co
                'UNH': '0000731766',    # UnitedHealth Group Inc
                'HD': '0000354950',     # Home Depot Inc
                'CVX': '0000093410',    # Chevron Corp
                'BAC': '0000070858',    # Bank of America Corp
                'ABBV': '0001551152',   # AbbVie Inc
                'PFE': '0000078003',    # Pfizer Inc
                'KO': '0000021344',     # Coca-Cola Co
                'AVGO': '0001730168',   # Broadcom Inc
                'MRK': '0000310158',    # Merck & Co Inc
                'PEP': '0000077476',    # PepsiCo Inc
                'TMO': '0000097745',    # Thermo Fisher Scientific Inc
                'COST': '0000909832',   # Costco Wholesale Corp
                'ABT': '0000001800',    # Abbott Laboratories
                'ACN': '0001467373',    # Accenture PLC
                'CSCO': '0000858877',   # Cisco Systems Inc
                'DHR': '0000313616',    # Danaher Corp
                'TXN': '0000097476',    # Texas Instruments Inc
                'VZ': '0000732712',     # Verizon Communications Inc
                'ADBE': '0000796343',   # Adobe Inc
                'NKE': '0000320187',    # Nike Inc
                'INTC': '0000050863',   # Intel Corp
                'CRM': '0001108524',    # Salesforce Inc
                'WFC': '0000072971'     # Wells Fargo & Co
            }
            return ticker_to_cik.get(ticker.upper())
        except:
            return None
    
    def get_company_facts(self, cik):
        """Get all financial facts for a company"""
        try:
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            time.sleep(0.1)  # Be respectful to SEC servers
            return response.json()
        except Exception as e:
            print(f"Error fetching company facts: {e}")
            return None
    
    def extract_financial_metrics(self, company_data, metrics=None):
        """
        Extract specific financial metrics from company data
        Args:
            company_data: JSON data from SEC API
            metrics: List of financial metrics to extract
        """
        if metrics is None:
            metrics = [
                'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                'CostOfRevenue', 'CostOfGoodsAndServicesSold',
                'GrossProfit', 'OperatingIncomeLoss', 'NetIncomeLoss',
                'Assets', 'AssetsCurrent', 'Liabilities', 'LiabilitiesCurrent',
                'StockholdersEquity', 'CashAndCashEquivalentsAtCarryingValue',
                'OperatingCashFlowNet', 'EarningsPerShareBasic', 'EarningsPerShareDiluted'
            ]
        
        financial_data = []
        
        if 'facts' not in company_data:
            return pd.DataFrame()
        
        us_gaap = company_data['facts'].get('us-gaap', {})
        
        for metric in metrics:
            if metric in us_gaap:
                metric_data = us_gaap[metric]
                
                # Get the most recent annual and quarterly data
                units = metric_data.get('units', {})
                
                for unit_type, values in units.items():
                    for entry in values:
                        if entry.get('form') in ['10-K', '10-Q']:  # Annual and quarterly reports
                            financial_data.append({
                                'metric': metric,
                                'value': entry.get('val'),
                                'unit': unit_type,
                                'date': entry.get('end'),
                                'period': entry.get('fp'),  # FY for annual, Q1/Q2/Q3/Q4 for quarterly
                                'form': entry.get('form'),
                                'fiscal_year': entry.get('fy'),
                                'filed_date': entry.get('filed')
                            })
        
        return pd.DataFrame(financial_data)
    
    def get_latest_financials(self, ticker, years=3):
        """
        Get latest financial data for a company
        Args:
            ticker: Stock ticker symbol
            years: Number of years of data to retrieve
        """
        cik = self.get_company_cik(ticker)
        if not cik:
            print(f"Could not find CIK for ticker {ticker}")
            return None
        
        print(f"Fetching data for {ticker} (CIK: {cik})")
        company_data = self.get_company_facts(cik)
        
        if not company_data:
            return None
        
        # Extract financial metrics
        df = self.extract_financial_metrics(company_data)
        
        if df.empty:
            print("No financial data found")
            return None
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter for recent years
        cutoff_date = datetime.now() - pd.DateOffset(years=years)
        df = df[df['date'] >= cutoff_date]
        
        # Sort by date descending
        df = df.sort_values('date', ascending=False)
        
        return df
    
    def create_financial_summary(self, df, ticker):
        """Create a summary of key financial metrics"""
        if df is None or df.empty:
            return None
        
        # Focus on annual data (10-K forms) for summary
        annual_data = df[df['form'] == '10-K'].copy()
        
        # Key metrics we want to summarize
        key_metrics = {
            'Revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
            'Net Income': ['NetIncomeLoss'],
            'Total Assets': ['Assets'],
            'Cash': ['CashAndCashEquivalentsAtCarryingValue'],
            'Stockholders Equity': ['StockholdersEquity']
        }
        
        summary = []
        
        for metric_name, metric_keys in key_metrics.items():
            for key in metric_keys:
                metric_data = annual_data[annual_data['metric'] == key]
                if not metric_data.empty:
                    # Remove duplicates by grouping by fiscal year and taking the first entry
                    unique_data = metric_data.drop_duplicates(subset=['fiscal_year'], keep='first')
                    # Get most recent 3 years
                    recent_data = unique_data.head(3)
                    for _, row in recent_data.iterrows():
                        summary.append({
                            'Company': ticker,
                            'Metric': metric_name,
                            'Value': row['value'],
                            'Date': row['date'].strftime('%Y-%m-%d'),
                            'Fiscal Year': row['fiscal_year'],
                            'Unit': row['unit']
                        })
                    break  # Use first available metric key
        
        return pd.DataFrame(summary)

    def get_available_companies(self):
        """Get list of available companies"""
        companies = {
            'AAPL': 'Apple Inc',
            'MSFT': 'Microsoft Corp',
            'GOOGL': 'Alphabet Inc (Google)',
            'AMZN': 'Amazon.com Inc',
            'TSLA': 'Tesla Inc',
            'META': 'Meta Platforms Inc (Facebook)',
            'NVDA': 'NVIDIA Corp',
            'BRK-A': 'Berkshire Hathaway Inc',
            'V': 'Visa Inc',
            'JNJ': 'Johnson & Johnson',
            'WMT': 'Walmart Inc',
            'JPM': 'JPMorgan Chase & Co',
            'MA': 'Mastercard Inc',
            'PG': 'Procter & Gamble Co',
            'UNH': 'UnitedHealth Group Inc',
            'HD': 'Home Depot Inc',
            'CVX': 'Chevron Corp',
            'BAC': 'Bank of America Corp',
            'ABBV': 'AbbVie Inc',
            'PFE': 'Pfizer Inc',
            'KO': 'Coca-Cola Co',
            'AVGO': 'Broadcom Inc',
            'MRK': 'Merck & Co Inc',
            'PEP': 'PepsiCo Inc',
            'TMO': 'Thermo Fisher Scientific Inc',
            'COST': 'Costco Wholesale Corp',
            'ABT': 'Abbott Laboratories',
            'ACN': 'Accenture PLC',
            'CSCO': 'Cisco Systems Inc',
            'DHR': 'Danaher Corp',
            'TXN': 'Texas Instruments Inc',
            'VZ': 'Verizon Communications Inc',
            'ADBE': 'Adobe Inc',
            'NKE': 'Nike Inc',
            'INTC': 'Intel Corp',
            'CRM': 'Salesforce Inc',
            'WFC': 'Wells Fargo & Co'
        }
        return companies
    
    def analyze_multiple_companies(self, tickers, years=3):
        """Analyze multiple companies and create comparison"""
        all_summaries = []
        
        for ticker in tickers:
            print(f"\nProcessing {ticker}...")
            df = self.get_latest_financials(ticker, years)
            
            if df is not None:
                summary = self.create_financial_summary(df, ticker)
                if summary is not None:
                    all_summaries.append(summary)
                    
                # Save individual company data
                output_file = f"{ticker}_financial_data.csv"
                df.to_csv(output_file, index=False)
                print(f"✓ {ticker} data saved to {output_file}")
            else:
                print(f"✗ Failed to get data for {ticker}")
        
        # Combine all summaries
        if all_summaries:
            combined_summary = pd.concat(all_summaries, ignore_index=True)
            combined_summary.to_csv("combined_financial_summary.csv", index=False)
            print(f"\n✓ Combined summary saved to combined_financial_summary.csv")
            return combined_summary
        
        return None

def select_companies():
    """Interactive company selection"""
    extractor = SECDataExtractor()
    companies = extractor.get_available_companies()
    
    print("Available Companies:")
    print("=" * 50)
    
    # Display companies in a nice format
    sorted_tickers = sorted(companies.keys())
    for i, ticker in enumerate(sorted_tickers, 1):
        print(f"{i:2d}. {ticker:6s} - {companies[ticker]}")
    
    print("\nSelect companies to analyze:")
    print("- Enter ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL)")
    print("- Or enter numbers separated by commas (e.g., 1,2,3)")
    print("- Or type 'all' to analyze all companies")
    
    while True:
        selection = input("\nYour selection: ").strip()
        
        if selection.lower() == 'all':
            return list(companies.keys())
        
        # Check if input contains numbers or tickers
        selections = [s.strip() for s in selection.split(',')]
        selected_tickers = []
        
        try:
            # Try to parse as numbers first
            if all(s.isdigit() for s in selections):
                for num in selections:
                    idx = int(num) - 1
                    if 0 <= idx < len(sorted_tickers):
                        selected_tickers.append(sorted_tickers[idx])
                    else:
                        print(f"Number {num} is out of range")
                        break
                else:
                    return selected_tickers
            else:
                # Parse as ticker symbols
                for ticker in selections:
                    ticker = ticker.upper()
                    if ticker in companies:
                        selected_tickers.append(ticker)
                    else:
                        print(f"Ticker '{ticker}' not found in available companies")
                        break
                else:
                    return selected_tickers
        except ValueError:
            print("Invalid input format. Please try again.")
        
        print("Please try again with valid selections.")

def main():
    """Main function with interactive company selection"""
    print("SEC Financial Data Extractor")
    print("=" * 40)
    
    # Set up extractor
    email = input("Enter your email address (required by SEC): ").strip()
    if not email:
        print("Email is required by SEC. Exiting.")
        return
    
    extractor = SECDataExtractor(email)
    
    # Select companies
    selected_tickers = select_companies()
    
    if not selected_tickers:
        print("No companies selected. Exiting.")
        return
    
    print(f"\nSelected companies: {', '.join(selected_tickers)}")
    
    # Get number of years
    while True:
        try:
            years = input("How many years of data? (default: 3): ").strip()
            years = int(years) if years else 3
            if years > 0:
                break
            else:
                print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nAnalyzing {len(selected_tickers)} companies for {years} years of data...")
    print("This may take a moment...")
    
    # Analyze companies
    combined_summary = extractor.analyze_multiple_companies(selected_tickers, years)
    
    if combined_summary is not None:
        print("\n" + "="*60)
        print("FINANCIAL SUMMARY")
        print("="*60)
        
        # Display summary by company
        for ticker in selected_tickers:
            company_data = combined_summary[combined_summary['Company'] == ticker]
            if not company_data.empty:
                print(f"\n{ticker}:")
                print("-" * 30)
                
                # Group by metric and remove duplicates
                for metric in company_data['Metric'].unique():
                    metric_data = company_data[company_data['Metric'] == metric]
                    # Remove duplicates by fiscal year, keep most recent
                    unique_metric_data = metric_data.drop_duplicates(subset=['Fiscal Year'], keep='first')
                    unique_metric_data = unique_metric_data.sort_values('Fiscal Year', ascending=False)
                    
                    print(f"\n  {metric}:")
                    for _, row in unique_metric_data.iterrows():
                        value = f"{row['Value']:,.0f}" if pd.notnull(row['Value']) else "N/A"
                        print(f"    {row['Fiscal Year']}: ${value} {row['Unit']}")
        
        print(f"\n" + "="*60)
        print("FILES CREATED:")
        print("="*60)
        for ticker in selected_tickers:
            print(f"• {ticker}_financial_data.csv - Detailed financial data")
        print("• combined_financial_summary.csv - Summary of all companies")
        
    else:
        print("No data was successfully extracted.")

if __name__ == "__main__":
    main()
//