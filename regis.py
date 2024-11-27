import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import datetime
import base64


logo_image = 'images/Picture_2.png'
bg_image = 'images/Picture_BG_resize.png'

# Initialize variables for form inputs
position_list = [
    'Position',
    'กรรมการผู้จัดการ', 'กรรมการบริหาร', 'ที่ปรึกษาอาวุโส', 'ผู้เชี่ยวชาญด้านโบราณคดี',
    'Admin', 'Architect', 'Associate director', 'Cad options', 'Draft man', 'Engineer', 'Interior',
    'Landscape', 'Production', 'Secretary', 'Senior Architect', 'Other'
]

# food_list = ['Meat','Pork']
fname = ""
lname = ""
phone = ""
email = ""
position_idx = 0
# is_allergy = False
# text_food_allergy = ""
# food_selected_idx = 0
found_row = 0

# st.logo('logo.png')
left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image(logo_image, width=200)


# Set the background image
def set_bg_hack(main_bg):
    # set bg name
    main_bg_ext = "png"

    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )


set_bg_hack(bg_image)


# Authenticate and connect to Google Sheets
def connect_to_gsheet(creds_json, spreadsheet_name, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",
             'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)  # Access specific sheet by name


# Google Sheet credentials and details
SPREADSHEET_NAME = 'bluescope_registration_file'
SHEET_NAME = 'Sheet1'
CREDENTIALS_FILE = './credentials.json'

# Connect to the Google Sheet
sheet_by_name = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name=SHEET_NAME)


# Read Data from Google Sheets
def read_data():
    data = sheet_by_name.get_all_records()  # Get all records from Google Sheet
    df = pd.DataFrame(data, dtype=str)
    return df


# Add Data to Google Sheets
def add_data(regis_data):
    # sheet_by_name = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name=SHEET_NAME)
    sheet_by_name.append_row(regis_data)  # Append the row to the Google Sheet


def update_data(update_row, regis_data):
    sheet_by_name.update_cell(update_row, 1, regis_data[0])
    sheet_by_name.update_cell(update_row, 2, regis_data[1])
    sheet_by_name.update_cell(update_row, 3, regis_data[2])
    sheet_by_name.update_cell(update_row, 4, regis_data[3])
    sheet_by_name.update_cell(update_row, 5, regis_data[4])
    # sheet_by_name.update_cell(update_row, 6, regis_data[5])
    # sheet_by_name.update_cell(update_row, 7, regis_data[6])
    # sheet_by_name.update_cell(update_row, 8, regis_data[7])
    # sheet_by_name.update_cell(update_row, 9, regis_data[8])
    sheet_by_name.update_cell(update_row, 6, regis_data[5])


def read_fullnames():
    fnames = sheet_by_name.col_values(1)[1:]
    lnames = sheet_by_name.col_values(2)[1:]
    df = pd.DataFrame()
    df['fnames'] = fnames
    df['lnames'] = lnames
    unique_names = df[['fnames', 'lnames']].drop_duplicates()
    unique_names_list = list(unique_names.itertuples(index=False, name=None))
    names_list = []
    for i in unique_names_list:
        names_list.append(' '.join(i))
    return names_list


# Create tabs
tab1, tab2 = st.tabs(["Registration Form | ", "Regis Information"])

with tab1:
    tab1_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">ลงทะเบียนเข้าร่วมงาน</p>'
    tab1.markdown(tab1_subhader, unsafe_allow_html=True)

    # Select box to choose a registered person
    st.markdown(
        """
        <style>
        div[data-testid="stSelectbox"] > label {
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    names = read_fullnames()
    selected_name = st.selectbox("Select a registered person (optional)", [""] + sorted(names))

    is_update = False
    if selected_name:
        words = selected_name.split()
        print('select:', words)

        selected_user_fname = words[0]
        selected_user_lname = ' '.join(words[1:])
        for found_cell in sheet_by_name.findall(selected_user_fname):
            found_row = found_cell.row
            found_lname = sheet_by_name.cell(found_row, 2).value
            if selected_user_lname == found_lname:
                # do
                is_update = True
                fname = sheet_by_name.cell(found_row, 1).value
                lname = sheet_by_name.cell(found_row, 2).value
                phone = sheet_by_name.cell(found_row, 3).value
                email = sheet_by_name.cell(found_row, 4).value
                position = sheet_by_name.cell(found_row, 5).value
                try:
                    position_idx = position_list.index(position)
                except ValueError:
                    position_idx = 0
                # is_allergy = sheet_by_name.cell(update_row, 6).value
                # text_food_allergy = sheet_by_name.cell(update_row, 7).value
                # food_selected = sheet_by_name.cell(update_row, 8).value
                # try:
                #    food_selected_idx = food_list.index(food_selected)
                # except ValueError:
                #    food_selected_idx = 0
    else:
        is_update = False  # add new

    detail_txt = '<p style="color:White;">Details of selected person:</p>'
    st.markdown(detail_txt, unsafe_allow_html=True)

    # Assuming the sheet has columns: 'Name', 'Age', 'Email'
    with st.form(key="data_form", clear_on_submit=True):
        fname = st.text_input('Enter your first name *', value=fname)
        lname = st.text_input('Enter your last name *', value=lname)
        phone = st.text_input('Enter your phone number', value=phone)
        email = st.text_input('Enter your email', value=email)
        position = st.selectbox('Enter your position', position_list, index=position_idx)
        # food_allergy = st.checkbox("Food Allergy", value=is_allergy)
        # text_food_allergy = st.text_input('Enter your allergy:', value=text_food_allergy)
        # food_selected = st.radio("Select your meal", food_list, index=food_selected_idx)

        # Submit button inside the form
        submitted = st.form_submit_button("Submit")
        # Handle form submission
        if submitted:
            timestamp = datetime.now()
            # regis_data = [fname, lname, str(phone), email, position, food_allergy, text_food_allergy, food_selected, str(timestamp)]
            regis_data = [fname, lname, str(phone), email, position, timestamp.strftime("%d/%m/%Y, %H:%M:%S")]
            print('submit:', regis_data)

            if is_update and fname and lname:
                update_data(found_row, regis_data)
            else:
                if fname and lname:  # Basic validation to check if required fields are filled
                    add_data(regis_data)  # Append the row to the sheet
                    st.success("Data added successfully!")
                else:
                    st.error("Please fill out the form correctly.")
                    st.error("If you want to leave either the first name or last name empty, please fill it with a \"-\" symbol")
    css = """
    <style>
        [data-testid="stForm"] {
            background: White;
        }
    </style>
    """

    st.write(css, unsafe_allow_html=True)


with tab2:
    # Display data in the main view
    tab2_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">แสดงข้อมูลการลงทะเบียนเข้าร่วมงาน</p>'
    tab2.markdown(tab2_subhader, unsafe_allow_html=True)
    df = read_data()
    st.dataframe(df, width=900, height=1000)

css = '''
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Jost">
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.5rem;
    font-family: "Jost", sans-serif;
    color: white;
    }
    .stAppHeader {visibility: hidden;}
</style>
'''

st.markdown(css, unsafe_allow_html=True)
