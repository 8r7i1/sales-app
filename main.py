import streamlit as st
import mysql.connector
from datetime import datetime, date, timedelta
import hashlib
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# إعدادات صفحة Streamlit
# ============================================
st.set_page_config(
    page_title="نظام المطاعم - المبيعات والمصروفات",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CSS المخصص للواجهة
# ============================================
def apply_custom_css():
    """تطبيق التنسيقات المخصصة للواجهة"""
    st.markdown("""
    <style>
    /* خطوط جميلة */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700&display=swap');
    * {
        font-family: 'Tajawal', sans-serif;
    }

    /* خلفية الصفحة */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* بطاقات المعلومات */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .metric-icon {
        font-size: 30px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        color: #666;
        font-size: 14px;
    }

    /* أزرار مخصصة */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }

    /* شريط جانبي */
    .css-1d391kg {
        background: linear-gradient(180deg, #1E3A8A 0%, #1a1a2e 100%);
    }
    .css-1d391kg .stMarkdown {
        color: white;
    }

    /* بطاقات النماذج */
    .form-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    /* عنوان رئيسي */
    .main-header {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #1E3A8A 0%, #667eea 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.3);
    }
    .main-header h1 {
        font-size: 45px;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        font-size: 18px;
        opacity: 0.9;
        margin: 10px 0 0 0;
    }

    /* شعار */
    .logo-container {
        text-align: center;
        padding: 20px 0;
    }
    .logo-text {
        font-size: 60px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    /* صندوق تسجيل الدخول */
    .login-box {
        background: rgba(255,255,255,0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        max-width: 450px;
        margin: 0 auto;
    }

    /* أيقونات الحالة */
    .status-open {
        color: #10B981;
        font-weight: bold;
    }
    .status-closed {
        color: #EF4444;
        font-weight: bold;
    }

    /* تحسينات الموبايل */
    @media only screen and (max-width: 600px) {
        .main-header h1 {
            font-size: 28px;
        }
        .metric-value {
            font-size: 20px;
        }
        .stButton button {
            width: 100% !important;
        }
        .row-widget {
            flex-wrap: wrap !important;
        }
    }

    /* شريط التقدم */
    .custom-progress {
        background: #e0e0e0;
        border-radius: 10px;
        height: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    .custom-progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    </style>
    """, unsafe_allow_html=True)


# تطبيق التنسيقات
apply_custom_css()


# ============================================
# دوال المساعدة
# ============================================

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
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND is_active = TRUE"
            cursor.execute(query, (username.strip(), hashed_pw))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            return None
    return None


# ============================================
# دوال الصلاحيات
# ============================================

def get_user_role(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT role, restaurant_name FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            return None
    return None


def is_developer(username):
    user = get_user_role(username)
    return user and user['role'] == 'admin'


def get_user_restaurant(username):
    user = get_user_role(username)
    return user['restaurant_name'] if user else None


def get_user_transactions(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            user = get_user_role(username)
            if user and user['role'] == 'admin':
                cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM transactions WHERE username = %s ORDER BY created_at DESC", (username,))
            transactions = cursor.fetchall()
            cursor.close()
            conn.close()
            return transactions
        except Exception as e:
            return []
    return []


def get_user_expenses(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            user = get_user_role(username)
            if user and user['role'] == 'admin':
                cursor.execute("SELECT * FROM expenses ORDER BY expense_date DESC")
            else:
                cursor.execute("SELECT * FROM expenses WHERE username = %s ORDER BY expense_date DESC", (username,))
            expenses = cursor.fetchall()
            cursor.close()
            conn.close()
            return expenses
        except Exception as e:
            return []
    return []


def get_daily_totals(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            user = get_user_role(username)
            if user and user['role'] == 'admin':
                cursor.execute(
                    "SELECT payment_type, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE status = 'open' GROUP BY payment_type"
                )
            else:
                cursor.execute(
                    "SELECT payment_type, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE status = 'open' AND username = %s GROUP BY payment_type",
                    (username,)
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


def get_today_expenses(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            today = date.today()
            user = get_user_role(username)
            if user and user['role'] == 'admin':
                cursor.execute(
                    "SELECT id, description, amount, category, expense_date, username, restaurant_name, created_at FROM expenses WHERE expense_date = %s AND closing_batch IS NULL",
                    (today,)
                )
            else:
                cursor.execute(
                    "SELECT id, description, amount, category, expense_date, username, restaurant_name, created_at FROM expenses WHERE expense_date = %s AND closing_batch IS NULL AND username = %s",
                    (today, username)
                )
            expenses = cursor.fetchall()
            cursor.close()
            conn.close()
            return expenses
        except Exception as e:
            return []
    return []


def get_total_expenses_today(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            today = date.today()
            user = get_user_role(username)
            if user and user['role'] == 'admin':
                cursor.execute(
                    "SELECT SUM(amount) as total FROM expenses WHERE expense_date = %s AND closing_batch IS NULL",
                    (today,)
                )
            else:
                cursor.execute(
                    "SELECT SUM(amount) as total FROM expenses WHERE expense_date = %s AND closing_batch IS NULL AND username = %s",
                    (today, username)
                )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] or 0
        except Exception as e:
            return 0
    return 0


def get_expense_categories():
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


def get_all_restaurants():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, full_name, restaurant_name FROM users WHERE role = 'user' AND is_active = TRUE")
            restaurants = cursor.fetchall()
            cursor.close()
            conn.close()
            return restaurants
        except Exception as e:
            return []
    return []


def ensure_users_exist():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()

            if result[0] == 0:
                users_data = [
                    ('developer', hash_password('dev123'), 'المطور', 'admin', 'المطور', True),
                    ('karoly', hash_password('karoly123'), 'مطعم كرولي الصحافة', 'user', 'مطعم كرولي الصحافة', True),
                    ('ghost', hash_password('ghost123'), 'محل حلويات Ghost Sweet', 'user', 'محل حلويات Ghost Sweet',
                     True),
                ]

                for username, password, full_name, role, restaurant_name, is_active in users_data:
                    cursor.execute(
                        "INSERT INTO users (username, password, full_name, role, restaurant_name, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
                        (username, password, full_name, role, restaurant_name, is_active)
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
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expense_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    icon VARCHAR(10) DEFAULT '💰'
                )
            """)

            categories = [
                ('إيجار', '🏠'), ('رواتب', '👨‍💼'), ('كهرباء', '⚡'),
                ('ماء', '💧'), ('إنترنت', '🌐'), ('مواصلات', '🚗'),
                ('مشتريات', '🛒'), ('أخرى', '📌')
            ]
            for name, icon in categories:
                cursor.execute("INSERT IGNORE INTO expense_categories (name, icon) VALUES (%s, %s)", (name, icon))

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    expense_date DATE NOT NULL,
                    closing_batch VARCHAR(50),
                    username VARCHAR(50),
                    restaurant_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (expense_date),
                    INDEX idx_batch (closing_batch),
                    INDEX idx_category (category),
                    INDEX idx_username (username)
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


# ============================================
# تهيئة الجلسة
# ============================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.archive_page = 0
    st.session_state.show_restaurants = False

ensure_users_exist()
ensure_tables_exist()

# ============================================
# واجهة تسجيل الدخول
# ============================================

if not st.session_state.logged_in:
    # تنسيق صفحة تسجيل الدخول
    st.markdown("""
        <div style='min-height: 100vh; display: flex; align-items: center; justify-content: center;'>
            <div style='width: 100%; max-width: 500px;'>
    """, unsafe_allow_html=True)

    # الشعار
    st.markdown("""
        <div class='logo-container'>
            <div class='logo-text'>🍽️</div>
            <h1 style='color: #1E3A8A; font-size: 35px; margin: 10px 0;'>نظام المطاعم</h1>
            <p style='color: #666; font-size: 16px;'>إدارة المبيعات والمصروفات</p>
        </div>
    """, unsafe_allow_html=True)

    # صندوق تسجيل الدخول
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🔐 تسجيل الدخول</h3>", unsafe_allow_html=True)

            username_input = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
            password_input = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")

            col1, col2 = st.columns([1, 1])
            with col1:
                st.checkbox("تذكرني 🔑")
            with col2:
                st.markdown("[🔓 نسيت كلمة المرور؟]")

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

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <hr>
        <p style='text-align: center; color: gray; font-size: 14px;'>
            Developed by <b>المطور</b> © 2026
        </p>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ============================================
# الواجهة الرئيسية (بعد تسجيل الدخول)
# ============================================

# الحصول على معلومات المستخدم
user = get_user_role(st.session_state.username)
is_dev = user and user['role'] == 'admin'
restaurant_name = user['restaurant_name'] if user else ''

# ============================================
# الهيدر الرئيسي
# ============================================

st.markdown(f"""
    <div class='main-header'>
        <div style='display: flex; align-items: center; justify-content: center; gap: 20px;'>
            <span style='font-size: 40px;'>🍽️</span>
            <div>
                <h1>نظام المطاعم</h1>
                <p>إدارة المبيعات والمصروفات</p>
            </div>
        </div>
        <div style='margin-top: 10px;'>
            <span style='background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;'>
                {f"👨‍💻 {st.session_state.username} - {restaurant_name}" if not is_dev else f"👨‍💻 {st.session_state.username} - صلاحية كاملة"}
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# الشريط الجانبي
# ============================================

with st.sidebar:
    # صورة البروفايل
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <div style='width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 35px; color: white;'>
                {'' if is_dev else '🍽️'}
                {'' if not is_dev else '👨‍💻'}
            </div>
            <h3 style='color: white; margin: 10px 0 5px 0;'>{st.session_state.username}</h3>
            <p style='color: rgba(255,255,255,0.8); font-size: 14px;'>
                {f"🏪 {restaurant_name}" if not is_dev else "👨‍💻 المطور"}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # القائمة
    nav_option = st.sidebar.radio(
        "📋 القائمة الرئيسية",
        ["📊 لوحة التحكم", "💰 المصروفات", "📅 الأرشيف", "🔒 إقفال اليومية"]
    )

    st.sidebar.markdown("---")

    # إدارة المطاعم (للمطور فقط)
    if is_dev:
        if st.sidebar.button("👥 إدارة المطاعم", use_container_width=True):
            st.session_state.show_restaurants = not st.session_state.show_restaurants
            st.rerun()

    # زر تسجيل الخروج
    if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
        log_activity(st.session_state.username, "تسجيل خروج", "تم تسجيل الخروج")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <p style='text-align: center; color: rgba(255,255,255,0.6); font-size: 12px;'>
            👨‍💻 المطور<br>
            📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>
    """, unsafe_allow_html=True)

# ============================================
# إدارة المطاعم (للمطور فقط)
# ============================================

if st.session_state.show_restaurants and is_dev:
    st.title("👥 إدارة المطاعم")

    restaurants = get_all_restaurants()
    if restaurants:
        df = pd.DataFrame(restaurants)
        st.dataframe(df, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 عدد المطاعم", len(restaurants))
        with col2:
            total_trans = 0
            for r in restaurants:
                trans = get_user_transactions(r['username'])
                total_trans += len(trans)
            st.metric("💰 إجمالي العمليات", total_trans)
        with col3:
            st.metric("📅 آخر تحديث", datetime.now().strftime("%H:%M"))

        # إضافة مطعم جديد
        with st.expander("➕ إضافة مطعم جديد", expanded=False):
            with st.form("add_restaurant_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("👤 اسم المستخدم")
                    new_password = st.text_input("🔑 كلمة المرور", type="password")
                with col2:
                    new_full_name = st.text_input("📛 الاسم الكامل")
                    new_restaurant_name = st.text_input("🏪 اسم المطعم")

                submit_rest = st.form_submit_button("💾 إضافة المطعم", use_container_width=True)

                if submit_rest:
                    if not new_username or not new_password:
                        st.warning("⚠️ يرجى إدخال جميع البيانات")
                    else:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                hashed_pw = hash_password(new_password)
                                cursor.execute("""
                                    INSERT INTO users (username, password, full_name, role, restaurant_name, is_active)
                                    VALUES (%s, %s, %s, 'user', %s, TRUE)
                                """, (new_username, hashed_pw, new_full_name, new_restaurant_name))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success(f"✅ تم إضافة المطعم {new_restaurant_name} بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ: {e}")
    else:
        st.info("📭 لا توجد مطاعم مسجلة")

    if st.button("🔙 العودة للوحة الرئيسية", use_container_width=True):
        st.session_state.show_restaurants = False
        st.rerun()
    st.stop()

# ============================================
# 1. لوحة التحكم (Dashboard)
# ============================================

if nav_option == "📊 لوحة التحكم":
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <h2 style='color: #1E3A8A; margin: 0;'>
                📊 لوحة التحكم {f" - {restaurant_name}" if not is_dev else ""}
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # جلب البيانات
    cash_total, bank_total, cash_count, bank_count = get_daily_totals(st.session_state.username)
    expenses_today = get_total_expenses_today(st.session_state.username)
    total_transactions = cash_count + bank_count
    total_amount = cash_total + bank_total
    net_profit = total_amount - expenses_today

    # بطاقات المعلومات
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>📊</div>
                <div class='metric-value'>{total_transactions}</div>
                <div class='metric-label'>عدد العمليات اليوم</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>💰</div>
                <div class='metric-value'>{total_amount:,.0f}</div>
                <div class='metric-label'>إجمالي المبيعات</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>💸</div>
                <div class='metric-value' style='color: #EF4444;'>{expenses_today:,.0f}</div>
                <div class='metric-label'>المصروفات اليوم</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>📈</div>
                <div class='metric-value' style='color: {"#10B981" if net_profit >= 0 else "#EF4444"};'>
                    {net_profit:,.0f}
                </div>
                <div class='metric-label'>صافي الربح</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # شريط تقدم اليوم
    target = 20  # الهدف اليومي
    progress = min((total_transactions / target) * 100, 100)
    st.markdown(f"""
        <div>
            <div style='display: flex; justify-content: space-between;'>
                <span>📊 تقدم اليوم</span>
                <span>{total_transactions} من {target} عمليات</span>
            </div>
            <div class='custom-progress'>
                <div class='custom-progress-bar' style='width: {progress}%;'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ملخص اليوم
    st.subheader("📈 ملخص اليوم")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("💵 الكاش المفتوح", f"{cash_total:,.0f} جنيه", f"{cash_count} عملية")
    with col_b:
        st.metric("🏦 بنكك المفتوح", f"{bank_total:,.0f} جنيه", f"{bank_count} عملية")
    with col_c:
        st.metric("💸 المصروفات اليوم", f"{expenses_today:,.0f} جنيه")

    # إذا كان مطوراً، يعرض إحصائيات إضافية
    if is_dev:
        st.markdown("---")
        st.subheader("📊 إحصائيات المطاعم")

        restaurants = get_all_restaurants()
        if restaurants:
            data = []
            for r in restaurants:
                trans = get_user_transactions(r['username'])
                exp = get_user_expenses(r['username'])
                total_sales = sum(t['amount'] for t in trans if t.get('status') == 'open')
                total_exp = sum(e['amount'] for e in exp if e.get('closing_batch') is None)
                data.append({
                    'المطعم': r['restaurant_name'],
                    'المبيعات': total_sales,
                    'المصروفات': total_exp,
                    'صافي الربح': total_sales - total_exp
                })

            df = pd.DataFrame(data)
            if not df.empty:
                st.dataframe(df, use_container_width=True)

                # رسم بياني للمطاعم
                fig = px.bar(df, x='المطعم', y=['المبيعات', 'المصروفات'],
                             title='مقارنة المطاعم',
                             barmode='group',
                             color_discrete_sequence=['#10B981', '#EF4444'])
                st.plotly_chart(fig, use_container_width=True)

# ============================================
# 2. المصروفات
# ============================================

elif nav_option == "💰 المصروفات":
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <h2 style='color: #1E3A8A; margin: 0;'>
                💰 المصروفات {f" - {restaurant_name}" if not is_dev else ""}
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # إضافة مصروف جديد
    with st.container():
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        with st.expander("➕ إضافة مصروف جديد", expanded=True):
            with st.form("expense_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    description = st.text_input("📝 وصف المصروف", placeholder="مثال: فاتورة كهرباء")
                with col2:
                    amount = st.number_input("💵 المبلغ", min_value=1, step=1, format="%d")

                col3, col4 = st.columns(2)
                with col3:
                    category = st.selectbox("📂 الفئة", get_expense_categories())
                with col4:
                    expense_date = st.date_input("📅 التاريخ", value=date.today())

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
                                query = """
                                    INSERT INTO expenses (description, amount, category, expense_date, username, restaurant_name) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(query, (description.strip(), amount, category, expense_date,
                                                       st.session_state.username, restaurant_name))
                                conn.commit()
                                log_activity(st.session_state.username, "إضافة مصروف",
                                             f"الوصف: {description}, المبلغ: {amount}, الفئة: {category}")
                                cursor.close()
                                conn.close()
                                st.success(f"✅ تم إضافة المصروف بنجاح! ({amount:,.0f} جنيه)")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # عرض المصروفات
    expenses = get_today_expenses(st.session_state.username)
    total_expenses = get_total_expenses_today(st.session_state.username)

    if expenses:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 عدد المصروفات", len(expenses))
        with col2:
            st.metric("💰 إجمالي المصروفات", f"{total_expenses:,.0f} جنيه")
        with col3:
            avg_expense = total_expenses / len(expenses) if expenses else 0
            st.metric("📊 متوسط المصروف", f"{avg_expense:,.0f} جنيه")

        st.markdown("---")

        df = pd.DataFrame(expenses)
        df_display = df[['description', 'amount', 'category', 'username', 'restaurant_name', 'created_at']]