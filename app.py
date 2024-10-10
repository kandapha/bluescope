import streamlit as st
import sqlite3
import pandas as pd
import openpyxl
import base64
import os.path

#st.logo('logo.png')
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image('Picture_2.png', width=200)
#html_code = """<h1 style="color:blue;">BlueScope Back to Work Party</h1>"""
#st.markdown(html_code, unsafe_allow_html=True)

# connect to original data
data = pd.read_excel('import_regis.xlsx')
output_path = './output.xlsx'

position_list = ['Admin','Architect','Associate director','Cad​ options','Draft man','Interior designer',
                    'Junior interior','Landscape','Production','Other...']
food_list = ['Meat','Pork']

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

side_bg = 'Picture_BG.png'
set_bg_hack(side_bg)


def formCreation(df):
    name_list = []

    #fname_df = df[['fname']] #.sort_values(by='fname')
    #fname_df.loc[len(df.index)] = ['Add new...']
    fname_df = df['fname'] 
    name_list = fname_df.to_list()
    name_list.append('Add new...')
    name_list.insert(0, '')
    
    s_name = st.selectbox('Select your first name:', name_list)

    emp_id = 0
    for idx, i in enumerate(df['fname']):
        if i == s_name :
            s_name = df['fname'][idx]
            emp_id = idx
            lname = df['lname'][idx]
            phone = df['phone'][idx]
            email = df['email'][idx]
            position_idx = position_list.index(df['position'][idx])
            text_food_allergy = df['text_food_allergy'][idx]
            is_allergy = False if df['text_food_allergy'][idx] in ['ไม่มี', 'ไม่แพ้', '-'] else True
            food_selected_idx = food_list.index(df['food_selected'][idx])
        elif s_name == 'Add new...' or s_name == '':
            s_name = ''
            emp_id = len(df['fname'])+1
            lname = ''
            phone = ''
            email = ''
            position_idx = 0
            is_allergy = 0
            text_food_allergy = ''
            food_selected_idx = 0
    
    #original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">Original image</p>'
    #st.markdown(original_title, unsafe_allow_html=True)
    
    original_title = '<p style="color:White;">Please fill in or update your data to this form</p>'
    st.markdown(original_title, unsafe_allow_html=True)

    with st.form(key='Registration Form', clear_on_submit=True):
        fname = st.text_input('Enter your first name:', value=s_name)
        lname = st.text_input('Enter your last name:', value=lname)
        phone = st.text_input('Enter your phone number:', value=phone)
        email = st.text_input('Enter your email:', value=email)
        position = st.selectbox('Enter your position', position_list, index=position_idx)
        food_allergy = st.checkbox("Food Allergy", value=is_allergy)
        text_food_allergy = st.text_input('Enter your allergy:', value=text_food_allergy)
        food_selected = st.radio("Select your meal", food_list, index=food_selected_idx)
        submitted = st.form_submit_button("Submit")

    if submitted == True:
        regis_data(df, emp_id, fname, lname, phone, email, position, text_food_allergy, food_selected)

    css="""
    <style>
        [data-testid="stForm"] {
            background: White;
        }
    </style>
    """
    st.write(css, unsafe_allow_html=True)

def regis_data(df, emp_id, fname, lname, phone, email, position, text_food_allergy, food_selected):
    print(emp_id)
    print(fname)
    df.loc[emp_id, "No"] = emp_id
    df.loc[emp_id, "fname"] = fname
    df.loc[emp_id, "lname"] = lname
    df.loc[emp_id, "phone"] = phone
    df.loc[emp_id, "email"] = email
    df.loc[emp_id, "position"] = position
    df.loc[emp_id, "text_food_allergy"] = text_food_allergy
    df.loc[emp_id, "food_selected"] = food_selected

    df.to_excel("output.xlsx") 
    st.cache_data.clear()
    st.rerun()

def import_data(uploaded_file):
    import_df = pd.read_excel(uploaded_file)
    st.success('Import Registration Data to SQLite database succesful')
    import_df.to_excel("output.xlsx") 

# ----------------------------------------------  

tab1, tab2, tab3 = st.tabs(["Registration Form | ", "Regis Information | ", "File Management"])

#tab1.subheader("Employee Data")
#tab2.subheader("Registration Information")
#tab3.subheader("Registration File")

tab1_subhader = '<p style="color:White; font-size: 20px; font-family:kanit;">ลงทะเบียนเข้าร่วมงาน</p>'
tab1.markdown(tab1_subhader, unsafe_allow_html=True)
tab2_subhader = '<p style="color:White; font-size: 20px; font-family:kanit;">แสดงข้อมูลผู้ลงทะเบียน</p>'
tab2.markdown(tab2_subhader, unsafe_allow_html=True)
tab3_subhader = '<p style="color:White; font-size: 20px; font-family:kanit;">จัดการข้อมูลผู้ลงทะเบียน</p>'
tab3.markdown(tab3_subhader, unsafe_allow_html=True)


with tab1:
    if os.path.exists(output_path):
        df = pd.read_excel(output_path, index_col=0)
    else:
        df = pd.read_excel('import_regis.xlsx')
    formCreation(df)

with tab2:
    if os.path.exists(output_path):
        df = pd.read_excel(output_path, index_col=0)
    else:
        df = pd.read_excel('import_regis.xlsx', index_col=0)
    st.dataframe(df)


with tab3:
    with st.popover("Import data"):
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None: 
            import_data(uploaded_file)    

    with st.popover("Export data"):
        if os.path.exists(output_path):
            export_df = pd.read_excel('output.xlsx', index_col=0)
            if st.button("Download Excel file"): 
                export_df.to_excel("output_registration_data_with_event_name.xlsx") 

css = '''
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Play">
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.5rem;
    font-family: "Play", sans-serif;
    color: white;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)
