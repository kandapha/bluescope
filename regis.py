import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64


logo_image = 'images/Picture_2.png'
bg_image = 'images/Picture_BG_resize.png'

# Initialize variables for form inputs
position_list = [
    'Position',
    'กรรมการผู้จัดการ',
    'กรรมการบริหาร',
    'ที่ปรึกษาอาวุโส',
    'ผู้เชี่ยวชาญด้านโบราณคดี',
    'Admin',
    'Architect',
    'Associate director',
    'Cad options',
    'Draft man',
    'Engineer',
    'Interior',
    'Landscape',
    'Production',
    'Secretary',
    'Senior Architect',
    'Draftsman',
    'Senior landscape architect',
    'Landscape',
    'Landscape Designer',
    'Associate director',
    'Cad Options',
    'Production',
    'Site Supervisor',
    'Design Manager',
    'Other'
]


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
SHEET_NAME = 'participants'
CREDENTIALS_FILE = './credentials.json'  # Google Sheet credentials and details
gsheet_participants = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name=SHEET_NAME)


# Read data from Google Sheets
def read_data():
    data = gsheet_participants.get_all_records()  # Get all records from Google Sheet
    df = pd.DataFrame(data, dtype=str)
    return df


# Add data to Google Sheets
def add_data(regis_data):
    # gsheet_participants = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name=SHEET_NAME)
    gsheet_participants.append_row(regis_data)  # Append the row to the Google Sheet


# Read cell data
@st.cache_data
def read_cell(row, col):
    return gsheet_participants.cell(row, col).value


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


# Read full-name
def read_fullnames():
    fnames = gsheet_participants.col_values(1)[1:]
    lnames = gsheet_participants.col_values(2)[1:]

    # print(fnames, len(fnames))
    # print(lnames, len(lnames))
    # FIXME: Should no one missing name or surname since submission
    if len(fnames) > len(lnames):
        lnames += [''] * (len(fnames) - len(lnames))
    if len(fnames) < len(lnames):
        fnames += [''] * (len(lnames) - len(fnames))

    df = pd.DataFrame()
    df['fnames'] = fnames
    df['lnames'] = lnames
    unique_names = df[['fnames', 'lnames']].drop_duplicates()
    unique_names_list = list(unique_names.itertuples(index=False, name=None))
    names_list = []
    for i in unique_names_list:
        names_list.append(' '.join(i))
    return sorted([""] + names_list)


# Fragment: Registration Form
def registration_form(tab):
    tab_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">ลงทะเบียนเข้าร่วมงาน</p>'
    tab.markdown(tab_subhader, unsafe_allow_html=True)

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
    fname = ""
    lname = ""
    phone = ""
    email = ""
    position_idx = 0
    # food_selected_idx = 0
    found_row = 0

    print("time(before selected_name): %s", time.time())

    st.session_state.all_names = read_fullnames()
    selected_name = st.selectbox("Select a registered person (optional)", st.session_state.all_names)

    is_update = False
    if selected_name:
        words = selected_name.split()

        print("time(after selected_name): %s", time.time())
        print('select:', words)

        selected_user_fname = words[0]
        selected_user_lname = ' '.join(words[1:])

        for found_row, found_cell in [ (i+1, n) for i, n in enumerate(gsheet_participants.col_values(1)) if n == selected_user_fname ]:
            print("time(found fnames): %s", time.time())

            row = gsheet_participants.row_values(found_row)
            found_lname = row[1]
            if selected_user_lname == found_lname:
                is_update = True
                fname = row[0]
                lname = row[1]
                phone = row[2]
                email = row[3]
                position = row[4]
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

            print("time(after read row): %s", time.time())
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

            if fname and lname:  # Basic validation to check if required fields are filled
                if is_update:
                    update_data(found_row, regis_data)
                else:
                    add_data(regis_data)  # Append the row to the sheet
                    st.success("Data added successfully!")

                st.session_state.all_names = read_fullnames()
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
def registration_info(tab):
    # Display data in the main view
    tab_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">แสดงข้อมูลการลงทะเบียนเข้าร่วมงาน</p>'
    tab.markdown(tab_subhader, unsafe_allow_html=True)
    st.dataframe(read_data(), width=900, height=1000)


# -----------------------------------------------------------------------------
# Create tabs
tab1, tab2 = st.tabs(["Registration Form | ", "Regis Information"])
with tab1:
    registration_form(tab1)
with tab2:
    registration_info(tab2)


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
