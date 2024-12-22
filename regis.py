import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64
from threading import Lock


logo_image = 'images/logo_2.png'
background_image = 'images/background_resize.png'


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
def connect_to_gsheet(creds_json, spreadsheet_name):  # Authenticate and connect to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",
             'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet


SPREADSHEET_NAME = 'bluescope_registration_file'
CREDENTIALS_FILE = './credentials.json'  # Google Sheet credentials and details
if 'gsheet' not in st.session_state:
    st.session_state.gsheet = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME)
# if 'gsheet_participants' not in st.session_state:
#     st.session_state.gsheet_participants = st.session_state.gsheet.worksheet('participants')
gsheet_participants = st.session_state.gsheet.worksheet('participants')
# if 'gsheet_positions' not in st.session_state:
#     st.session_state.gsheet_positions = st.session_state.gsheet.worksheet('positions')
gsheet_positions = st.session_state.gsheet.worksheet('positions')


# Safe lite to prevent accessing a missing item
class safelist(list):
    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default


# Read cell data
read_cell_lock = Lock()

@st.cache_data
def read_cell(row, col):
    with read_cell_lock: return gsheet_participants.cell(row, col).value


# Read row data
read_row_lock = Lock()

@st.cache_data
def read_row(row):
    with read_row_lock: return gsheet_participants.row_values(row)


# Read col data
read_col_lock = Lock()

@st.cache_data
def read_col(col):
    with read_col_lock: return gsheet_participants.col_values(col)


# Read full-name
read_names_lock = Lock()

@st.cache_data
def read_names():
    with read_names_lock:
        first_names = read_col(1)[1:]
        last_names = read_col(2)[1:]

        # FIXME: Should no missing name or surname since submission
        if len(first_names) > len(last_names):
            last_names += [''] * (len(first_names) - len(last_names))
        if len(first_names) < len(last_names):
            first_names += [''] * (len(last_names) - len(first_names))

        df = pd.DataFrame()
        df['first_name'] = first_names
        df['last_name'] = last_names
        unique_names_df = df[['first_name', 'last_name']].drop_duplicates()
        unique_names_list = list(unique_names_df.itertuples(index=False, name=None))  # Make list of tuples
        return sorted([''] + [' '.join(i) for i in unique_names_list])  # Cancatenate names+surnames, and, lead them with blank item


# Read positions
# Its cache can be cleared with 'c' key
@st.cache_data
def read_positions():
    print('Press C button for clearing cache, then ctrl-r for refreshing the browser')
    return gsheet_positions.col_values(1)


# Update data
def update_data(row_index, regis_data):

    ## Old method to update data
    # gsheet_participants.update_cell(row_index, 1, regis_data[0])  # first_name
    # gsheet_participants.update_cell(row_index, 2, regis_data[1])  # last_name
    # gsheet_participants.update_cell(row_index, 3, regis_data[2])  # phone
    # gsheet_participants.update_cell(row_index, 4, regis_data[3])  # email
    # gsheet_participants.update_cell(row_index, 5, regis_data[4])  # position
    # gsheet_participants.update_cell(row_index, 6, regis_data[5])  # timestamp

    ## New method to update data
    def column_number_to_letter(column):
        result = ''
        while column > 0:
            column, remainder = divmod(column - 1, 26)
            result = chr(remainder + 65) + result
        return result

    values = [
        # ["Product", "Price", "Quantity"],
        # ["Apples", 1.2, 10],
        # ["Oranges", 0.8, 15],
        # ["Bananas", 0.5, 20],
        regis_data,
    ]
    num_rows = len(values)
    num_cols = len(values[0])
    start_row = row_index
    start_col = 1

    start_cell = f'{column_number_to_letter(start_col)}{start_row}'
    end_cell = f'{column_number_to_letter(start_col + num_cols - 1)}{start_row + num_rows - 1}'
    range_to_update = f'{start_cell}:{end_cell}'

    gsheet_participants.update(range_to_update, values)

    ## Clear cache
    with read_cell_lock:
        for i in range(1, 7):
            read_cell.clear(row_index, i)

    with read_col_lock: read_col.clear()
    with read_row_lock: read_row.clear(row_index)
    with read_names_lock: read_names.clear()


# Add data to Google Sheets
def add_data(regis_data):
    gsheet_participants.append_row(regis_data)  # Append the row to the Google Sheet

    ## Clear cache
    # read_cell.clear()
    with read_col_lock: read_col.clear()
    # read_row.clear()
    with read_names_lock: read_names.clear()


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

    first_name      = '' if 'first_name'    not in st.session_state else st.session_state.first_name
    last_name       = '' if 'last_name'     not in st.session_state else st.session_state.last_name
    phone           = '' if 'phone'         not in st.session_state else st.session_state.phone
    email           = '' if 'email'         not in st.session_state else st.session_state.email
    position_idx    = 0 if 'position_idx'   not in st.session_state else st.session_state.position_idx
    found_row_index = 0 if 'found_row_index' not in st.session_state else st.session_state.found_row_index

    print(f'time(reg_form get started..): @{time.time()}')

    # Provide a selectbox to choose a registered person
    fullnames = read_names()
    selected_index = None
    if st.session_state.get('added_fullname', None):
        # TODO: if needed to select the last added person
        # selected_index = fullnames.index(st.session_state['added_fullname'])
        st.session_state['added_fullname'] = None
    selected_fullname = st.selectbox('Select a registered person (optional)',
                                     options=fullnames,
                                     index=selected_index,
                                     )
    print(f'time(reg_form got selected_fullname): {selected_fullname} @{time.time()}')

    position_list = read_positions()
    print(f'time(reg_form got position_list): @{time.time()}')

    is_update = False  # Will do updating if true else do adding
    if selected_fullname:
        words = selected_fullname.split()
        print('selected guest:', words)

        selected_first_name = words[0]
        selected_last_name = ' '.join(words[1:])

        for found_row_index, found_cell in [ (i+1, n) for i, n in enumerate(read_col(1)) if n == selected_first_name ]:
            print(f'time(reg_form yield cell containing selected_first_name): {found_row_index} @{time.time()}')

            row = read_row(found_row_index)
            # print(f'read_row got {type(row)} len:{len(row)}')
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

                st.session_state['first_name']      = first_name
                st.session_state['last_name']       = last_name
                st.session_state['phone']           = phone
                st.session_state['email']           = email
                st.session_state['position_idx']    = position_idx
                st.session_state['found_row_index'] = found_row_index
                st.session_state['added_fullname'] = None

                print(f'time(reg_form found cell with selected name): {selected_fullname} @{time.time()}')

    detail_txt = '<p style="color:White;">Details of selected person:</p>'
    st.markdown(detail_txt, unsafe_allow_html=True)

    # Form to enter registration details
    with st.form(key="data_form", clear_on_submit=True):  # Assume the sheet has columns: 'Name', 'Age', 'Email'
        first_name  = st.text_input('Enter your first name *', value=first_name).strip()
        last_name   = st.text_input('Enter your last name *',  value=last_name).strip()
        phone       = st.text_input('Enter your phone number', value=phone)
        email       = st.text_input('Enter your email',        value=email)
        position    = st.selectbox('Enter your position', options=position_list, index=position_idx)
        # food_allergy = st.checkbox("Food Allergy", value=is_allergy)
        # text_food_allergy = st.text_input('Enter your allergy:', value=text_food_allergy)
        # food_selected = st.radio("Select your meal", food_list, index=food_selected_idx)

        # Submit button inside the form
        submitted = st.form_submit_button("Submit")

        # Handle form submission
        if submitted:
            timestamp = datetime.now()
            regis_data = [first_name, last_name, str(phone), email, position, timestamp.strftime("%d/%m/%Y, %H:%M:%S")]
            print('submit:', regis_data)

            if first_name and last_name:  # Basic validation to check if required fields are filled
                if is_update:
                    update_data(found_row_index, regis_data)
                    st.success(f'Data updated!')
                    print(f'Data updated! @row:{found_row_index} with {regis_data}')
                else:
                    add_data(regis_data)  # Append the row to the sheet
                    st.success("Data added successfully!")
                    print(f'Data added! with {regis_data}')

                st.session_state['first_name']      = first_name
                st.session_state['last_name']       = last_name
                st.session_state['phone']           = phone
                st.session_state['email']           = email
                st.session_state['position_idx']    = position_idx
                st.session_state['found_row_index'] = found_row_index
                st.session_state['added_fullname'] = f'{first_name} {last_name}'
                # st.rerun(scope='fragment')  # Force rerun to refresh the selectbox
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
