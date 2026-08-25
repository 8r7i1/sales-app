import streamlit as st
import mysql.connector
from datetime import datetime
import hashlib
import pandas as pd
import time
from io import StringIO

# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="نظام المبيعات - حسن",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ===================== دوال المساعدة =====================

# دالة لتشفير كلمة المرور
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# دالة الاتصال بقاعدة البيانات
def get_db_connection(max_retries=3):
    for attempt in range(max_retries):
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
            if attempt == max_retries - 1:
                st.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
                return None
            time.sleep(1)
    return None


# دالة تسجيل سجل العمليات
def log_activity(username, action, details=""):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (username, action, details, timestamp) VALUES (%s, %s, %s, NOW())",
                (username, action, details)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            return False
    return False


# دالة التحقق من تسجيل الدخول
def authenticate_user(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            hashed_pw = hash_password(password)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username.strip(), hashed_pw))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            st.error(f"خطأ في التحقق: {e}")
            return None
    return None


# دالة الحصول على مجاميع اليوم
def get_daily_totals():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT payment_type, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE status = 'open' GROUP BY payment_type"
            )
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            cash_total = 0
            bank_total = 0
            cash_count = 0
            bank_count = 0

            for row in results:
                if row['payment_type'] == 'نقداً':
                    cash_total = row['total'] or 0
                    cash_count = row['count'] or 0
                elif row['payment_type'] == 'بنكك':
                    bank_total = row['total'] or 0
                    bank_count = row['count'] or 0

            return cash_total, bank_total, cash_count, bank_count
        except Exception as e:
            return 0, 0, 0, 0
    return 0, 0, 0, 0


# دالة التأكد من وجود مستخدمين
def ensure_users_exist():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()

            if result[0] == 0:
                users_data = [
                    ('admin', hash_password('admin123'), 'مدير النظام', 'admin'),
                    ('user1', hash_password('user123'), 'مستخدم تجريبي', 'user'),
                    ('manager', hash_password('manager123'), 'مدير مبيعات', 'manager'),
                    ('user', hash_password('user123'), 'مستخدم عادي', 'user')
                ]

                for username, password, full_name, role in users_data:
                    cursor.execute(
                        "INSERT INTO users (username, password, full_name, role) VALUES (%s, %s, %s, %s)",
                        (username, password, full_name, role)
                    )

                conn.commit()
                print(f"✅ تم إضافة {len(users_data)} مستخدم")

            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    return False


# ===================== تهيئة الجلسة =====================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page_num = 0

# التأكد من وجود مستخدمين
ensure_users_exist()

# ===================== واجهة تسجيل الدخول =====================

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 تسجيل الدخول - نظام المبيعات</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("👤 اسم المستخدم:")
            password_input = st.text_input("🔑 كلمة المرور:", type="password")
            submit_login = st.form_submit_button("🚪 دخول النظام", use_container_width=True)

            if submit_login:
                if not username_input.strip() or not password_input.strip():
                    st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
                else:
                    user = authenticate_user(username_input.strip(), password_input.strip())
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username_input.strip()
                        log_activity(username_input.strip(), "تسجيل دخول", "نجح تسجيل الدخول")
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة!")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 14px;'>Developed by <b>HASSAN ELNOUSH</b> © 2026</p>",
        unsafe_allow_html=True
    )

# ===================== الواجهة الرئيسية =====================

else:
    # الشريط الجانبي
    st.sidebar.markdown(f"### 👋 مرحباً، {st.session_state.username}")
    st.sidebar.markdown("---")

    nav_option = st.sidebar.radio(
        "📋 القائمة الرئيسية",
        ["📊 تسجيل مبيعات", "📅 أرشيف العمليات", "🔒 إقفال اليومية"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
        log_activity(st.session_state.username, "تسجيل خروج", "تم تسجيل الخروج")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page_num = 0
        st.rerun()

    st.sidebar.markdown(
        f"<p style='text-align: center; color: gray; font-size: 12px;'>👨‍💻 Developer: <b>HASSAN ELNOUSH</b><br>📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>",
        unsafe_allow_html=True
    )

    # ====== 1. تسجيل مبيعات ======
    if nav_option == "📊 تسجيل مبيعات":
        st.title("📊 لوحة تحكم نظام المبيعات")

        cash_total, bank_total, cash_count, bank_count = get_daily_totals()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 عدد العمليات اليوم", total_transactions)
        with col2:
            st.metric("💰 إجمالي المبيعات", f"{total_amount:,.0f} جنيه")
        with col3:
            st.metric("⏱️ آخر تحديث", datetime.now().strftime("%H:%M"))

        st.markdown("---")

        with st.form("sales_form", clear_on_submit=True):
            st.subheader("➕ إضافة عملية بيع جديدة")

            col_form1, col_form2 = st.columns(2)
            with col_form1:
                amount = st.number_input("💵 مبلغ العملية:", min_value=1, step=1, format="%d")
            with col_form2:
                payment_type = st.selectbox("💳 طريقة الدفع:", ["نقداً", "بنكك"])

            transaction_ref = st.text_input("🔢 رقم العملية المرجعي:", placeholder="مطلوب فقط للدفع عبر بنكك")

            submit_sale = st.form_submit_button("💾 حفظ العملية", use_container_width=True, type="primary")

        if submit_sale:
            if amount <= 0:
                st.warning("⚠️ يرجى إدخال مبلغ أكبر من الصفر!")
            elif payment_type == "بنكك" and not transaction_ref.strip():
                st.warning("⚠️ يرجى إدخال رقم العملية المرجعي!")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        ref_val = transaction_ref.strip() if payment_type == "بنكك" else None
                        query = "INSERT INTO transactions (amount, payment_type, transaction_ref, status) VALUES (%s, %s, %s, 'open')"
                        cursor.execute(query, (amount, payment_type, ref_val))
                        conn.commit()
                        log_activity(st.session_state.username, "إضافة مبيعات",
                                     f"المبلغ: {amount}, الطريقة: {payment_type}")
                        cursor.close()
                        conn.close()
                        st.success(f"✅ تم تسجيل العملية بنجاح! ({amount:,} جنيه)")
                        st.balloons()
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")

        st.markdown("---")
        st.subheader("📈 ملخص المجاميع المفتوحة")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💵 إجمالي الكاش المفتوح", f"{cash_total:,.0f} جنيه", f"{cash_count} عملية")
        with col_b:
            st.metric("🏦 إجمالي بنكك المفتوح", f"{bank_total:,.0f} جنيه", f"{bank_count} عملية")

    # ====== 2. أرشيف العمليات ======
    elif nav_option == "📅 أرشيف العمليات":
        st.title("📅 أرشيف الإقفالات")
        st.info("ℹ️ العمليات التي تم إقفالها")

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                page_size = 20
                offset = st.session_state.page_num * page_size

                cursor.execute("SELECT COUNT(*) as total FROM transactions WHERE status = 'closed'")
                total_records = cursor.fetchone()['total']
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1

                cursor.execute(
                    "SELECT id, amount, payment_type, transaction_ref, closing_batch, created_at FROM transactions WHERE status = 'closed' ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (page_size, offset)
                )
                archive_data = cursor.fetchall()

                if archive_data:
                    st.dataframe(archive_data, use_container_width=True)

                    col_pagi1, col_pagi2, col_pagi3 = st.columns([1, 2, 1])
                    with col_pagi1:
                        if st.button("⬅️ السابق", disabled=(st.session_state.page_num == 0)):
                            st.session_state.page_num -= 1
                            st.rerun()
                    with col_pagi2:
                        st.write(f"📄 صفحة {st.session_state.page_num + 1} من {total_pages}")
                    with col_pagi3:
                        if st.button("التالي ➡️", disabled=(st.session_state.page_num >= total_pages - 1)):
                            st.session_state.page_num += 1
                            st.rerun()
                else:
                    st.info("📭 لا توجد عمليات مقفلة")

                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"❌ خطأ: {e}")

    # ====== 3. إقفال اليومية ======
    elif nav_option == "🔒 إقفال اليومية":
        st.title("🔒 إقفال اليومية")

        cash_total, bank_total, cash_count, bank_count = get_daily_totals()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total

        st.warning(
            f"⚠️ **تنبيه:** سوف يتم إقفال {total_transactions} عملية بمبلغ {total_amount:,.0f} جنيه"
        )

        col_warn1, col_warn2 = st.columns(2)
        with col_warn1:
            st.metric("📊 عدد العمليات", total_transactions)
        with col_warn2:
            st.metric("💰 إجمالي المبلغ", f"{total_amount:,.0f} جنيه")

        confirm_text = st.text_input("✍️ اكتب 'إقفال' لتأكيد العملية:", placeholder="اكتب إقفال هنا")

        if st.button("🔒 تأكيد الإقفال", type="primary", use_container_width=True, disabled=(confirm_text != "إقفال")):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    query = "UPDATE transactions SET status = 'closed', closing_batch = %s WHERE status = 'open'"
                    cursor.execute(query, (batch_id,))
                    affected_rows = cursor.rowcount
                    conn.commit()
                    log_activity(st.session_state.username, "إقفال يومية", f"رقم الإقفال: {batch_id}")
                    cursor.close()
                    conn.close()
                    st.success(f"✅ تم إقفال اليومية بنجاح! (رقم: {batch_id})")
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

# ===================== نهاية الملف =====================