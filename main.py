import streamlit as st
import mysql.connector


# إعدادات الاتصال بقاعدة البيانات باستخدام Streamlit Secrets
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None


# دالة التحقق من تسجيل الدخول
def authenticate_user(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None


# حالة تسجيل الدخول في الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# واجهة تسجيل الدخول إذا لم يتم تسجيل الدخول بعد
if not st.session_state.logged_in:
    st.subheader("تسجيل الدخول - نظام المبيعات")

    with st.form("login_form"):
        username_input = st.text_input("اسم المستخدم:")
        password_input = st.text_input("كلمة المرور:", type="password")
        submit_login = st.form_submit_button("دخول")

        if submit_login:
            if authenticate_user(username_input.strip(), password_input.strip()):
                st.session_state.logged_in = True
                st.session_state.username = username_input.strip()
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

else:
    # الواجهة الرئيسية بعد تسجيل الدخول الناجح
    st.sidebar.write(f"مرحباً، {st.session_state.username}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("لوحة تحكم نظام المبيعات")

    # نموذج تسجيل عملية مبيعات جديدة
    with st.form("sales_form"):
        # تم تعديل حقل المبلغ ليقبل أرقام صحيحة فقط بدون أعشار (step=1)
        amount = st.number_input("مبلغ العملية:", min_value=0, step=1, format="%d")

        # خيارات طرق الدفع
        payment_type = st.selectbox("طريقة الدفع:", ["نقداً", "بنكك"])

        # حقل إدخال رقم العملية المرجعي لبنكك
        transaction_ref = st.text_input("رقم العملية المرجعي (مطلوب لبنكك فقط):")

        submit_sale = st.form_submit_button("حفظ العملية")

    if submit_sale:
        if amount <= 0:
            st.warning("يرجى إدخال مبلغ أكبر من الصفر!")
        elif payment_type == "بنكك" and not transaction_ref.strip():
            st.warning("يرجى إدخال رقم العملية المرجعي لبنكك!")
        else:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                ref_val = transaction_ref.strip() if payment_type == "بنكك" else None
                query = "INSERT INTO transactions (amount, payment_type, transaction_ref, status) VALUES (%s, %s, %s, 'open')"
                cursor.execute(query, (amount, payment_type, ref_val))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("تم تسجيل عملية المبيعات بنجاح!")
                st.rerun()