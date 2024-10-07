import streamlit as st
import sqlite3
import pandas as pd
import openpyxl
import base64
from streamlit_js_eval import streamlit_js_eval

#st.logo('logo.png')
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image('Picture_2.png', width=200)
#html_code = """<h1 style="color:blue;">BlueScope Back to Work Party</h1>"""
#st.markdown(html_code, unsafe_allow_html=True)

# connect to SQLite
conn = sqlite3.connect('regis.db', check_same_thread=True)
cursor = conn.cursor()
cursor.execute("""
    create table if not exists registrations(
            No number(5),
            fname text(100), 
            lname text(100), 
            phone text(10), 
            email text(40),
            position text(100), 
            text_food_allergy text(100),
            food_selected text(100))
""")

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

    if submitted == True and (s_name == 'Add new...' or s_name == ''): #emp_id = index
        print('add new -------------')
        print(s_name)
        print(emp_id)
        add_regis_data(emp_id, fname, lname, phone, email, position, text_food_allergy, food_selected)
    elif submitted == True:
        #updateRegis(emp_id, fname, lname, phone, email, position, text_food_allergy, food_selected)
        print('update -------------')
        print(s_name)
        print(emp_id)
        print(fname)
        print(food_selected)
        update_regis_data(emp_id, fname, lname, phone, email, position, text_food_allergy, food_selected)

    css="""
    <style>
        [data-testid="stForm"] {
            background: White;
        }
    </style>
    """
    st.write(css, unsafe_allow_html=True)

def update_regis_data(emp_id,a,b,c,d,e,f,g):
    #cursor.execute("Insert into registrations values (?,?,?,?,?,?,?,?)" , (emp_id,a,b,c,d,e,f,g))
    #conn.commit()
    
    css="""
    <style>
        [data-testid="stAlert"] {
            background: White;
            border-radius: 5px;
        }
    </style>
    """

    st.warning('Your registration has been updated')
    st.write(css, unsafe_allow_html=True)
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

def add_regis_data(emp_id,a,b,c,d,e,f,g):

    cursor.execute("Insert into registrations values (?,?,?,?,?,?,?,?)" , (emp_id,a,b,c,d,e,f,g))
    conn.commit()
    
    css="""
    <style>
        [data-testid="stAlert"] {
            background: White;
            border-radius: 5px;
        }
    </style>
    """

    st.success('Your registration has been added successful!')
    st.write(css, unsafe_allow_html=True)
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

def import_data(uploaded_file):
    cursor.execute("""
        create table if not exists registrations(
                No number(5),
                fname text(100), 
                lname text(100), 
                phone text(10), 
                email text(40),
                position text(100), 
                text_food_allergy text(100),
                food_selected text(100))
    """)
    cursor.execute('DROP TABLE IF EXISTS registrations;')

    import_df = pd.read_excel(uploaded_file)
    st.write(import_df)
    import_df.to_sql(name='registrations', con=conn, if_exists='replace', index=False)

    st.success('Import Registration Data to SQLite database succesful')

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
    query = "select * from registrations order by fname"
    df = pd.read_sql(query, conn)    
    formCreation(df)

with tab2:
    query = "select * from registrations"
    df = pd.read_sql(query, conn)
    #print(df.head())
    st.write(df)


with tab3:
    with st.popover("Import data"):
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None: 
            import_data(uploaded_file)    

    with st.popover("Export data"):
        if st.button("Download Excel file"):  
            query = "select * from registrations"
            df = pd.read_sql(query, conn)
            df.to_excel("export_regis.xlsx")        
            st.success('Download Successful')    

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
