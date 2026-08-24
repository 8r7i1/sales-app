import streamlit as st
import mysql.connector

# إعدادات صفحة Streamlit لتصميم أنيق وواضح
st.set_page_config(page_title="نظام المبيعات - حسن", page_icon="📊", layout="centered")


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

# واجهة تسجيل الدخول
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>تسجيل الدخول - نظام المبيعات</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("اسم المستخدم:")
            password_input = st.text_input("كلمة المرور:", type="password")
            submit_login = st.form_submit_button("دخول النظام", use_container_width=True)

            if submit_login:
                if authenticate_user(username_input.strip(), password_input.strip()):
                    st.session_state.logged_in = True
                    st.session_state.username = username_input.strip()
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Developed by <b>HASSAN ELNOUSH</b></p>",
                unsafe_allow_html=True)

else:
    # ----------------- الشريط الجانبي (Sidebar) لإدارة النظام والأرشيف -----------------
    st.sidebar.markdown(f"### مرحباً، {st.session_state.username}")
    st.sidebar.markdown("---")

    # قائمة التنقل الجانبية
    nav_option = st.sidebar.radio("القائمة الرئيسية", ["تسجيل مبيعات", "أرشيف العمليات", "إقفال اليومية"])

    st.sidebar.markdown("---")
    if st.sidebar.button("تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.markdown(
        "<p style='text-align: center; color: gray; font-size: 12px;'>Developer: <b>HASSAN ELNOUSH</b></p>",
        unsafe_allow_html=True)

    # ----------------- 1. شاشة تسجيل مبيعات (الواجهة الافتراضية) -----------------
    if nav_option == "تسجيل مبيعات":
        st.title("📊 لوحة تحكم نظام المبيعات")

        # نموذج تسجيل عملية مبيعات جديدة (أرقام صحيحة بدون أعشار)
        with st.form("sales_form", clear_on_submit=True):
            st.subheader("إضافة عملية بيع جديدة")
            amount = st.number_input("مبلغ العملية (أرقام صحيحة فقط):", min_value=0, step=1, format="%d")
            payment_type = st.selectbox("طريقة الدفع:", ["نقداً", "بنكك"])
            transaction_ref = st.text_input("رقم العملية المرجعي (مطلوب لبنكك فقط):")

            submit_sale = st.form_submit_button("حفظ العملية", use_container_width=True)

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

        # قسم عرض إجمالي المجاميع السريعة في الواجهة الرئيسية
        st.markdown("---")
        st.subheader("📈 ملخص المجاميع العامة")

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT payment_type, SUM(amount) as total FROM transactions WHERE status = 'open' GROUP BY payment_type")
            totals = cursor.fetchall()

            cash_total = 0
            bank_total = 0
            for row in totals:
                if row['payment_type'] == 'نقداً':
                    cash_total = row['total'] or 0
                elif row['payment_type'] == 'بنكك':
                    bank_total = row['total'] or 0

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(label="💵 إجمالي الكاش المفتوح", value=f"{cash_total:,} جنيه")
            with col_b:
                st.metric(label="🏦 إجمالي بنكك المفتوح", value=f"{bank_total:,} جنيه")

            cursor.close()
            conn.close()

    # ----------------- 2. شاشة أرشيف العمليات (مخفية في القائمة الجانبية) -----------------
    elif nav_option == "أرشيف العمليات":
        st.title("📅 أرشيف العمليات السابقة")
        st.info("هنا يمكنك الاطلاع على كافة سجلات العمليات السابقة بشكل خاص.")

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, amount, payment_type, transaction_ref, status, created_at FROM transactions ORDER BY created_at DESC")
            transactions_data = cursor.fetchall()

            if transactions_data:
                st.dataframe(transactions_data, use_container_width=True)
            else:
                st.info("لا توجد عمليات مسجلة حتى الآن.")

            cursor.close()
            conn.close()

    # ----------------- 3. شاشة إقفال اليومية -----------------
    elif nav_option == "إقفال اليومية":
        st.title("🔒 إقفال اليومية")
        st.warning("عملية إقفال اليومية تقوم بتسوية العمليات الحالية وتصفير الحسابات المفتوحة لبدء يومية جديدة.")

        if st.button("تأكيد إقفال اليومية الحالية", type="primary"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # تحديث حالة العمليات من open إلى closed
                cursor.execute("UPDATE transactions SET status = 'closed' WHERE status = 'open'")
                conn.commit()
                cursor.close()
                conn.close()
                st.success("تم إقفال اليومية بنجاح وتصفير العمليات المفتوحة!")
                st.rerun()