import streamlit as st

def display_camera_images():
    st.set_page_config(page_title="Camera Images", page_icon="📷")
    st.title("Camera Images")
    st.write(":rainbow[Here you can check what images the model analyzed to create the recommendation. Don't hesitate to check the cameras' links!]")

    if 'images' in st.session_state and 'camera_links' in st.session_state:
        for image, link in zip(st.session_state['images'], st.session_state['camera_links']):
            st.image(image, caption=f'View live feed from this public camera {link}', use_column_width=True)
            # st.markdown(f"[View live feed]({link})", unsafe_allow_html=True)
    else:
        st.warning("Camera images are not available until after a recommendation is generated.")

if __name__ == "__main__":
    display_camera_images()