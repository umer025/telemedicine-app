import streamlit as st
import requests
import datetime
import re
import html
import bleach
import pandas as pd

BASE_URL = "http://backend:8000"

def sanitize_input(value):
    if value is None:
        return ""
    return bleach.clean(html.escape(str(value)), tags=[], attributes={}, strip=True)

# ---------------- Session State ----------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- Authentication ----------------
def login():
    st.subheader("🔐 Login")
    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not email or not password:
                st.warning("⚠️ Email and password are required")
            else:
                res = requests.post(f"{BASE_URL}/login", data={"username": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]["access_token"]
                    st.session_state.user = data["user"]
                    st.success("✅ Login successful")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

def signup():
    st.subheader("📝 Signup")
    with st.form("signup_form"):
        name = st.text_input("📛 Full Name")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        phone = st.text_input("📞 Phone Number")
        role = st.selectbox("👤 Role", ["Patient", "Doctor", "Admin"])
        submitted = st.form_submit_button("Signup")

        if submitted:
            if not re.match(r"^[a-zA-Z\s]+$", name):
                st.warning("⚠️ Name must contain only letters and spaces")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.warning("⚠️ Invalid email format")
            elif not password.strip():
                st.warning("⚠️ Password cannot be empty")
            elif not (phone.isdigit() and 10 <= len(phone) <= 15):
                st.warning("⚠️ Phone number should be 10–15 digits")
            else:
                payload = {
                    "full_name": name.strip(),
                    "email": email.strip(),
                    "password": password,
                    "role": role,
                    "phone_number": phone.strip()
                }
                res = requests.post(f"{BASE_URL}/signup", json=payload)
                if res.status_code in [200, 201]:
                    st.success("✅ Signup successful. You may login.")
                else:
                    st.error(f"❌ {res.text}")

def reset_password():
    st.subheader("🔁 Password Reset")
    with st.form("reset_form"):
        email = st.text_input("📧 Registered Email")
        new_pw = st.text_input("🔒 New Password", type="password")
        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.warning("⚠️ Invalid email format")
            elif not new_pw.strip():
                st.warning("⚠️ Password cannot be empty")
            else:
                payload = {"email": email.strip(), "new_password": new_pw}
                res = requests.post(f"{BASE_URL}/reset-password", json=payload)
                if res.status_code == 200:
                    st.success("✅ Password updated.")
                else:
                    st.error("❌ Reset failed.")

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

# ---------------- Auth Flow ----------------
if not st.session_state.token:
    auth_tab = st.sidebar.radio("🔐 Select Option", ["Login", "Signup", "Reset Password"])
    if auth_tab == "Login":
        login()
    elif auth_tab == "Signup":
        signup()
    else:
        reset_password()
    st.stop()

# ---------------- Dashboard ----------------
st.set_page_config(page_title="Telemedicine Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1F618D;'>🩺 Telemedicine Dashboard</h1>", unsafe_allow_html=True)
st.sidebar.success(f"✅ Logged in as: {st.session_state.user['full_name']} ({st.session_state.user['role']})")
if st.sidebar.button("🚪 Logout"):
    logout()

# ---------------- Role-Based Action Visibility ----------------
role = st.session_state.user["role"]

# Module visibility
if role == "Admin":
    allowed_modules = ["Users", "Appointments", "Prescriptions", "Inventory", "Payments", "Lab Tests", "EMR"]
    allowed_actions = ["Create", "View All", "View by ID", "Update", "Delete"]
elif role == "Doctor":
    allowed_modules = ["Appointments", "Prescriptions", "Lab Tests", "EMR"]
    allowed_actions = ["Create", "View All", "View by ID", "Update", "Delete"]
elif role == "Patient":
    allowed_modules = ["Appointments", "Prescriptions", "Lab Tests", "EMR"]
    allowed_actions = ["View All", "View by ID"]
else:
    allowed_modules = []
    allowed_actions = []

# Sidebar selections
st.sidebar.markdown("## 📁 Navigation")
menu = st.sidebar.selectbox("📋 Select Module", allowed_modules)
action = st.sidebar.radio("⚙️ Select Action", allowed_actions)

st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJYk1MTig96Bql3gEO4_GlDMsnZgHidWY0Pw&s", use_container_width=True)

def emoji_field(field):
    emojis = {
        "full_name": "📛 Full Name", "email": "📧 Email", "password_hash": "🔒 Password",
        "role": "🧑‍⚕️ Role", "phone_number": "📞 Phone Number", "patient_id": "🧑 Patient ID",
        "doctor_id": "👨‍⚕️ Doctor ID", "appointment_date": "📅 Appointment Date", "status": "📌 Status",
        "notes": "📝 Notes", "appointment_id": "📄 Appointment ID", "name": "💊 Medicine Name",
        "description": "🧾 Description", "price": "💵 Price", "quantity": "📦 Quantity", "user_id": "👤 User ID",
        "amount": "💰 Amount", "payment_method": "💳 Payment Method", "test_type": "🧪 Test Type",
        "result": "📄 Result", "summary": "🗒️ Summary"
    }
    return emojis.get(field, field.replace("_", " ").title())

def section_image(module):
    icons = {
        "Users": "https://cdn-icons-png.flaticon.com/512/847/847969.png",
        "Appointments": "https://cdn-icons-png.flaticon.com/512/2989/2989988.png",
        "Prescriptions": "https://cdn-icons-png.flaticon.com/512/899/899755.png",
        "Inventory": "https://cdn-icons-png.flaticon.com/512/3621/3621605.png",
        "Payments": "https://cdn-icons-png.flaticon.com/512/1574/1574345.png",
        "Lab Tests": "https://cdn-icons-png.flaticon.com/512/2674/2674510.png",
        "EMR": "https://cdn-icons-png.flaticon.com/512/2037/2037991.png"
    }
    st.image(icons.get(module), width=80)

# ---------------- API Request Wrapper ----------------
def make_request(method, endpoint, **kwargs):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = requests.request(method, f"{BASE_URL}/{endpoint}", headers=headers, **kwargs)
        return res
    except Exception as e:
        st.error(f"❌ {e}")
        return None

# ---------------- Dynamic Input Fields ----------------
def build_inputs(fields, endpoint):
    inputs = {}
    valid = True

    for f in fields:
        label = emoji_field(f)
        value = None

        try:
            if f == "role":
                value = st.selectbox(label, ["Patient", "Doctor", "Admin"])

            elif f == "status":
                if "appointment" in endpoint:
                    value = st.selectbox(label, ["Pending", "Confirmed", "Cancelled"])
                elif "payments" in endpoint:
                    value = st.selectbox(label, ["Pending", "Success", "Failed"])
                elif "lab-tests" in endpoint:
                    value = st.selectbox(label, ["Pending", "Completed"])
                else:
                    value = st.text_input(label)

            elif f == "payment_method":
                value = st.selectbox(label, ["Card", "Easypaisa", "JazzCash"])

            elif f == "appointment_date":
                date = st.date_input(label)
                time = st.time_input("⏰ Appointment Time", value=datetime.time(9, 0))
                value = datetime.datetime.combine(date, time).isoformat()

            elif f == "password":
                value = st.text_input(label, type="password")

            elif "email" in f:
                value = st.text_input(label)
                if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    st.warning("⚠️ Invalid email format")
                    valid = False

            elif "phone" in f:
                value = st.text_input(label)
                if not (value.isdigit() and 10 <= len(value) <= 15):
                    st.warning("⚠️ Phone number should be 10–15 digits")
                    valid = False

            elif f == "name":
                value = st.text_input(label)
                if not re.match(r"^[a-zA-Z\s]+$", value):
                    st.warning("⚠️ Name must contain only letters and spaces")
                    valid = False

            elif f in ["price", "amount"]:
                value = st.number_input(label, min_value=0.0, step=0.01)

            elif f == "quantity":
                value = st.number_input(label, min_value=0, step=1)

            elif f in ["user_id", "patient_id", "doctor_id"]:
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    res = requests.get(f"{BASE_URL}/users/", headers=headers)
                    if res.status_code == 200:
                        users = res.json()

                        # Role filtering
                        if f == "patient_id":
                            users = [u for u in users if u["role"] == "Patient"]
                        elif f == "doctor_id":
                            users = [u for u in users if u["role"] == "Doctor"]

                        ids = [u["user_id"] for u in users]
                        if ids:
                            value = st.selectbox(label, ids)
                        else:
                            st.warning(f"⚠️ No {f.replace('_id','s')} found")
                            valid = False
                    else:
                        st.error(f"❌ Unable to fetch users: {res.status_code}")
                        valid = False
                except Exception as e:
                    st.error(f"❌ Failed to load user list: {e}")
                    valid = False

            elif f == "appointment_id":
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    res = requests.get(f"{BASE_URL}/appointments/", headers=headers)
                    if res.status_code == 200:
                        appts = res.json()
                        ids = [a["appointment_id"] for a in appts]
                        if ids:
                            value = st.selectbox(label, ids)
                        else:
                            st.warning("⚠️ No appointments found")
                            valid = False
                    else:
                        st.error(f"❌ Unable to fetch appointments: {res.status_code}")
                        valid = False
                except Exception as e:
                    st.error(f"❌ Failed to load appointments: {e}")
                    valid = False

            else:
                value = st.text_area(label) if len(f) > 20 or f in ["summary", "description", "notes", "result"] else st.text_input(label)

        except Exception as e:
            st.error(f"❌ Error rendering input: {f} - {e}")
            valid = False

        inputs[f] = sanitize_input(value) if isinstance(value, str) else value

    return inputs, valid


def handle_crud(module, fields, endpoint, action):
    st.markdown(f"### 🚀 {module} Management Panel")
    section_image(module)
    st.markdown(f"#### ✏️ You selected: **{action}**")
    st.markdown("---")

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if action == "Create":
        st.subheader(f"➕ Create New {module}")
        with st.form(f"create_{module}"):
            inputs, valid = build_inputs(fields, endpoint)
            submitted = st.form_submit_button(f"Create {module}")
            if submitted:
                if not valid or None in inputs.values() or any(str(v).strip() == "" for v in inputs.values()):
                    st.error("❌ All fields are required and must be valid.")
                else:
                    res = requests.post(f"{BASE_URL}/{endpoint}/", json=inputs, headers=headers)
                    if res.status_code in [200, 201]:
                        st.success("✅ Created successfully!")
                        st.json(res.json())
                    else:
                        st.error(f"❌ Creation failed: {res.status_code} - {res.text}")

    elif action == "View All":
        st.subheader(f"📃 All {module}")
        res = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("ℹ️ No records found.")
        else:
            st.error(f"❌ Error: {res.status_code} - {res.text}")

    elif action == "View by ID":
        st.subheader(f"🔍 View {module} by ID")
        obj_id = st.number_input(f"Enter {module} ID", min_value=1, step=1)
        if st.button("Fetch"):
            res = requests.get(f"{BASE_URL}/{endpoint}/{obj_id}", headers=headers)
            if res.status_code == 200:
                data = res.json()
                df = pd.DataFrame([data])
                st.dataframe(df)
            else:
                st.error(f"❌ Record not found. {res.status_code} - {res.text}")

    elif action == "Update":
        st.subheader(f"✏️ Update {module}")
        obj_id = st.number_input(f"Enter {module} ID to Update", min_value=1, step=1)
        with st.form(f"update_{module}"):
            inputs, valid = build_inputs(fields, endpoint)
            submitted = st.form_submit_button("Update")
            if submitted:
                if not valid or None in inputs.values() or any(str(v).strip() == "" for v in inputs.values()):
                    st.error("❌ All fields are required and must be valid.")
                else:
                    res = requests.put(f"{BASE_URL}/{endpoint}/{obj_id}", json=inputs, headers=headers)
                    if res.status_code == 200:
                        st.success("✅ Updated successfully!")
                        st.json(res.json())
                    else:
                        st.error(f"❌ Update failed: {res.status_code} - {res.text}")

    elif action == "Delete":
        st.subheader(f"🗑️ Delete {module}")
        obj_id = st.number_input(f"Enter {module} ID to Delete", min_value=1, step=1)
        if st.button("Delete"):
            res = requests.delete(f"{BASE_URL}/{endpoint}/{obj_id}", headers=headers)
            if res.status_code == 200:
                st.success("✅ Deleted successfully!")
                st.json(res.json())
            else:
                st.error(f"❌ Deletion failed: {res.status_code} - {res.text}")

# Route modules
if menu == "Users":
    handle_crud("Users", ["full_name", "email", "password", "role", "phone_number"], "users", action)
elif menu == "Appointments":
    handle_crud("Appointments", ["patient_id", "doctor_id", "appointment_date", "status"], "appointments", action)
elif menu == "Prescriptions":
    handle_crud("Prescriptions", ["appointment_id", "doctor_id", "patient_id", "notes"], "prescriptions", action)
elif menu == "Inventory":
    handle_crud("Inventory", ["name", "description", "price", "quantity"], "inventory", action)
elif menu == "Payments":
    handle_crud("Payments", ["user_id", "amount", "payment_method", "status"], "payments", action)
elif menu == "Lab Tests":
    handle_crud("Lab Tests", ["patient_id", "test_type", "result", "status"], "lab-tests", action)
elif menu == "EMR":
    handle_crud("EMR", ["patient_id", "doctor_id", "summary"], "emr", action)
