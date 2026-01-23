import os
import gspread
import pdfkit
import smtplib
import datetime
import pandas as pd
import base64
from jinja2 import Template
from email.message import EmailMessage
from oauth2client.service_account import ServiceAccountCredentials

import google.generativeai as genai

def get_gemini_analysis(brand, location, orders, error_pct, kpt, mfr_cancellations=0, kitchen_errors=0):
    """
    Uses Google Gemini AI to analyze kitchen performance and provide improvement tips.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return "AI Analysis: Gemini API Key not configured. Please set GEMINI_API_KEY."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze the following kitchen performance data for {brand} at {location}:
        - Total Orders: {orders}
        - Error Percentage: {error_pct}%
        - Kitchen Prep Time (KPT): {kpt} minutes
        - MFR Cancellations: {mfr_cancellations}
        - Kitchen Errors: {kitchen_errors}

        Provide 3 concise, professional, and actionable recommendations to reduce errors and improve speed.
        Focus on specific issues like cancellations and kitchen-specific errors if they are high.
        Keep the response brief (max 100 words) and formatted as a bulleted list.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis could not be generated: {str(e)}"

def match_input_with_ai(user_input, valid_options, item_type="Brand"):
    """
    Forces the AI to pick exactly one valid option from the list provided.
    """
    if not user_input or not valid_options:
        return user_input

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return user_input 
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a data validation expert. 
        TASK: Match the value "{user_input}" to one item in this list: {valid_options}

        RULES:
        1. You MUST pick the most likely item from the provided list.
        2. Even if it's a partial match or abbreviation, pick the closest one.
        3. Output ONLY the exact string from the list. No quotes, no explanations.
        4. If it's impossible to match, only then return the original "{user_input}".

        MATCH:
        """
        
        response = model.generate_content(prompt)
        match = response.text.strip().strip('"').strip("'")
        
        # Priority 1: Exact or Case-Insensitive Match
        for option in valid_options:
            if str(match).lower() == str(option).lower():
                return option
        
        # Priority 2: Normalized Match (Remove all spaces, hyphens, etc)
        def normalize(s):
            return "".join(e for e in str(s).lower() if e.isalnum())

        normalized_user = normalize(user_input)
        normalized_match = normalize(match)
        
        for option in valid_options:
            norm_opt = normalize(option)
            if normalized_match == norm_opt or normalized_user == norm_opt:
                return option

        # Priority 3: Substring Match
        for option in valid_options:
            if str(user_input).lower() in str(option).lower() or str(option).lower() in str(user_input).lower():
                return option

        return user_input
    except Exception:
        return user_input

def generate_report_from_df(df, brand, location, logo_b64=None):
    """
    Renders a PDF report with flexible column finding and robust row matching.
    """
    # Auto-load logo if none provided and logo.jpg exists
    if not logo_b64 and os.path.exists("logo.jpg"):
        try:
            with open("logo.jpg", "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
        except Exception:
            pass

    # 0. Clean the DataFrame
    df = df.copy().fillna('')
    df.columns = [str(c).strip() for c in df.columns]
    
    # 1. Identify columns dynamically
    def find_col(possible_names):
        # Case 1: Exact Match (stripped)
        for col in df.columns:
            if col.lower() in [p.lower() for p in possible_names]:
                return col
        # Case 2: Partial Match
        for col in df.columns:
            for p in possible_names:
                if p.lower() in col.lower(): return col
        return None

    brand_col = find_col(['Brand', 'Brand Name', 'Company', 'Restaurant'])
    loc_col = find_col(['Location', 'Store', 'Outlet', 'City', 'Area'])

    if not brand_col or not loc_col:
        raise ValueError(f"Could not find Brand or Location columns. Found: {df.columns.tolist()}")

    # 2. AI FUZZY MATCHING
    all_brands = [str(b).strip() for b in df[brand_col].unique() if str(b).strip()]
    all_locations = [str(l).strip() for l in df[loc_col].unique() if str(l).strip()]
    
    corrected_brand = match_input_with_ai(brand, all_brands, "Brand")
    corrected_location = match_input_with_ai(location, all_locations, "Location")
    
    # 3. ROBUST FILTERING
    def normalize_series(series):
        return series.astype(str).str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)

    norm_brand = "".join(e for e in str(corrected_brand).lower() if e.isalnum())
    norm_loc = "".join(e for e in str(corrected_location).lower() if e.isalnum())

    mask = (
        (normalize_series(df[brand_col]) == norm_brand) & 
        (normalize_series(df[loc_col]) == norm_loc)
    )
    filtered_df = df[mask]
    
    # Try 2: Substring Match if Try 1 fails
    if filtered_df.empty:
        mask = (
            (df[brand_col].astype(str).str.lower().str.contains(str(corrected_brand).lower(), na=False)) |
            (normalize_series(df[brand_col]).str.contains(norm_brand, na=False))
        ) & (
            (df[loc_col].astype(str).str.lower().str.contains(str(corrected_location).lower(), na=False)) |
            (normalize_series(df[loc_col]).str.contains(norm_loc, na=False))
        )
        filtered_df = df[mask]

    if filtered_df.empty:
        # Diagnostic: Show available combinations for this brand
        same_brand = df[df[brand_col].astype(str).str.strip().str.lower() == str(corrected_brand).strip().lower()]
        avail_locs = same_brand[loc_col].unique().tolist() if not same_brand.empty else []
        
        err_msg = f"No record found for '{corrected_brand}' at '{corrected_location}'."
        if avail_locs:
            err_msg += f" Available locations for this brand: {avail_locs}"
        else:
            err_msg += f" Brand not found in data. Found: {all_brands[:5]}..."
            
        raise ValueError(err_msg)
        
    row = filtered_df.iloc[0]
    
    # 4. GET AI ANALYSIS
    # Find Orders, Errors, KPT columns dynamically
    orders_col = find_col(['Orders', 'Total Orders']) or 'Orders'
    errors_col = find_col(['Kitchen Errors', 'K-Errors', 'Kitchen Error', 'Errors', 'Total Errors', 'CSR Errors']) or 'Kitchen Errors'
    kpt_col = find_col(['KPT', 'Prep Time', 'Kitchen Prep Time']) or 'KPT'
    email_col = find_col(['Manager_Email', 'Email', 'Manager Email']) or 'Manager_Email'
    
    # New Fields
    mfr_can_col = find_col(['MFR Cancellations', 'Cancellations', 'MFR Can']) or 'MFR Cancellations'

    orders = row.get(orders_col, 0) or 0
    errors = row.get(errors_col, 0) or 0
    kpt = row.get(kpt_col, 0) or 0
    manager_email = row.get(email_col, "No email found") or "No email found"
    
    mfr_cancellations = row.get(mfr_can_col, 0) or 0
    kitchen_errors = errors # User specified they are the same

    error_pct = round((float(errors)/float(orders))*100, 2) if float(orders) > 0 else 0
    k_error_pct = error_pct # Since they are the same
    
    # 5. RENDER PDF
    with open("template.html") as f:
        tmpl = Template(f.read())
    
    html_out = tmpl.render(
        brand=corrected_brand, 
        location=corrected_location, 
        orders=orders,
        error_pct=error_pct,
        kpt=kpt, 
        mfr_cancellations=mfr_cancellations,
        kitchen_errors=kitchen_errors,
        k_error_pct=k_error_pct,
        logo_b64=logo_b64,
        date=datetime.date.today().strftime("%B %d, %Y")
    )
    
    # Path detection for wkhtmltopdf (Windows and Linux)
    config = None
    import shutil
    
    # Try system PATH first
    system_path = shutil.which("wkhtmltopdf")
    if system_path:
        config = pdfkit.configuration(wkhtmltopdf=system_path)
    else:
        # Fallback to common hardcoded paths
        possible_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'/usr/bin/wkhtmltopdf',
            r'/usr/local/bin/wkhtmltopdf'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                config = pdfkit.configuration(wkhtmltopdf=path)
                break
            
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'enable-local-file-access': None,
        'no-outline': None
    }
    
    try:
        pdf = pdfkit.from_string(html_out, False, configuration=config, options=options)
    except Exception as e:
        if "No wkhtmltopdf executable found" in str(e):
            raise RuntimeError("PDF Error: wkhtmltopdf is not installed correctly in the cloud environment.")
        raise e
        
    return pdf, manager_email

def generate_report(brand, location, creds_dict, sheet_identifier="Kitchen_Data", logo_b64=None):
    """
    Fetches data from Google Sheets (by Name, ID, or URL) and calls generate_report_from_df.
    """
    # Cloud Resiliency: Handle potential string-pasting issues
    if isinstance(creds_dict, str):
        try:
            # Fix potential double-escaping from copy-pasting
            clean_json = creds_dict.replace('\\\\', '\\')
            creds_dict = json.loads(clean_json)
        except Exception as e:
            raise ValueError(f"Failed to parse Google Credentials JSON. Please check your secrets formatting. Error: {e}")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    try:
        if "docs.google.com/spreadsheets" in sheet_identifier:
            sheet = client.open_by_url(sheet_identifier).worksheet("Data")
        else:
            sheet = client.open(sheet_identifier).worksheet("Data")
    except Exception:
        # Fallback to first worksheet if "Data" doesn't exist
        if "docs.google.com/spreadsheets" in sheet_identifier:
            sheet = client.open_by_url(sheet_identifier).get_worksheet(0)
        else:
            sheet = client.open(sheet_identifier).get_worksheet(0)
            
    df = pd.DataFrame(sheet.get_all_records())
    
    return generate_report_from_df(df, brand, location, logo_b64=logo_b64)

def send_email(pdf_content, recipient, brand):
    """
    Sends the generated PDF as an attachment via Gmail SMTP.
    """
    msg = EmailMessage()
    msg['Subject'] = f"Weekly Report: {brand}"
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = recipient
    msg.set_content(f"Please find the attached report for {brand}.")
    
    msg.add_attachment(
        pdf_content, 
        maintype='application', 
        subtype='pdf', 
        filename=f"{brand}_Report_{datetime.date.today()}.pdf"
    )

    smtp_user = os.getenv('EMAIL_USER')
    smtp_pass = os.getenv('EMAIL_PASS')
    
    if not smtp_user or not smtp_pass:
        print("Error: EMAIL_USER or EMAIL_PASS environment variables not set.")
        return

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)
