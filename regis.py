import streamlit as st
import pandas as pd
import base64
from datetime import datetime

logo_image = 'images/Picture_2.png'
bg_image = 'images/Picture_BG_resize.png'

# Initialize variables for form inputs
position_list = ['Admin','Architect','Associate director','Cad​ options','Draft man','Interior designer',
                    'Junior interior','Landscape','Production','Other...']
food_list = ['Meat','Pork']
fname = ""
lname = ""
phone = ""
email = ""
position_idx = 0
is_allergy = False
text_food_allergy = ""
food_selected_idx = 0

# Function to load existing data from Excel
def load_data(file):
    data = pd.read_excel(file)
    return data

def load_and_save_data(file):
    data = pd.read_excel(file)
    data['timestamp'] = pd.NaT
    data.to_excel("new_registrations.xlsx", index=False)
    return data

# Function to save data to Excel
def save_data(data, file):
    data.to_excel(file, index=False)
    
try:
    existing_data = load_data("registrations.xlsx")
    unique_names = existing_data[['fname', 'lname']].drop_duplicates()
    names = list(unique_names.itertuples(index=False, name=None))
except FileNotFoundError:
    names = []


#st.logo('logo.png')
left_co, cent_co,last_co = st.columns(3)
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

# -----------------------------------------------

# Create tabs
tab1, tab2 = st.tabs(["Registration Form | ", "Regis Information"])


# Tab 1: Registration Form
with tab1:

    # Title of the app
    tab1_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">ลงทะเบียนเข้าร่วมงาน</p>'
    tab1.markdown(tab1_subhader, unsafe_allow_html=True)
    existing_data = []
    # Load existing data if the file exists
    try:
        existing_data = load_data("new_registrations.xlsx")
        #names = existing_data["fname"].unique().tolist()
        unique_names = existing_data[['fname', 'lname']].drop_duplicates()
        unique_names_list = list(unique_names.itertuples(index=False, name=None))
        names = []
        for i in unique_names_list:
            print(' '.join(i))
            names.append(' '.join(i))        
    except FileNotFoundError:
        names = []

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

    selected_name = st.selectbox("Select a registered person (optional)", [""] + sorted(names))

    detail_txt = '<p style="color:White;">Details of selected person:</p>'
    st.markdown(detail_txt, unsafe_allow_html=True)

    is_update = False
    # If a name is selected, display the corresponding details
    if selected_name:
        words = selected_name.split()
        matching_rows = unique_names[(unique_names["fname"] == words[0]) & (unique_names["lname"] == words[1])]
        matching_indices = matching_rows.index.tolist()
        if matching_indices:
            is_update = True
            emp_id = matching_indices[0]
            fname = existing_data.loc[matching_indices[0]]['fname']
            lname = existing_data.loc[matching_indices[0]]['lname']
            phone = existing_data.loc[matching_indices[0]]['phone']
            email = existing_data.loc[matching_indices[0]]['email']
            position = existing_data.loc[matching_indices[0]]['position']
            position_idx = position_list.index(position)
            is_allergy = False if existing_data.loc[matching_indices[0]]['text_food_allergy'] in ['ไม่มี', 'ไม่แพ้', '-'] else True
            text_food_allergy = existing_data.loc[matching_indices[0]]['text_food_allergy']
            food_selected = existing_data.loc[matching_indices[0]]['food_selected']
            food_selected_idx = food_list.index(food_selected)
    else:
        is_update = False
        print('===============')

    # Registration form fields
    with st.form(key='registration_form', clear_on_submit=True):
        fname = st.text_input('Enter your first name:', value=fname)
        lname = st.text_input('Enter your last name:', value=lname)
        phone = st.text_input('Enter your phone number:', value=phone)
        email = st.text_input('Enter your email:', value=email)
        position = st.selectbox('Enter your position', position_list, index=position_idx)
        food_allergy = st.checkbox("Food Allergy", value=is_allergy)
        text_food_allergy = st.text_input('Enter your allergy:', value=text_food_allergy)
        food_selected = st.radio("Select your meal", food_list, index=food_selected_idx)
        submit_button = st.form_submit_button("Registration")

    # Create a new DataFrame to store registration data
    if submit_button:
      
        if is_update :
            # Create a new row with the form data and the current timestamp
            print('update data')

            if not text_food_allergy:
                text_food_allergy = "-"
            existing_data.loc[matching_indices[0], 'fname'] = fname
            existing_data.loc[matching_indices[0], 'lname'] = lname
            existing_data.loc[matching_indices[0], 'phone'] = phone
            existing_data.loc[matching_indices[0], 'email'] = email
            existing_data.loc[matching_indices[0], 'position'] = position
            existing_data.loc[matching_indices[0], 'text_food_allergy'] = text_food_allergy
            existing_data.loc[matching_indices[0], 'food_selected'] = food_selected
            existing_data.loc[matching_indices[0], 'timestamp'] = datetime.now()
        else:
            print('new data')
            if not text_food_allergy:
                text_food_allergy = "-"
            new_row = {
                'No' : len(existing_data)+1 ,
                'fname': fname,
                'lname': lname,
                'phone': phone,
                'email': email,
                'position': position,
                'text_food_allergy': text_food_allergy,
                'food_selected': food_selected,
                'timestamp': datetime.now()  # Current timestamp
            }              

            # Append new data
            new_data = pd.DataFrame.from_dict(new_row, orient='index')
            existing_data = pd.concat([existing_data, new_data.T], ignore_index=True)
            existing_data['text_food_allergy'] = existing_data['text_food_allergy'].fillna('-')

        # Save updated data to Excel
        save_data(existing_data, "new_registrations.xlsx")
        st.success("Registration successful!")
        st.experimental_rerun()

    css="""
    <style>
        [data-testid="stForm"] {
            background: White;
        }
    </style>
    """
    
    st.write(css, unsafe_allow_html=True)
    
    
# Tab 2: View Registrations
with tab2:
    tab2_subhader = '<p style="color:White; font-size: 28px; font-family:kanit;">แสดงข้อมูลผู้ลงทะเบียน</p>'
    tab2.markdown(tab2_subhader, unsafe_allow_html=True)    

    # Check if the Excel file exists
    try:
        df = load_data("new_registrations.xlsx")

        existing_txt = '<p style="color:White;">Existing Registrations:</p>'
        st.markdown(existing_txt, unsafe_allow_html=True)

        st.dataframe(df)

        # Select box to choose a registered person
        selected_name = st.selectbox("Select a registered person", df["fname"].unique())

        # Display details of the selected person
        selected_data = df[df["fname"] == selected_name]
        detail_txt = '<p style="color:White;">Detail:</p>'
        st.markdown(detail_txt, unsafe_allow_html=True)
        st.dataframe(selected_data)

    except FileNotFoundError:     
        st.warning("No registrations found. Please register first.")

    st.empty()
    # -------------------------
    detail_txt = '<p style="color:White;">File Management ------------ </p>'
    st.markdown(detail_txt, unsafe_allow_html=True)   

    with st.expander("Download File"):
        # Download link for the updated registrations
        if st.button("Download Registration Data"):
            if 'updated_data' in locals():
                #updated_data.to_excel("new_registrations.xlsx", index=False)
                st.success("Download link available.")
            else:
                st.warning("No data available to download.")

         # Upload new registrations data
        uploaded_file = st.file_uploader("Upload file for the new event")
        if uploaded_file is not None:
            load_and_save_data(uploaded_file)

css = '''
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Jost">
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.5rem;
    font-family: "Jost", sans-serif;
    color: white;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)