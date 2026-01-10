"""
🌐 COVENANT COMMAND CENTER - STREAMLIT WEB VERSION
Cloud-deployable version for the hackathon showcase

Deploy to Streamlit Cloud in 5 minutes!
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="Covenant Command Center",
    page_icon="https://covenantcommandcenter.com/logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066CC;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066CC;
    }
    .breach-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #d32f2f;
        margin-bottom: 1rem;
    }
    .warning-alert {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 1rem;
    }
    .success-banner {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Database connection
@st.cache_resource
def get_database_connection():
    """Connect to SQLite database"""
    # For demo purposes, create a sample database
    db_path = "covenant_demo.db"

    # Check if database exists, if not create sample data
    if not os.path.exists(db_path):
        create_sample_database(db_path)

    return db_path


def create_sample_database(db_path):
    """Create sample database for demo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_agreements (
            loan_id INTEGER PRIMARY KEY,
            deal_name TEXT,
            borrower_name TEXT,
            principal_amount REAL,
            interest_rate REAL,
            status TEXT,
            origination_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covenants (
            covenant_id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            covenant_name TEXT,
            covenant_type TEXT,
            threshold_text TEXT,
            current_value TEXT,
            compliance_status TEXT,
            is_active INTEGER,
            updated_at TEXT,
            source_document TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_data (
            financial_id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            reporting_period TEXT,
            total_debt REAL,
            ebitda REAL,
            interest_expense REAL,
            current_assets REAL,
            current_liabilities REAL,
            net_worth REAL,
            upload_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            alert_type TEXT,
            message TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')

    # Insert sample data
    sample_loans = [
        (1, 'Aerospace Credit Facility 2022', 'Aerospace Industries Inc', 50000000, 5.5, 'Active', '2022-01-15'),
        (2, 'Manufacturing Term Loan', 'Global Manufacturing Corp', 30000000, 4.8, 'Active', '2021-06-20'),
        (3, 'Tech Startup Revolver', 'TechCo Innovations', 15000000, 6.2, 'Active', '2023-03-10'),
        (4, 'Real Estate Bridge Loan', 'Property Holdings LLC', 25000000, 5.0, 'Active', '2022-09-01'),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO loan_agreements 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_loans)

    sample_covenants = [
        (1, 1, 'Maximum Leverage Ratio', 'Financial', '≤ 4.50x', '5.20x', 'BREACH', 1, datetime.now().isoformat(),
         'Credit Agreement 2022.pdf'),
        (2, 1, 'Minimum Interest Coverage Ratio', 'Financial', '≥ 3.00x', '2.85x', 'BREACH', 1,
         datetime.now().isoformat(), 'Credit Agreement 2022.pdf'),
        (3, 2, 'Maximum Leverage Ratio', 'Financial', '≤ 3.00x', '2.50x', 'COMPLIANT', 1, datetime.now().isoformat(),
         'Term Loan Agreement.pdf'),
        (4, 3, 'Minimum EBITDA', 'Financial', '≥ $5,000,000', '$6,200,000', 'COMPLIANT', 1, datetime.now().isoformat(),
         'Revolver Agreement.pdf'),
        (5, 4, 'Current Ratio', 'Financial', '≥ 1.20x', '1.15x', 'AT_RISK', 1, datetime.now().isoformat(),
         'Bridge Loan Agreement.pdf'),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO covenants 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_covenants)

    sample_alerts = [
        (1, 1, 'BREACH', 'Leverage Ratio breach detected: 5.20x (Limit: 4.50x)', 'Active', datetime.now().isoformat()),
        (2, 1, 'BREACH', 'Interest Coverage breach detected: 2.85x (Required: 3.00x)', 'Active',
         datetime.now().isoformat()),
        (3, 4, 'WARNING', 'Current Ratio approaching threshold', 'Active', datetime.now().isoformat()),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO alerts 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_alerts)

    conn.commit()
    conn.close()


def load_data(db_path, query):
    """Load data from database"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_portfolio_stats(db_path):
    """Get portfolio statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total loans
    cursor.execute("SELECT COUNT(*) FROM loan_agreements WHERE status = 'Active'")
    total_loans = cursor.fetchone()[0]

    # Total exposure
    cursor.execute("SELECT SUM(principal_amount) FROM loan_agreements WHERE status = 'Active'")
    total_exposure = cursor.fetchone()[0] or 0

    # Active breaches
    cursor.execute("SELECT COUNT(*) FROM covenants WHERE compliance_status = 'BREACH' AND is_active = 1")
    active_breaches = cursor.fetchone()[0]

    # Compliance rate
    cursor.execute("SELECT COUNT(*) FROM covenants WHERE is_active = 1")
    total_covenants = cursor.fetchone()[0]

    if total_covenants > 0:
        compliance = ((total_covenants - active_breaches) / total_covenants) * 100
    else:
        compliance = 100.0

    conn.close()

    return {
        'total_loans': total_loans,
        'total_exposure': total_exposure,
        'active_breaches': active_breaches,
        'compliance': compliance
    }


def get_banner_status(db_path):
    """
    Returns banner with DUAL priorities:
    1. BREACH alerts (RED - highest priority)
    2. UPLOAD REMINDERS (YELLOW/ORANGE - missing data)
    3. UPCOMING TESTS (BLUE - next 7 days)
    4. ALL GOOD (GREEN - everything compliant)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Priority 1: Check for ACTIVE BREACHES
    cursor.execute("""
        SELECT COUNT(*) 
        FROM covenants 
        WHERE compliance_status = 'BREACH' AND is_active = 1
    """)
    breach_count = cursor.fetchone()[0]
    
    # Priority 2: Check for MISSING FINANCIAL DATA
    cursor.execute("""
        SELECT COUNT(*) 
        FROM covenants 
        WHERE is_active = 1 
        AND (current_value IS NULL OR current_value = '' OR current_value = 'N/A')
    """)
    missing_data_count = cursor.fetchone()[0]
    
    # Priority 3: Get UPCOMING TESTS (simulated)
    cursor.execute("""
        SELECT 
            l.deal_name,
            c.covenant_name,
            'Quarterly' as test_frequency
        FROM covenants c
        JOIN loan_agreements l ON c.loan_id = l.loan_id
        WHERE c.is_active = 1
        AND c.compliance_status != 'BREACH'
        LIMIT 3
    """)
    upcoming_tests = cursor.fetchall()
    
    # Get 30-DAY UPCOMING TESTS
    cursor.execute("""
        SELECT 
            l.deal_name,
            c.covenant_name,
            c.covenant_type
        FROM covenants c
        JOIN loan_agreements l ON c.loan_id = l.loan_id
        WHERE c.is_active = 1
        ORDER BY l.deal_name, c.covenant_name
        LIMIT 10
    """)
    upcoming_30_days = cursor.fetchall()
    
    conn.close()
    
    # RETURN BANNER CONFIG
    if breach_count > 0:
        return {
            'type': 'error',
            'icon': '🚨',
            'title': f'{breach_count} COVENANT BREACH(ES) REQUIRE IMMEDIATE ATTENTION',
            'message': 'Review breaches immediately and contact your lender. Breach alerts are automatically generated when financial data is uploaded.',
            'priority': 1,
            'count': breach_count,
            'upcoming_30': upcoming_30_days
        }
    
    elif missing_data_count > 0:
        return {
            'type': 'warning',
            'icon': '⚠️',
            'title': f'{missing_data_count} COVENANT(S) MISSING FINANCIAL DATA - UPLOAD REQUIRED',
            'message': 'Upload quarterly financial statements to enable automatic covenant testing and breach detection. System will calculate compliance immediately upon upload.',
            'priority': 2,
            'count': missing_data_count,
            'upcoming_30': upcoming_30_days
        }
    
    elif len(upcoming_tests) > 0:
        return {
            'type': 'info',
            'icon': '📅',
            'title': f'{len(upcoming_tests)} COVENANT TEST(S) DUE IN NEXT 7 DAYS',
            'message': 'Prepare financial statements for upcoming covenant tests. Upload data early to ensure timely compliance monitoring.',
            'priority': 3,
            'upcoming_tests': upcoming_tests,
            'upcoming_30': upcoming_30_days
        }
    
    else:
        next_upload_days = 25
        return {
            'type': 'success',
            'icon': '✅',
            'title': 'ALL COVENANTS IN COMPLIANCE - NO IMMEDIATE ACTION REQUIRED',
            'message': f'Next financial data upload due in approximately {next_upload_days} days. System is actively monitoring all covenants.',
            'priority': 4,
            'upcoming_30': upcoming_30_days
        }


def show_dashboard_banner(db_path):
    """Display the priority banner on dashboard"""
    banner = get_banner_status(db_path)
    
    # Main banner
    if banner['type'] == 'error':
        st.error(f"### {banner['icon']} {banner['title']}")
        st.markdown(f"**{banner['message']}**")
        
        with st.expander("🔍 View Breach Details"):
            breach_query = """
                SELECT 
                    l.deal_name as 'Loan',
                    c.covenant_name as 'Covenant',
                    c.current_value as 'Current',
                    c.threshold_text as 'Threshold'
                FROM covenants c
                JOIN loan_agreements l ON c.loan_id = l.loan_id
                WHERE c.compliance_status = 'BREACH' AND c.is_active = 1
            """
            conn = sqlite3.connect(db_path)
            breach_df = pd.read_sql_query(breach_query, conn)
            conn.close()
            st.dataframe(breach_df, use_container_width=True, hide_index=True)
    
    elif banner['type'] == 'warning':
        st.warning(f"### {banner['icon']} {banner['title']}")
        st.markdown(f"**{banner['message']}**")
        
        with st.expander("📋 View Covenants Missing Data"):
            missing_query = """
                SELECT 
                    l.deal_name as 'Loan',
                    c.covenant_name as 'Covenant',
                    c.covenant_type as 'Type',
                    c.threshold_text as 'Threshold'
                FROM covenants c
                JOIN loan_agreements l ON c.loan_id = l.loan_id
                WHERE c.is_active = 1 
                AND (c.current_value IS NULL OR c.current_value = '' OR c.current_value = 'N/A')
            """
            conn = sqlite3.connect(db_path)
            missing_df = pd.read_sql_query(missing_query, conn)
            conn.close()
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
            st.info("💡 **Tip:** Go to '📂 Upload Data' to submit financial statements")
    
    elif banner['type'] == 'info':
        st.info(f"### {banner['icon']} {banner['title']}")
        st.markdown(f"**{banner['message']}**")
        
        with st.expander("📅 Upcoming Tests (Next 7 Days)"):
            if 'upcoming_tests' in banner:
                for loan, covenant, freq in banner['upcoming_tests']:
                    days = 3
                    test_date = (datetime.now() + timedelta(days=days)).strftime('%b %d, %Y')
                    st.write(f"• **{loan}** - {covenant} ({freq}) - Due: {test_date}")
    
    else:
        st.success(f"### {banner['icon']} {banner['title']}")
        st.markdown(f"**{banner['message']}**")
    
    # ALWAYS SHOW: 30-Day Upcoming Tests
    st.markdown("---")
    st.markdown("### 📋 UPCOMING COVENANT TESTS (Next 30 Days)")
    st.caption("Financial data uploads enable automatic covenant testing and breach alerts")
    
    if 'upcoming_30' in banner and banner['upcoming_30']:
        upcoming_data = []
        for i, (loan, covenant, cov_type) in enumerate(banner['upcoming_30']):
            days_until = (i + 1) * 3
            test_date = (datetime.now() + timedelta(days=days_until)).strftime('%b %d, %Y')
            upcoming_data.append({
                'Loan': loan,
                'Covenant': covenant,
                'Type': cov_type,
                'Test Date': test_date,
                'Days': f"{days_until} days"
            })
        
        upcoming_df = pd.DataFrame(upcoming_data)
        st.dataframe(upcoming_df, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming covenant tests scheduled")


# Initialize database
db_path = get_database_connection()

# Sidebar
with st.sidebar:
    # Logo at top
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("### 🏦 Covenant Command Center")
    
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📋 Covenant Status", "🔔 Alerts", "📂 Upload Data", "📈 Analytics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")
    stats = get_portfolio_stats(db_path)
    st.metric("Total Loans", stats['total_loans'])
    st.metric("Active Breaches", stats['active_breaches'],
              delta=None if stats['active_breaches'] == 0 else f"-{stats['active_breaches']}", delta_color="inverse")
    st.metric("Compliance Rate", f"{stats['compliance']:.1f}%")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("**Covenant Command Center** automates loan covenant monitoring and breach detection.")

    st.markdown("---")
    st.markdown("**Demo Version**")
    st.caption("Built for Hackathon 2026")

# Main content
if page == "📊 Dashboard":
    st.markdown('<p class="main-header">📊 Portfolio Dashboard</p>', unsafe_allow_html=True)

    # Show priority banner system
    show_dashboard_banner(db_path)
    
    st.markdown("---")

    # Portfolio metrics
    st.markdown("### 📈 Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💼 Total Loans",
            stats['total_loans'],
            delta=None,
            help="Number of active loans in portfolio"
        )

    with col2:
        exposure_m = stats['total_exposure'] / 1_000_000
        st.metric(
            "💰 Total Exposure",
            f"${exposure_m:.0f}M",
            delta=None,
            help="Total principal amount outstanding"
        )

    with col3:
        st.metric(
            "🔔 Active Alerts",
            stats['active_breaches'],
            delta=f"-{stats['active_breaches']}" if stats['active_breaches'] > 0 else None,
            delta_color="inverse",
            help="Covenants currently in breach"
        )

    with col4:
        st.metric(
            "✅ Compliance",
            f"{stats['compliance']:.0f}%",
            delta=None,
            help="Percentage of covenants in compliance"
        )

    # Covenant status table
    st.markdown("### 📋 Covenant Status by Loan")
    covenant_query = """
        SELECT 
            l.deal_name as 'Loan',
            l.borrower_name as 'Borrower',
            c.covenant_name as 'Covenant',
            c.covenant_type as 'Type',
            c.compliance_status as 'Status',
            c.current_value as 'Current Value',
            c.threshold_text as 'Threshold'
        FROM covenants c
        LEFT JOIN loan_agreements l ON c.loan_id = l.loan_id
        WHERE c.is_active = 1
        ORDER BY 
            CASE c.compliance_status
                WHEN 'BREACH' THEN 1
                WHEN 'AT_RISK' THEN 2
                WHEN 'COMPLIANT' THEN 3
                ELSE 4
            END
    """
    covenant_df = load_data(db_path, covenant_query)


    # Color code the status column
    def highlight_status(row):
        if row['Status'] == 'BREACH':
            return ['background-color: #ffebee'] * len(row)
        elif row['Status'] == 'AT_RISK':
            return ['background-color: #fff3e0'] * len(row)
        elif row['Status'] == 'COMPLIANT':
            return ['background-color: #e8f5e9'] * len(row)
        else:
            return [''] * len(row)


    styled_df = covenant_df.style.apply(highlight_status, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # Recent alerts
    st.markdown("### 🔔 Recent Alerts")
    alerts_query = """
        SELECT 
            a.created_at as 'Date',
            l.deal_name as 'Loan',
            a.alert_type as 'Type',
            a.message as 'Message',
            a.status as 'Status'
        FROM alerts a
        JOIN loan_agreements l ON a.loan_id = l.loan_id
        ORDER BY a.created_at DESC
        LIMIT 5
    """
    alerts_df = load_data(db_path, alerts_query)

    if len(alerts_df) > 0:
        for _, alert in alerts_df.iterrows():
            if alert['Type'] == 'BREACH':
                st.error(f"**{alert['Loan']}** - {alert['Message']}")
            elif alert['Type'] == 'WARNING':
                st.warning(f"**{alert['Loan']}** - {alert['Message']}")
            else:
                st.info(f"**{alert['Loan']}** - {alert['Message']}")
    else:
        st.info("No recent alerts")

elif page == "📋 Covenant Status":
    st.markdown('<p class="main-header">📋 Covenant Status</p>', unsafe_allow_html=True)

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["BREACH", "AT_RISK", "COMPLIANT", "NOT_TESTED"],
            default=["BREACH", "AT_RISK", "COMPLIANT"]
        )

    with col2:
        loan_query = "SELECT DISTINCT deal_name FROM loan_agreements ORDER BY deal_name"
        loans = load_data(db_path, loan_query)
        loan_filter = st.multiselect(
            "Filter by Loan",
            loans['deal_name'].tolist(),
            default=None
        )

    with col3:
        covenant_type_filter = st.multiselect(
            "Filter by Type",
            ["Financial", "Reporting", "Negative", "Affirmative"],
            default=["Financial"]
        )

    # Build query with filters
    where_clauses = []
    if status_filter:
        status_list = "','".join(status_filter)
        where_clauses.append(f"c.compliance_status IN ('{status_list}')")
    if loan_filter:
        loan_list = "','".join(loan_filter)
        where_clauses.append(f"l.deal_name IN ('{loan_list}')")
    if covenant_type_filter:
        type_list = "','".join(covenant_type_filter)
        where_clauses.append(f"c.covenant_type IN ('{type_list}')")

    where_clause = " AND " + " AND ".join(where_clauses) if where_clauses else ""

    covenant_query = f"""
        SELECT 
            l.deal_name as 'Loan',
            l.borrower_name as 'Borrower',
            c.covenant_name as 'Covenant Name',
            c.covenant_type as 'Type',
            c.compliance_status as 'Status',
            c.current_value as 'Current Value',
            c.threshold_text as 'Threshold',
            c.source_document as 'Source Document'
        FROM covenants c
        LEFT JOIN loan_agreements l ON c.loan_id = l.loan_id
        WHERE c.is_active = 1 {where_clause}
        ORDER BY 
            CASE c.compliance_status
                WHEN 'BREACH' THEN 1
                WHEN 'AT_RISK' THEN 2
                WHEN 'COMPLIANT' THEN 3
                ELSE 4
            END,
            l.deal_name
    """

    covenant_df = load_data(db_path, covenant_query)

    st.markdown(f"**Showing {len(covenant_df)} covenant(s)**")


    def highlight_status(row):
        if row['Status'] == 'BREACH':
            return ['background-color: #ffebee'] * len(row)
        elif row['Status'] == 'AT_RISK':
            return ['background-color: #fff3e0'] * len(row)
        elif row['Status'] == 'COMPLIANT':
            return ['background-color: #e8f5e9'] * len(row)
        else:
            return [''] * len(row)


    styled_df = covenant_df.style.apply(highlight_status, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

    # Export button
    csv = covenant_df.to_csv(index=False)
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name="covenant_status.csv",
        mime="text/csv"
    )

elif page == "🔔 Alerts":
    st.markdown('<p class="main-header">🔔 Alerts & Notifications</p>', unsafe_allow_html=True)

    # Alert summary
    alerts_summary_query = """
        SELECT 
            alert_type,
            COUNT(*) as count
        FROM alerts
        WHERE status = 'Active'
        GROUP BY alert_type
    """
    summary = load_data(db_path, alerts_summary_query)

    col1, col2, col3 = st.columns(3)
    breach_count = summary[summary['alert_type'] == 'BREACH']['count'].sum() if 'BREACH' in summary[
        'alert_type'].values else 0
    warning_count = summary[summary['alert_type'] == 'WARNING']['count'].sum() if 'WARNING' in summary[
        'alert_type'].values else 0
    info_count = summary[summary['alert_type'] == 'INFO']['count'].sum() if 'INFO' in summary[
        'alert_type'].values else 0

    with col1:
        st.metric("🚨 Breach Alerts", int(breach_count))
    with col2:
        st.metric("⚠️ Warning Alerts", int(warning_count))
    with col3:
        st.metric("ℹ️ Info Alerts", int(info_count))

    # Filters
    alert_type_filter = st.multiselect(
        "Filter by Type",
        ["BREACH", "WARNING", "INFO", "CRITICAL"],
        default=["BREACH", "WARNING"]
    )

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Active", "Resolved", "Dismissed"]
    )

    # Build query
    type_clause = ""
    if alert_type_filter:
        type_list = "','".join(alert_type_filter)
        type_clause = f"AND a.alert_type IN ('{type_list}')"

    status_clause = "" if status_filter == "All" else f"AND a.status = '{status_filter}'"

    alerts_query = f"""
        SELECT 
            a.created_at as 'Date',
            l.deal_name as 'Loan',
            l.borrower_name as 'Borrower',
            a.alert_type as 'Type',
            a.message as 'Message',
            a.status as 'Status'
        FROM alerts a
        JOIN loan_agreements l ON a.loan_id = l.loan_id
        WHERE 1=1 {type_clause} {status_clause}
        ORDER BY 
            CASE a.alert_type
                WHEN 'BREACH' THEN 1
                WHEN 'CRITICAL' THEN 2
                WHEN 'WARNING' THEN 3
                ELSE 4
            END,
            a.created_at DESC
    """

    alerts_df = load_data(db_path, alerts_query)

    st.markdown(f"**Showing {len(alerts_df)} alert(s)**")

    # Display alerts as cards
    for _, alert in alerts_df.iterrows():
        with st.container():
            if alert['Type'] == 'BREACH':
                st.error(f"""
                **🚨 {alert['Type']}** - {alert['Date'][:10]}  
                **Loan:** {alert['Loan']} ({alert['Borrower']})  
                **Message:** {alert['Message']}  
                **Status:** {alert['Status']}
                """)
            elif alert['Type'] == 'WARNING':
                st.warning(f"""
                **⚠️ {alert['Type']}** - {alert['Date'][:10]}  
                **Loan:** {alert['Loan']} ({alert['Borrower']})  
                **Message:** {alert['Message']}  
                **Status:** {alert['Status']}
                """)
            else:
                st.info(f"""
                **ℹ️ {alert['Type']}** - {alert['Date'][:10]}  
                **Loan:** {alert['Loan']} ({alert['Borrower']})  
                **Message:** {alert['Message']}  
                **Status:** {alert['Status']}
                """)

elif page == "📂 Upload Data":
    st.markdown('<p class="main-header">📂 Upload Financial Data</p>', unsafe_allow_html=True)

    st.info(
        "This is a demo version. In the full application, you can upload quarterly financial statements to trigger covenant testing.")

    # Loan selection
    loan_query = "SELECT loan_id, deal_name, borrower_name FROM loan_agreements WHERE status = 'Active' ORDER BY deal_name"
    loans = load_data(db_path, loan_query)

    selected_loan = st.selectbox(
        "Select Loan",
        loans['deal_name'].tolist()
    )

    # Period selection
    current_year = datetime.now().year
    periods = [f"{year}-Q{q}" for year in range(current_year - 2, current_year + 1) for q in range(1, 5)]
    selected_period = st.selectbox("Select Reporting Period", periods, index=len(periods) - 1)

    # File upload
    st.markdown("### Upload Financial Statement")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['xlsx', 'xls', 'csv'])

    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        # In real version, would parse file and extract financial metrics
        st.markdown("### Financial Metrics (Demo)")

        col1, col2 = st.columns(2)
        with col1:
            total_debt = st.number_input("Total Debt ($)", value=45000000, format="%d")
            ebitda = st.number_input("EBITDA ($)", value=8500000, format="%d")
            interest_expense = st.number_input("Interest Expense ($)", value=3000000, format="%d")

        with col2:
            current_assets = st.number_input("Current Assets ($)", value=15000000, format="%d")
            current_liabilities = st.number_input("Current Liabilities ($)", value=12000000, format="%d")
            net_worth = st.number_input("Net Worth ($)", value=25000000, format="%d")

        if st.button("🔍 Calculate Covenants", type="primary"):
            with st.spinner("Analyzing financial data and testing covenants..."):
                import time

                time.sleep(2)  # Simulate processing

                st.success("✅ Covenant testing complete!")

                # Show sample results
                st.markdown("### Covenant Test Results")

                leverage = total_debt / ebitda if ebitda > 0 else 0
                interest_coverage = ebitda / interest_expense if interest_expense > 0 else 0
                current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0

                results = [
                    {"Covenant": "Maximum Leverage Ratio", "Threshold": "≤ 4.50x", "Actual": f"{leverage:.2f}x",
                     "Status": "BREACH" if leverage > 4.5 else "COMPLIANT"},
                    {"Covenant": "Minimum Interest Coverage", "Threshold": "≥ 3.00x",
                     "Actual": f"{interest_coverage:.2f}x",
                     "Status": "BREACH" if interest_coverage < 3.0 else "COMPLIANT"},
                    {"Covenant": "Minimum Current Ratio", "Threshold": "≥ 1.20x", "Actual": f"{current_ratio:.2f}x",
                     "Status": "COMPLIANT" if current_ratio >= 1.2 else "AT_RISK"},
                ]

                results_df = pd.DataFrame(results)


                def highlight_status(row):
                    if row['Status'] == 'BREACH':
                        return ['background-color: #ffebee'] * len(row)
                    elif row['Status'] == 'AT_RISK':
                        return ['background-color: #fff3e0'] * len(row)
                    else:
                        return ['background-color: #e8f5e9'] * len(row)


                styled_results = results_df.style.apply(highlight_status, axis=1)
                st.dataframe(styled_results, use_container_width=True, hide_index=True)

                # Show breach alert if any
                breaches = results_df[results_df['Status'] == 'BREACH']
                if len(breaches) > 0:
                    st.error(f"🚨 {len(breaches)} covenant breach(es) detected! Alerts have been sent to stakeholders.")

elif page == "📈 Analytics":
    st.markdown('<p class="main-header">📈 Portfolio Analytics</p>', unsafe_allow_html=True)

    st.info("📊 Advanced analytics dashboard coming soon!")

    st.markdown("""
    ### Planned Features:
    - 📉 Trend analysis of covenant performance over time
    - 🎯 Predictive breach warnings using machine learning
    - 📊 Portfolio risk scoring
    - 📈 Industry benchmark comparisons
    - 📉 Waterfall charts for covenant movements
    - 🗺️ Geographic risk heat maps
    """)

    # Sample chart
    st.markdown("### Covenant Compliance Trend (Sample)")

    chart_data = pd.DataFrame({
        'Quarter': ['2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4', '2026-Q1'],
        'Compliance Rate': [98, 97, 95, 94, 96]
    })

    st.line_chart(chart_data.set_index('Quarter'))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Covenant Command Center</strong> - Built for Hackathon 2026</p>
    <p>AI-powered loan covenant monitoring | Saving banks 100+ hours per quarter</p>
</div>
""", unsafe_allow_html=True)
