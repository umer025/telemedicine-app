import streamlit as st
import requests
import datetime
import re

BASE_URL = "http://backend:8000"

st.set_page_config(page_title="Telemedicine Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1F618D;'>🩺 Telemedicine Dashboard</h1>", unsafe_allow_html=True)

# Sidebar for both module and action
st.sidebar.markdown("## 📁 Navigation")
menu = st.sidebar.selectbox("📋 Select Module", ["Users", "Appointments", "Prescriptions"])
action = st.sidebar.radio("⚙️ Select Action", ["Create", "View All", "View by ID", "Update", "Delete"])

# Top image banner
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJYk1MTig96Bql3gEO4_GlDMsnZgHidWY0Pw&s", use_container_width=True)


def emoji_field(field):
    emoji_dict = {
        "full_name": "📛 Full Name",
        "email": "📧 Email",
        "password_hash": "🔒 Password",
        "role": "🧑‍⚕️ Role",
        "phone_number": "📞 Phone Number",
        "patient_id": "🧑 Patient ID",
        "doctor_id": "👨‍⚕️ Doctor ID",
        "appointment_date": "📅 Appointment Date",
        "status": "📌 Status",
        "notes": "📝 Notes",
        "appointment_id": "📄 Appointment ID"
    }
    return emoji_dict.get(field, field.replace("_", " ").title())


def section_image(module):
    img_map = {
        "Users": "https://cdn-icons-png.flaticon.com/512/847/847969.png",
        "Appointments": "https://cdn-icons-png.flaticon.com/512/2989/2989988.png",
        "Prescriptions": "https://cdn-icons-png.flaticon.com/512/899/899755.png"
    }
    st.image(img_map.get(module), width=80)


def build_inputs(fields):
    inputs = {}
    validation_passed = True

    for f in fields:
        label = emoji_field(f)
        if "role" in f.lower():
            inputs[f] = st.selectbox("🧑 Role", ["Patient", "Doctor", "Admin"])
        elif "status" in f.lower():
            inputs[f] = st.selectbox("📌 Status", ["Pending", "Confirmed", "Cancelled"])
        elif "appointment_date" in f:
            date = st.date_input("📅 Appointment Date")
            time = st.time_input("⏰ Appointment Time", value=datetime.time(9, 0))
            inputs[f] = datetime.datetime.combine(date, time).isoformat()
        elif "password" in f.lower():
            inputs[f] = st.text_input(label, type="password")
        elif "email" in f.lower():
            value = st.text_input(label)
            if value and not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                st.warning("⚠️ Invalid email format")
                validation_passed = False
            inputs[f] = value
        elif "phone" in f.lower():
            value = st.text_input(label)
            if value and (not value.isdigit() or len(value) < 10 or len(value) > 15):
                st.warning("⚠️ Phone number should be 10–15 digits")
                validation_passed = False
            inputs[f] = value
        elif "name" in f.lower():
            value = st.text_input(label)
            if value and not re.match(r"^[a-zA-Z\s]+$", value):
                st.warning("⚠️ Full name should contain only letters and spaces")
                validation_passed = False
            inputs[f] = value
        else:
            inputs[f] = st.text_input(label)
    
    return inputs, validation_passed


def handle_crud(module, fields, endpoint, action):
    st.markdown(f"### 🚀 {module} Management Panel")
    section_image(module)
    st.markdown(f"#### ✏️ You selected: **{action}**")
    st.markdown("---")

    if action == "Create":
        st.subheader(f"➕ Create New {module}")
        with st.form(f"create_{module.lower()}"):
            inputs, valid = build_inputs(fields)
            submitted = st.form_submit_button(f"Create {module}")
            if submitted:
                if not valid:
                    st.error("❌ Please correct the highlighted input errors.")
                elif all(str(v).strip() != "" for v in inputs.values()):
                    response = requests.post(f"{BASE_URL}/{endpoint}/", json=inputs)
                    st.success("✅ Created successfully!")
                    st.json(response.json())
                else:
                    st.error("❌ All fields are required. Please fill in every field.")

    elif action == "View All":
        st.subheader(f"📃 All {module}s")
        response = requests.get(f"{BASE_URL}/{endpoint}/")
        st.json(response.json())

    elif action == "View by ID":
        st.subheader(f"🔍 View {module} by ID")
        obj_id = st.number_input(f"Enter {module} ID", min_value=1, step=1)
        if st.button("Fetch"):
            response = requests.get(f"{BASE_URL}/{endpoint}/{obj_id}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error("❌ Record not found.")

    elif action == "Update":
        st.subheader(f"✏️ Update {module}")
        obj_id = st.number_input(f"Enter {module} ID to Update", min_value=1, step=1)
        with st.form(f"update_{module.lower()}"):
            inputs, valid = build_inputs(fields)
            submitted = st.form_submit_button("Update")
            if submitted:
                if not valid:
                    st.error("❌ Please correct the highlighted input errors.")
                elif all(str(v).strip() != "" for v in inputs.values()):
                    response = requests.put(f"{BASE_URL}/{endpoint}/{obj_id}", json=inputs)
                    if response.status_code == 200:
                        st.success("✅ Updated successfully!")
                        st.json(response.json())
                    else:
                        st.error("❌ Update failed.")
                else:
                    st.error("❌ All fields are required. Please fill in every field.")

    elif action == "Delete":
        st.subheader(f"🗑️ Delete {module}")
        obj_id = st.number_input(f"Enter {module} ID to Delete", min_value=1, step=1)
        if st.button("Delete"):
            response = requests.delete(f"{BASE_URL}/{endpoint}/{obj_id}")
            if response.status_code == 200:
                st.success("✅ Deleted successfully!")
                st.json(response.json())
            else:
                st.error("❌ Deletion failed.")


# Route to correct module and perform action
if menu == "Users":
    handle_crud("Users", ["full_name", "email", "password_hash", "role", "phone_number"], "users", action)
elif menu == "Appointments":
    handle_crud("Appointments", ["patient_id", "doctor_id", "appointment_date", "status"], "appointments", action)
elif menu == "Prescriptions":
    handle_crud("Prescriptions", ["appointment_id", "doctor_id", "patient_id", "notes"], "prescriptions", action)
