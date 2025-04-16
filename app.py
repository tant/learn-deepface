import streamlit as st
import os
import uuid
from retinaface import RetinaFace
from deepface import DeepFace
from PIL import Image
import uuid


# Ensure the 'img' directory exists
if not os.path.exists("img"):
  os.makedirs("img")

if not os.path.exists("faces"):
  os.makedirs("faces")





# Set page config
st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("Look a like? 🎉")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Guide", "Privacy notice"])

# Initialize state if it doesn't exist
if 'img_file' not in st.session_state:
  st.session_state.img_file = ""
if 'faces' not in st.session_state:
  st.session_state.faces = []


def process_image(image_path):
  
  print(f"Processing file: {image_path}")
  # save this filename to db and get the id 
  faces = RetinaFace.extract_faces(image_path, align=True)
  print(f"Total number of faces detected: {len(faces)}")

  n = 0
  # loop through all faces 
  for face in faces:
    # need an id here
    unique_id = uuid.uuid4()

    # get the face and save it to jpg
    filepath = f"./faces/face_{unique_id}.jpg"
    Image.fromarray(face).save(filepath)

    # try to get emmbeding here to skip wrong face images
    try:
      # i take the embedding as well and save it
      embedding_objs = DeepFace.represent(face, enforce_detection=True)
      # embedding_filepath = f"./faces/emb_{unique_id}.txt"

      # with open(embedding_filepath, "w") as f:
      #   f.write(str(embedding_objs))

      # count one more picture
      n = n + 1
      st.session_state.faces.append(filepath)

    except Exception as e:
      # delete the image if there is an error
      if os.path.exists(filepath):
        os.remove(filepath)

  print(f"Total number of faces saved: {n}")
  return n




# Main content
if page == "Home":
  if (st.session_state.img_file == ""):
    # File uploader for JPG files
    st.subheader("Upload your 3 members picture:")
    
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
      uploaded_file = st.file_uploader("Choose a JPG file", type=["jpg"])

      if uploaded_file is not None:
        # Save the uploaded file to the 'img' directory
        file_path = os.path.join("img", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Generate a unique ID for the file
        unique_id = f"img-{uuid.uuid4().hex}.jpg"
        unique_file_path = os.path.join("img", unique_id)

        # Rename the file
        os.rename(file_path, unique_file_path)
        st.session_state.img_file = unique_file_path
        st.success("File uploaded successfully!")
        st.rerun()
  else: 
    st.subheader("Uploaded Image:")

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
      # Display the uploaded image
      st.image(st.session_state.img_file, caption="Uploaded Image", use_container_width=True)
    
    # Button to process the image
    if st.button("Process Image"):
    
      st.success("Processing image...")
    
      process_image(st.session_state.img_file)
      
      with col2:
        # st.subheader("Detected Faces:")

        min_age = 1000
        
        child_gender = ""
        child = "" 
        mom = ""
        dad = ""

        # Display detected faces
        for face in st.session_state.faces:
          data = DeepFace.analyze(img_path = face, actions = ['age', 'gender'])
          gender = data[0]['dominant_gender']
          age = data[0]['age']

          # child is the face which has smallest age
          # dad là Man không phải tuổi nhỏ nhất
          # mon là Woman khô

          if (age < min_age):
            # xuất hiện tuổi nhỏ rồi thì cập nhật lại min age thôi
            min_age = age

            if (child == ""): # nếu chưa có child thì lấy thôi không quan tâm
              child = face
              child_gender = gender
            else: # đã từng lưu child rồi thì backup lại thành dad với mom
              if (child_gender == "Man"):
                dad = child
                child = face
              else:
                mom = child
                child = face
          else: # tuổi lớn rồi, update thôi
            if (gender == "Man"):
                dad = face
            else:
                mom = face

          # st.image(face, caption="Detected Face")
          # st.write("Gender:", gender, "-", "Age:", age)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image(dad, caption="Dad")
        with col2:
            st.image(child, caption="Child")
        with col3:
            st.image(mom, caption="Mom")

        paternal_result = DeepFace.verify(img1_path = dad, img2_path = child)
        maternal_result = DeepFace.verify(img1_path = mom, img2_path = child)
        # st.write("Paternal Verification Result:", paternal_result)
        # st.write("Maternal Verification Result:", maternal_result)
        if (paternal_result["distance"] <= maternal_result["distance"]):
          st.success("The child is more likely to resemble the father.")
        else:
          st.success("The child is more likely to resemble the mother.")
        

    st.success("Image processed successfully!")
    # Button to clear the image
    if st.button("Clear", key="clear_button"):
      # Delete all image files and face files
      try:
        os.remove(st.session_state.img_file)
        for face in st.session_state.faces:
          os.remove(face)
      except:
        pass
      st.success("All image and face files have been deleted.")
      # Clear the session state
      st.session_state.img_file = ""
      st.session_state.faces = []
      st.rerun()
        
      
      # st.session_state.img_file = ""
      # st.rerun()

elif page == "Guide":
    st.header("How to use")
    
    st.write("""
    - Upload an image of your family with 3 members. Please note that other faces in the image may affect the process due to the simple logic used.
    - Once your image is uploaded and displayed on the web, click **Process Image** to extract the faces of the dad, mom, and child, and then find the similarities.
    - Click **Clear** to delete all data and back to the beginning.
    """)

elif page == "Privacy notice":
    st.header("Privacy notice")
    