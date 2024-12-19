import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64


logo_image = 'images/logo_2.png'
background_image = 'images/background_resize.png'

# Initialize variables for form inputs
# position_list = [
#     'Position',
#     'กรรมการผู้จัดการ',
#     'กรรมการบริหาร',
#     'ที่ปรึกษาอาวุโส',
#     'ผู้เชี่ยวชาญด้านโบราณคดี',
#     'Admin',
#     'Architect',
#     'Associate director',
#     'Cad options',
#     'Draft man',
#     'Engineer',
#     'Interior',
#     'Landscape',
#     'Production',
#     'Secretary',
#     'Senior Architect',
#     'Draftsman',
#     'Senior landscape architect',
#     'Landscape',
#     'Landscape Designer',
#     'Associate director',
#     'Cad Options',
#     'Production',
#     'Site Supervisor',
#     'Design Manager',
#     'Other'
# ]


# st.logo('logo.png')
left_column, center_column, right_column = st.columns(3)
with center_column:
    st.image(logo_image, width=200)


# Set the background image
def set_background_hack(main_background):
    # set bg name
    main_background_extension = "png"

    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_background_extension};base64,{base64.b64encode(open(main_background, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )


set_background_hack(background_image)


# Connect to the Google Sheet
def connect_to_gsheet(creds_json, spreadsheet_name, sheet_name):  # Authenticate and connect to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",
             'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)  # Access specific sheet by name


SPREADSHEET_NAME = 'bluescope_registration_file'
CREDENTIALS_FILE = './credentials.json'  # Google Sheet credentials and details
gsheet_participants = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name='participants')
gsheet_positions = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name='positions')


# Safe lite to prevent accessing a missing item
class safelist(list):
    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default


# Read cell data
@st.cache_data
def read_cell(row, col):
    return gsheet_participants.cell(row, col).value


# Read row data
@st.cache_data
def read_row(row):
    return gsheet_participants.row_values(row)


# Read col data
@st.cache_data
def read_col(col):
    return gsheet_participants.col_values(col)


# Read full-name
@st.cache_data
def read_names():
    first_names = gsheet_participants.col_values(1)[1:]
    last_names = gsheet_participants.col_values(2)[1:]

    # FIXME: Should no one missing name or surname since submission
    if len(first_names) > len(last_names):
        last_names += [''] * (len(first_names) - len(last_names))
    if len(first_names) < len(last_names):
        first_names += [''] * (len(last_names) - len(first_names))

    df = pd.DataFrame()
    df['first_name'] = first_names
    df['last_name'] = last_names
    unique_names_df = df[['first_name', 'last_name']].drop_duplicates()
    unique_names_list = list(unique_names_df.itertuples(index=False, name=None))
    return sorted([''] + [' '.join(i) for i in unique_names_list])


# Read positions
@st.cache_data
def read_positions():
    print('Press C button for clearing cache, then ctrl-r for refreshing the browser')
    return gsheet_positions.col_values(1)


# Update data
def update_data(update_row, regis_data):
    gsheet_participants.update_cell(update_row, 1, regis_data[0].strip())
    gsheet_participants.update_cell(update_row, 2, regis_data[1].strip())
    gsheet_participants.update_cell(update_row, 3, regis_data[2])
    gsheet_participants.update_cell(update_row, 4, regis_data[3])
    gsheet_participants.update_cell(update_row, 5, regis_data[4])
    # gsheet_participants.update_cell(update_row, 6, regis_data[5])
    # gsheet_participants.update_cell(update_row, 7, regis_data[6])
    # gsheet_participants.update_cell(update_row, 8, regis_data[7])
    # gsheet_participants.update_cell(update_row, 9, regis_data[8])
    gsheet_participants.update_cell(update_row, 6, regis_data[5])

    # Clear cache
    read_cell.clear()
    read_col.clear()
    read_row.clear()
    read_names.clear()


# Add data to Google Sheets
def add_data(regis_data):
    gsheet_participants.append_row(regis_data)  # Append the row to the Google Sheet

    # Clear cache
    read_cell.clear()
    read_col.clear()
    read_row.clear()
    read_names.clear()


# Read data from Google Sheets
def read_data():
    data = gsheet_participants.get_all_records()  # Get all records from Google Sheet
    df = pd.DataFrame(data, dtype=str)
    return df


# Fragment: Registration Form
@st.fragment()
def registration_form():
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

    # food_list = ['Meat','Pork']
    first_name = ""
    last_name = ""
    phone = ""
    email = ""
    position_idx = 0
    # food_selected_idx = 0
    found_row_index = 0

    print("time(reg_form get started..): %s", time.time())

    st.session_state.all_names = read_names()
    # selected_name = st.selectbox("Select a registered person (optional)", st.session_state.all_names)
    selected_name = st.selectbox("Select a registered person (optional)", read_names())
    print("time(reg_form got selected_name): %s", time.time())

    position_list = read_positions()
    print("time(reg_form got position_list): %s", time.time())

    is_update = False
    if selected_name:
        words = selected_name.split()
        print('select:', words)

        selected_first_name = words[0]
        selected_last_name = ' '.join(words[1:])

        for found_row_index, found_cell in [ (i+1, n) for i, n in enumerate(read_col(1)) if n == selected_first_name ]:
            print("time(reg_form yield cell containing selected_first_name): %s", time.time())

            row = read_row(found_row_index)
            print(f'read_row got {type(row)} len:{len(row)}')
            row = safelist(row)

            found_last_name = row.get(1, '')
            if selected_last_name == found_last_name:
                is_update = True
                first_name  = row.get(0, '')
                last_name   = row.get(1, '')
                phone       = row.get(2, '')
                email       = row.get(3, '')
                position    = row.get(4, '')
                try:
                    position_idx = position_list.index(position)
                except ValueError:
                    position_idx = 0
                # is_allergy = read_cell(update_row, 6)
                # text_food_allergy = read_cell(update_row, 7)
                # food_selected = read_cell(update_row, 8)
                # try:
                #    food_selected_idx = food_list.index(food_selected)
                # except ValueError:
                #    food_selected_idx = 0

                print("time(reg_form found cell with selected name): %s", time.time())
    else:
        is_update = False  # add new

    detail_txt = '<p style="color:White;">Details of selected person:</p>'
    st.markdown(detail_txt, unsafe_allow_html=True)

    # Assuming the sheet has columns: 'Name', 'Age', 'Email'
    with st.form(key="data_form", clear_on_submit=True):
        first_name = st.text_input('Enter your first name *', value=first_name)
        last_name = st.text_input('Enter your last name *', value=last_name)
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
            regis_data = [first_name, last_name, str(phone), email, position, timestamp.strftime("%d/%m/%Y, %H:%M:%S")]
            print('submit:', regis_data)

            if first_name and last_name:  # Basic validation to check if required fields are filled
                if is_update:
                    update_data(found_row_index, regis_data)
                else:
                    add_data(regis_data)  # Append the row to the sheet
                    st.success("Data added successfully!")

                st.session_state.all_names = read_names()
                st.rerun()  # Force rerun to refresh the selectbox
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


# Fragment: Registration Info
@st.fragment()
def registration_info():
    st.dataframe(read_data(), width=900, height=1000)


# -----------------------------------------------------------------------------
# Create tabs
tab1, tab2 = st.tabs(["Registration Form | ", "Regis Information"])
with tab1:
    tab1_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">ลงทะเบียนเข้าร่วมงาน</p>'
    tab1.markdown(tab1_subhader, unsafe_allow_html=True)
    registration_form()
with tab2:
    tab2_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">แสดงข้อมูลการลงทะเบียนเข้าร่วมงาน</p>'
    tab2.markdown(tab2_subhader, unsafe_allow_html=True)
    registration_info()


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
