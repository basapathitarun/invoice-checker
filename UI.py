import os
import streamlit as st
import requests

FAST_API_URL = 'http://localhost:8000'

def list_folders_in_dir(folder_path):
    folders = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path,name))]
    return folders
def main():
    st.header("Invoice checker")

    action =  st.radio(
        "Select Action",
        ("None","Select Images","select folder")
    )

    if action == "Select Images":
        uploaded_files = st.file_uploader("Upolad mulitiple images", type=['jpg','jpeg','png'],accept_multiple_files=True)
        if uploaded_files and st.button("Process Images"):
            try:
                files = [("files",(uploaded_file.name, uploaded_file,uploaded_file.type)) for uploaded_file in uploaded_files]
                response = requests.post(f"{FAST_API_URL}/process_image/",files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.write(result)
                else:
                    st.error(f"Error processing images: {response.text}")
            except Exception as e:
                st.error(f"An error occured: {e}")
    elif action == "select folder":
        currect_dir = os.getcwd()

        folders = list_folders_in_dir(currect_dir)

        selected_folder = st.selectbox("select a folder:",folders)

        if selected_folder:
            folder_path = os.path.join(currect_dir,selected_folder)
            if st.button("Process Folder"):
                response = requests.post(f"{FAST_API_URL}/process_folder/",params ={"file_name":folder_path})

                if response.status_code == 200:
                    result = response.json()
                    st.json(result)
                else:
                    st.error(f"Error processing images: {response.text}")
    else:
        st.info("No action selected.please chose an action.")

if __name__ == "__main__":
    main()




