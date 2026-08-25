import streamlit as st
import mysql.connector
from datetime import datetime, date
import hashlib
import pandas as pd
import time

# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="نظام المبيعات والمصروفات - حسن",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ===================== دوال المساعدة =====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
            return None
    return None


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


def get_today_expenses():
    """الحصول على مصروفات اليوم"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            today = date.today()
            cursor.execute(
                "SELECT id, description, amount, category, expense_date, created_by, created_at FROM expenses WHERE expense_date = %s AND closing_batch IS NULL",
                (today,)
            )
            expenses = cursor.fetchall()
            cursor.close()
            conn.close()
            return expenses
        except Exception as e:
            return []
    return []


def get_total_expenses_today():
    """إجمالي مصروفات اليوم"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            today = date.today()
            cursor.execute(
                "SELECT SUM(amount) as total FROM expenses WHERE expense_date = %s AND closing_batch IS NULL",
                (today,)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] or 0
        except Exception as e:
            return 0
    return 0


def get_expense_categories():
    """الحصول على فئات المصروفات"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM expense_categories ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return categories
        except Exception as e:
            return ['إيجار', 'رواتب', 'كهرباء', 'ماء', 'إنترنت', 'مواصلات', 'مشتريات', 'أخرى']
    return ['إيجار', 'رواتب', 'كهرباء', 'ماء', 'إنترنت', 'مواصلات', 'مشتريات', 'أخرى']


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


def ensure_tables_exist():
    """التأكد من وجود الجداول المطلوبة"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # إنشاء جدول expense_categories إذا لم يكن موجوداً
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expense_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    icon VARCHAR(10) DEFAULT '💰'
                )
            """)

            # إضافة الفئات الافتراضية
            categories = [
                ('إيجار', '🏠'), ('رواتب', '👨‍💼'), ('كهرباء', '⚡'),
                ('ماء', '💧'), ('إنترنت', '🌐'), ('مواصلات', '🚗'),
                ('مشتريات', '🛒'), ('أخرى', '📌')
            ]
            for name, icon in categories:
                cursor.execute(
                    "INSERT IGNORE INTO expense_categories (name, icon) VALUES (%s, %s)",
                    (name, icon)
                )

            # إنشاء جدول expenses إذا لم يكن موجوداً
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    expense_date DATE NOT NULL,
                    closing_batch VARCHAR(50),
                    created_by VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (expense_date),
                    INDEX idx_batch (closing_batch),
                    INDEX idx_category (category)
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطأ في إنشاء الجداول: {e}")
            return False
    return False


# ===================== تهيئة الجلسة =====================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page_num = 0

# التأكد من وجود المستخدمين والجداول
ensure_users_exist()
ensure_tables_exist()

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
        ["📊 تسجيل مبيعات", "💰 المصروفات", "📅 أرشيف العمليات", "🔒 إقفال اليومية"]
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
        expenses_today = get_total_expenses_today()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total
        net_profit = total_amount - expenses_today

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 عدد العمليات اليوم", total_transactions)
        with col2:
            st.metric("💰 إجمالي المبيعات", f"{total_amount:,.0f} جنيه")
        with col3:
            st.metric("💸 المصروفات اليوم", f"{expenses_today:,.0f} جنيه", delta="-", delta_color="inverse")
        with col4:
            st.metric("📈 صافي الربح", f"{net_profit:,.0f} جنيه")

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
        st.subheader("📈 ملخص اليوم")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("💵 الكاش المفتوح", f"{cash_total:,.0f} جنيه", f"{cash_count} عملية")
        with col_b:
            st.metric("🏦 بنكك المفتوح", f"{bank_total:,.0f} جنيه", f"{bank_count} عملية")
        with col_c:
            st.metric("💸 المصروفات اليوم", f"{expenses_today:,.0f} جنيه")

    # ====== 2. المصروفات ======
    elif nav_option == "💰 المصروفات":
        st.title("💰 نظام المصروفات")

        # إضافة مصروف جديد
        with st.expander("➕ إضافة مصروف جديد", expanded=True):
            with st.form("expense_form", clear_on_submit=True):
                col_exp1, col_exp2 = st.columns(2)
                with col_exp1:
                    description = st.text_input("📝 وصف المصروف:", placeholder="مثال: فاتورة كهرباء")
                with col_exp2:
                    amount = st.number_input("💵 المبلغ:", min_value=1, step=1, format="%d")

                col_exp3, col_exp4 = st.columns(2)
                with col_exp3:
                    category = st.selectbox("📂 الفئة:", get_expense_categories())
                with col_exp4:
                    expense_date = st.date_input("📅 التاريخ:", value=date.today())

                submit_expense = st.form_submit_button("💾 حفظ المصروف", use_container_width=True, type="primary")

                if submit_expense:
                    if not description.strip():
                        st.warning("⚠️ يرجى إدخال وصف للمصروف!")
                    elif amount <= 0:
                        st.warning("⚠️ يرجى إدخال مبلغ أكبر من الصفر!")
                    else:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                query = "INSERT INTO expenses (description, amount, category, expense_date, created_by) VALUES (%s, %s, %s, %s, %s)"
                                cursor.execute(query, (description.strip(), amount, category, expense_date,
                                                       st.session_state.username))
                                conn.commit()
                                log_activity(st.session_state.username, "إضافة مصروف",
                                             f"الوصف: {description}, المبلغ: {amount}, الفئة: {category}")
                                cursor.close()
                                conn.close()
                                st.success(f"✅ تم إضافة المصروف بنجاح! ({amount:,.0f} جنيه)")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ: {e}")

        # عرض المصروفات اليومية
        st.subheader("📋 مصروفات اليوم")

        expenses = get_today_expenses()
        total_expenses = get_total_expenses_today()

        if expenses:
            # إحصائيات سريعة
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("📊 عدد المصروفات", len(expenses))
            with col_stat2:
                st.metric("💰 إجمالي المصروفات", f"{total_expenses:,.0f} جنيه")
            with col_stat3:
                avg_expense = total_expenses / len(expenses) if expenses else 0
                st.metric("📊 متوسط المصروف", f"{avg_expense:,.0f} جنيه")

            st.markdown("---")

            # عرض المصروفات في جدول
            df = pd.DataFrame(expenses)
            df_display = df[['description', 'amount', 'category', 'created_by', 'created_at']]
            df_display.columns = ['الوصف', 'المبلغ', 'الفئة', 'أضيف بواسطة', 'التاريخ']
            st.dataframe(df_display, use_container_width=True)

            # إجمالي حسب الفئة
            st.subheader("📊 توزيع المصروفات حسب الفئة")
            category_totals = df.groupby('category')['amount'].sum().reset_index()
            category_totals.columns = ['الفئة', 'المبلغ']
            st.dataframe(category_totals, use_container_width=True)

            # رسم بياني بسيط
            if len(category_totals) > 0:
                st.bar_chart(category_totals.set_index('الفئة'))
        else:
            st.info("📭 لا توجد مصروفات اليوم")

        # عرض مصروفات سابقة
        with st.expander("📅 مصروفات الأيام السابقة"):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT description, amount, category, expense_date, created_by FROM expenses WHERE expense_date < %s ORDER BY expense_date DESC LIMIT 50",
                        (date.today(),)
                    )
                    old_expenses = cursor.fetchall()
                    cursor.close()
                    conn.close()

                    if old_expenses:
                        df_old = pd.DataFrame(old_expenses)
                        df_old.columns = ['الوصف', 'المبلغ', 'الفئة', 'التاريخ', 'أضيف بواسطة']
                        st.dataframe(df_old, use_container_width=True)
                    else:
                        st.info("📭 لا توجد مصروفات سابقة")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

    # ====== 3. أرشيف العمليات ======
    elif nav_option == "📅 أرشيف العمليات":
        st.title("📅 أرشيف الإقفالات")
        st.info("ℹ️ العمليات التي تم إقفالها مع المصروفات المرتبطة")

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
                    # عرض ملخص المصروفات لكل إقفال
                    for batch in archive_data:
                        batch_id = batch['closing_batch']
                        if batch_id:
                            cursor.execute(
                                "SELECT SUM(amount) as total_expenses FROM expenses WHERE closing_batch = %s",
                                (batch_id,)
                            )
                            exp_result = cursor.fetchone()
                            batch['expenses_total'] = exp_result['total_expenses'] if exp_result else 0
                        else:
                            batch['expenses_total'] = 0

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

    # ====== 4. إقفال اليومية (النسخة الجديدة) ======
    elif nav_option == "🔒 إقفال اليومية":
        st.title("🔒 إقفال اليومية")

        cash_total, bank_total, cash_count, bank_count = get_daily_totals()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total
        expenses_today = get_total_expenses_today()
        net_profit = total_amount - expenses_today

        # عرض ملخص اليوم
        st.subheader("📊 ملخص اليوم")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 عدد العمليات", total_transactions)
        with col2:
            st.metric("💰 إجمالي المبيعات", f"{total_amount:,.0f} جنيه")
        with col3:
            st.metric("💸 المصروفات", f"{expenses_today:,.0f} جنيه", delta="-", delta_color="inverse")
        with col4:
            st.metric("📈 صافي الربح", f"{net_profit:,.0f} جنيه")

        st.markdown("---")

        # عرض المصروفات قبل الإقفال
        expenses = get_today_expenses()
        if expenses:
            with st.expander("📋 عرض المصروفات اليومية", expanded=True):
                df_exp = pd.DataFrame(expenses)
                df_exp_display = df_exp[['description', 'amount', 'category']]
                df_exp_display.columns = ['الوصف', 'المبلغ', 'الفئة']
                st.dataframe(df_exp_display, use_container_width=True)
                st.info(f"💸 إجمالي المصروفات: {expenses_today:,.0f} جنيه")
        else:
            st.info("📭 لا توجد مصروفات اليوم")

        st.markdown("---")

        # تأكيد الإقفال (بدون كتابة كلمة إقفال)
        st.warning("⚠️ **تنبيه:** سيتم إقفال اليومية الحالية ونقل جميع العمليات والمصروفات إلى الأرشيف.")

        confirm_checkbox = st.checkbox("✅ أوافق على إقفال اليومية الحالية")

        if st.button("🔒 تأكيد إقفال اليومية", type="primary", use_container_width=True, disabled=not confirm_checkbox):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                    # إقفال العمليات
                    query = "UPDATE transactions SET status = 'closed', closing_batch = %s WHERE status = 'open'"
                    cursor.execute(query, (batch_id,))
                    transactions_closed = cursor.rowcount

                    # ربط المصروفات بالإقفال
                    today = date.today()
                    query_exp = "UPDATE expenses SET closing_batch = %s WHERE expense_date = %s AND closing_batch IS NULL"
                    cursor.execute(query_exp, (batch_id, today))
                    expenses_closed = cursor.rowcount

                    conn.commit()

                    log_activity(
                        st.session_state.username,
                        "إقفال يومية",
                        f"رقم الإقفال: {batch_id}, عمليات: {transactions_closed}, مصروفات: {expenses_closed}"
                    )

                    cursor.close()
                    conn.close()

                    st.success(f"✅ تم إقفال اليومية بنجاح!")
                    st.info(f"📋 رقم الإقفال: **{batch_id}**")
                    st.info(f"📊 العمليات المقفلة: **{transactions_closed}**")
                    st.info(f"💰 المصروفات المقفلة: **{expenses_closed}**")
                    st.info(f"📈 صافي الربح: **{net_profit:,.0f} جنيه**")
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

# ===================== نهاية الملف =====================