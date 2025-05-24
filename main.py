import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

class SECDataExtractor:
    def __init__(self, email="streamlit-app@example.com"):
        """Initialize SEC data extractor"""
        self.base_url = "https://data.sec.gov/api/xbrl"
        self.headers = {
            'User-Agent': f'SEC Financial Data Extractor Streamlit App {email}',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
    def get_company_cik(self, ticker):
        """Get CIK number for a company ticker"""
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
    
    def get_company_facts(self, cik):
        """Get all financial facts for a company"""
        try:
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            time.sleep(0.1)  # Be respectful to SEC servers
            return response.json()
        except Exception as e:
            st.error(f"Error fetching company facts: {e}")
            return None
    
    def extract_financial_metrics(self, company_data):
        """Extract financial metrics from company data"""
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
                units = metric_data.get('units', {})
                
                for unit_type, values in units.items():
                    for entry in values:
                        if entry.get('form') in ['10-K', '10-Q']:
                            financial_data.append({
                                'metric': metric,
                                'value': entry.get('val'),
                                'unit': unit_type,
                                'date': entry.get('end'),
                                'period': entry.get('fp'),
                                'form': entry.get('form'),
                                'fiscal_year': entry.get('fy'),
                                'filed_date': entry.get('filed')
                            })
        
        return pd.DataFrame(financial_data)
    
    def get_latest_financials(self, ticker, years=3):
        """Get latest financial data for a company"""
        cik = self.get_company_cik(ticker)
        if not cik:
            return None, f"Could not find CIK for ticker {ticker}"
        
        company_data = self.get_company_facts(cik)
        if not company_data:
            return None, f"Failed to fetch data for {ticker}"
        
        df = self.extract_financial_metrics(company_data)
        if df.empty:
            return None, f"No financial data found for {ticker}"
        
        df['date'] = pd.to_datetime(df['date'])
        cutoff_date = datetime.now() - pd.DateOffset(years=years)
        df = df[df['date'] >= cutoff_date]
        df = df.sort_values('date', ascending=False)
        
        return df, "Success"
    
    def create_financial_summary(self, df, ticker):
        """Create a summary of key financial metrics"""
        if df is None or df.empty:
            return None
        
        annual_data = df[df['form'] == '10-K'].copy()
        
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
                    unique_data = metric_data.drop_duplicates(subset=['fiscal_year'], keep='first')
                    recent_data = unique_data.head(5)  # Get 5 years for better visualization
                    for _, row in recent_data.iterrows():
                        summary.append({
                            'Company': ticker,
                            'Metric': metric_name,
                            'Value': row['value'],
                            'Date': row['date'].strftime('%Y-%m-%d'),
                            'Fiscal Year': row['fiscal_year'],
                            'Unit': row['unit']
                        })
                    break
        
        return pd.DataFrame(summary)

    def get_available_companies(self):
        """Get list of available companies"""
        return {
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

def create_financial_charts(summary_df):
    """Create interactive charts for financial data"""
    if summary_df.empty:
        return None
    
    # Create subplots for different metrics
    metrics = summary_df['Metric'].unique()
    companies = summary_df['Company'].unique()
    
    charts = {}
    
    for metric in metrics:
        metric_data = summary_df[summary_df['Metric'] == metric].copy()
        metric_data = metric_data.sort_values('Fiscal Year')
        
        fig = go.Figure()
        
        for company in companies:
            company_data = metric_data[metric_data['Company'] == company]
            if not company_data.empty:
                fig.add_trace(go.Scatter(
                    x=company_data['Fiscal Year'],
                    y=company_data['Value'],
                    mode='lines+markers',
                    name=company,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title=f'{metric} Over Time',
            xaxis_title='Fiscal Year',
            yaxis_title=f'{metric} (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            yaxis=dict(tickformat='$,.0f')  # Fixed: moved tickformat into yaxis dict
        )
        
        charts[metric] = fig
    
    return charts

def main():
    st.set_page_config(
        page_title="SEC Financial Data Extractor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 SEC Financial Data Extractor")
    st.markdown("Extract and analyze financial data from SEC filings")
    
    # Initialize session state
    if 'extractor' not in st.session_state:
        st.session_state.extractor = SECDataExtractor()
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'combined_summary' not in st.session_state:
        st.session_state.combined_summary = None
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Company selection
    companies = st.session_state.extractor.get_available_companies()
    
    st.sidebar.subheader("Select Companies")
    selected_companies = st.sidebar.multiselect(
        "Choose companies to analyze:",
        options=list(companies.keys()),
        default=['AAPL', 'MSFT', 'GOOGL'],
        format_func=lambda x: f"{x} - {companies[x]}"
    )
    
    # Years selection
    years = st.sidebar.slider("Years of data", min_value=1, max_value=10, value=5)
    
    # Analysis button
    if st.sidebar.button("🚀 Analyze Companies", type="primary"):
        if not selected_companies:
            st.sidebar.error("Please select at least one company")
        else:
            st.session_state.analysis_complete = False
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_summaries = []
            total_companies = len(selected_companies)
            
            for i, ticker in enumerate(selected_companies):
                status_text.text(f"Processing {ticker}... ({i+1}/{total_companies})")
                progress_bar.progress((i) / total_companies)
                
                df, message = st.session_state.extractor.get_latest_financials(ticker, years)
                
                if df is not None:
                    summary = st.session_state.extractor.create_financial_summary(df, ticker)
                    if summary is not None:
                        all_summaries.append(summary)
                else:
                    st.warning(f"Failed to get data for {ticker}: {message}")
            
            progress_bar.progress(1.0)
            status_text.text("Analysis complete!")
            
            if all_summaries:
                st.session_state.combined_summary = pd.concat(all_summaries, ignore_index=True)
                st.session_state.analysis_complete = True
                st.success(f"Successfully analyzed {len(all_summaries)} companies!")
            else:
                st.error("No data was successfully extracted.")
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.combined_summary is not None:
        st.header("📈 Financial Analysis Results")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📋 Summary Table", "💾 Download Data", "🔍 Detailed View"])
        
        with tab1:
            st.subheader("Interactive Financial Charts")
            
            charts = create_financial_charts(st.session_state.combined_summary)
            if charts:
                for metric, chart in charts.items():
                    st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No chart data available")
        
        with tab2:
            st.subheader("Financial Summary Table")
            
            # Create pivot table for better display
            try:
                pivot_df = st.session_state.combined_summary.pivot_table(
                    index=['Company', 'Metric'],
                    columns='Fiscal Year',
                    values='Value',
                    aggfunc='first'
                ).reset_index()
                
                # Format numbers
                numeric_columns = pivot_df.select_dtypes(include=['number']).columns
                for col in numeric_columns:
                    pivot_df[col] = pivot_df[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
                
                st.dataframe(pivot_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating pivot table: {e}")
                st.dataframe(st.session_state.combined_summary, use_container_width=True)
        
        with tab3:
            st.subheader("Download Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download summary as CSV
                csv_buffer = io.StringIO()
                st.session_state.combined_summary.to_csv(csv_buffer, index=False)
                
                st.download_button(
                    label="📥 Download Summary (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name=f"financial_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download summary as Excel
                try:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        st.session_state.combined_summary.to_excel(writer, index=False, sheet_name='Summary')
                        try:
                            pivot_df = st.session_state.combined_summary.pivot_table(
                                index=['Company', 'Metric'],
                                columns='Fiscal Year',
                                values='Value',
                                aggfunc='first'
                            ).reset_index()
                            pivot_df.to_excel(writer, index=False, sheet_name='Pivot_Table')
                        except:
                            pass  # Skip pivot table if it fails
                    
                    st.download_button(
                        label="📊 Download Excel Report",
                        data=excel_buffer.getvalue(),
                        file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Excel export not available: {e}")
        
        with tab4:
            st.subheader("Detailed Financial Data")
            
            # Company selector for detailed view
            selected_company = st.selectbox(
                "Select company for detailed view:",
                options=st.session_state.combined_summary['Company'].unique()
            )
            
            if selected_company:
                company_data = st.session_state.combined_summary[
                    st.session_state.combined_summary['Company'] == selected_company
                ]
                
                st.markdown(f"### {selected_company} Financial Details")
                
                # Display metrics in cards
                metrics = company_data['Metric'].unique()
                
                for metric in metrics:
                    metric_data = company_data[company_data['Metric'] == metric].sort_values('Fiscal Year', ascending=False)
                    
                    st.markdown(f"#### {metric}")
                    
                    # Handle case where there might be more columns than available space
                    max_cols = min(len(metric_data), 5)  # Limit to 5 columns max
                    cols = st.columns(max_cols)
                    
                    for i, (_, row) in enumerate(metric_data.head(max_cols).iterrows()):
                        with cols[i]:
                            value = f"${row['Value']:,.0f}" if pd.notnull(row['Value']) else "N/A"
                            st.metric(
                                label=f"FY {row['Fiscal Year']}",
                                value=value
                            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Data Source:** SEC EDGAR Database | "
        "**Built with:** Streamlit & SEC APIs | "
        "**Note:** Data is for informational purposes only"
    )

if __name__ == "__main__":
    main()