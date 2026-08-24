import streamlit as st
import mysql.connector
import pandas as pd


# =========================================================
# 1. الاتصال بقاعدة البيانات
# =========================================================
def get_db_connection():
    """
    دالة الاتصال بقاعدة بيانات MySQL.
    تقوم بفتح الاتصال وإرجاعه للاستخدام في الاستعلامات.
    """
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"]["port"])
        )
    except Exception as err:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {err}")
        return None


# =========================================================
# 2. التحقق من المستخدم (نظام الحماية)
# =========================================================
def authenticate_user(username, password):
    """
    التحقق من صحة بيانات الدخول من جدول المستخدمين users.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None


# =========================================================
# 3. إعدادات الصفحة والجلسة
# =========================================================
st.set_page_config(page_title="HASSAN ELNOUSH - Sales System", layout="centered")

# تهيئة حالة تسجيل الدخول في الجلسة
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# =========================================================
# 4. شاشة تسجيل الدخول
# =========================================================
if not st.session_state["logged_in"]:
    st.title("🔒 تسجيل الدخول")
    st.write("نظام المبيعات - **HASSAN ELNOUSH**")

    with st.form("login_form"):
        username_input = st.text_input("اسم المستخدم:")
        password_input = st.text_input("كلمة المرور:", type="password")
        login_button = st.form_submit_button("دخول")

    if login_button:
        if authenticate_user(username_input.strip(), password_input.strip()):
            st.session_state["logged_in"] = True
            st.success("تم تسجيل الدخول بنجاح!")
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

# =========================================================
# 5. الواجهة الرئيسية لبرنامج المبيعات
# =========================================================
else:
    # --- الترويسة الرئيسية ---
    col_header, col_logout = st.columns([3, 1])
    with col_header:
        st.title("💼 HASSAN ELNOUSH")
        st.caption("نظام إدارة المبيعات واليومية")
    with col_logout:
        if st.button("تسجيل الخروج"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.divider()

    # --- نموذج تسجيل عملية مبيعات جديدة ---
    st.subheader("📝 تسجيل عملية مبيعات جديدة")

    with st.form("sales_form", clear_on_submit=True):
        amount = st.number_input("المبلغ (بالجنيه):", min_value=0.0, step=1.0, format="%.2f")
        payment_type = st.radio("طريقة الدفع:", ["كاش", "فيزا"], horizontal=True)

        # إدخال رقم العملية المرجعي في حالة الفيزا
        transaction_ref = st.text_input("رقم العملية المرجعي (مطلوب للفيزا فقط):")

        submit_sale = st.form_submit_button("حفظ العملية")

    if submit_sale:
        if amount <= 0:
            st.warning("يرجى إدخال مبلغ أكبر من الصفر!")
        elif payment_type == "فيزا" and not transaction_ref.strip():
            st.warning("يرجى إدخال رقم العملية المرجعي للفيزا!")
        else:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                ref_val = transaction_ref.strip() if payment_type == "فيزا" else None
                query = "INSERT INTO transactions (amount, payment_type, transaction_ref, status) VALUES (%s, %s, %s, 'open')"
                cursor.execute(query, (amount, payment_type, ref_val))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("تم تسجيل عملية المبيعات بنجاح!")
                st.rerun()

    st.divider()

    # --- عرض عمليات اليومية الحالية المفتوحة ---
    st.subheader("📊 مبيعات اليومية الحالية")

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, amount, payment_type, IFNULL(transaction_ref, '-'), created_at FROM transactions WHERE status = 'open' ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            # تحويل البيانات إلى الجدول
            df = pd.DataFrame(rows, columns=["الرقم", "المبلغ", "طريقة الدفع", "رقم العملية المرجعي", "التاريخ والوقت"])
            st.dataframe(df, use_container_width=True)

            # حساب الإجماليات
            total_cash = sum(r[1] for r in rows if r[2] == "كاش")
            total_visa = sum(r[1] for r in rows if r[2] == "فيزا")
            grand_total = total_cash + total_visa

            # عرض الإحصائيات في بطاقات
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الكاش", f"{total_cash:,.2f} جنيه")
            c2.metric("إجمالي الفيزا", f"{total_visa:,.2f} جنيه")
            c3.metric("إجمالي المبيعات الكلي", f"{grand_total:,.2f} جنيه")

            # --- زر إقفال اليومية ---
            st.write("---")
            if st.button("🔒 إقفال اليومية الحالية", type="primary", use_container_width=True):
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE transactions SET status = 'closed' WHERE status = 'open'")
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("تم إقفال اليومية بنجاح وحفظ كافة بياناتها!")
                    st.rerun()
        else:
            st.info("لا توجد مبيعات مسجلة في اليومية الحالية حتى الآن.")

    # --- أرشيف اليوميات المغلقة للمراجعة لاحقاً ---
    st.divider()
    with st.expander("📂 مراجعة أرشيف اليوميات السابقة"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, amount, payment_type, IFNULL(transaction_ref, '-'), created_at FROM transactions WHERE status = 'closed' ORDER BY id DESC")
            closed_rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if closed_rows:
                df_closed = pd.DataFrame(closed_rows, columns=["الرقم", "المبلغ", "طريقة الدفع", "رقم العملية المرجعي",
                                                               "التاريخ والوقت"])
                st.dataframe(df_closed, use_container_width=True)
            else:
                st.write("لا توجد يوميات مغلقة مقفلة سابقاً.")
            