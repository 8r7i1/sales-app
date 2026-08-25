

Pasted text.txt
Document

نعم، الآن اتضح الجزء الناقص. الخطأ هنا هو أن السطر الأخير غير مكتمل:

color_discrete_sequence=['#10B981', '#3B82F6
ناقصه إغلاق ' ثم ] ثم ).

والجزء الصحيح كاملًا هو:

transactions = get_user_transactions(st.session_state.username)
open_transactions = [t for t in transactions if t.get('status') == 'open']

if open_transactions:
    df = pd.DataFrame(open_transactions)

    df_display = df[
        ['id', 'amount', 'payment_type', 'transaction_ref', 'created_at']
    ]

    df_display.columns = [
        'رقم العملية',
        'المبلغ',
        'طريقة الدفع',
        'المرجع',
        'التاريخ'
    ]

    st.dataframe(df_display, use_container_width=True)

    # إجمالي حسب طريقة الدفع
    st.subheader("📊 توزيع الإيرادات حسب طريقة الدفع")

    payment_totals = (
        df.groupby('payment_type')['amount']
        .sum()
        .reset_index()
    )

    payment_totals.columns = ['طريقة الدفع', 'المبلغ']

    st.dataframe(payment_totals, use_container_width=True)

    # رسم بياني
    if not payment_totals.empty:
        fig = px.pie(
            payment_totals,
            values='المبلغ',
            names='طريقة الدفع',
            title='توزيع الإيرادات',
            color_discrete_sequence=['#10B981', '#3B82F6']
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
ملاحظة مهمة
أنا أنصحك باستخدام هذه النسخة بدل مجرد إضافة الأقواس؛ لأنني أضفت أيضًا:

fig.update_traces(
    textposition='inside',
    textinfo='percent+label'
)
بحيث يظهر داخل الرسم اسم طريقة الدفع + النسبة المئوية.

وهذا الجزء مرتبط مباشرة بالكود السابق في ملفك؛ حيث كنت بالفعل تستخدم px.pie لعرض توزيع الإيرادات.


إذن الخطأ النحوي الأساسي تم حله.
إذا أردت، أستطيع الآن مراجعة الكود الـ850 سطر كاملًا سطرًا بسطر واستخراج جميع الأخطاء، وليس فقط هذا الخطأ، ثم أعطيك النسخة المصححة.


اعطيني الكود كامل محسن جاهز للطباعه

تمام. جهزت لك نسخة كاملة ومحسّنة من النظام بدل إصلاح السطر الأخير فقط.

أهم التحسينات التي أضفتها:

إصلاح الخطأ النحوي في px.pie.

استكمال الصفحات التي كانت ناقصة في الملف الأصلي.

إنشاء جداول users, transactions, expenses, expense_categories, وaudit_log تلقائيًا.

تسجيل الدخول والصلاحيات.

الإيرادات: كاش / بنكك + الرقم المرجعي.

المصروفات والتصنيفات.

لوحة تحكم وإحصائيات.

أرشيف الإيرادات والمصروفات مع البحث بالتاريخ.

إقفال اليومية برقم إقفال فريد.

حساب صافي الربح.

سجل للأنشطة.

تحسين معالجة أخطاء MySQL.

تحسين شكل الواجهة.

اختبرت صياغة Python للملف ولم يظهر خطأ SyntaxError.

📥 الكود الكامل الجاهز

مهم: الكود يعتمد على وجود إعدادات MySQL في Streamlit Secrets بهذا الشكل:

[mysql]
host = "localhost"
port = 3306
user = "root"
password = "كلمة_المرور"
database = "اسم_قاعدة_البيانات"
والكود نفسه سيقوم بإنشاء الجداول المطلوبة تلقائيًا عند تشغيله.


بيانات الدخول الافتراضية التي وضعتها في النسخة:

المطور: developer / dev123

كرولي: karoly / karoly123

Ghost Sweet: ghost / ghost123

أنصحك بتغيير كلمات المرور قبل استخدام النظام فعليًا.



File "/mount/src/sales-app/main.py", line 5
  راجعت الكود المرفق، وأول خطأ مؤكد يمنع البرنامج من التشغيل موجود في السطر 850.
                    ^
SyntaxError: invalid character '،' (U+060C)

صحيح، الخطأ واضح الآن. الملف الذي شغّلته يحتوي على نص شرحي عربي داخل ملف Python نفسه، ولذلك ظهر:

SyntaxError: invalid character '،' (U+060C)
وهذا خطئي في النسخة السابقة؛ النص:

راجعت الكود المرفق، وأول خطأ مؤكد...
لا يجب أن يكون داخل main.py.

قمت بفحص ملف Python نفسه، والنسخة الموجودة عندي الآن تمر من فحص Python بدون SyntaxError.

الحل
لا تنسخ النص السابق إلى main.py. استخدم ملف الكود فقط:


ثم في مشروع Streamlit:

احذف محتوى main.py القديم بالكامل.

ضع محتوى الملف الذي حملته مكانه.

احفظ الملف.

شغّل التطبيق مرة أخرى.

إذا ظهر لك بعد ذلك أي Error آخر، أرسله لي كما ظهر بالضبط، وسأصلحه لك؛ لأن الخطأ الحالي تحديدًا ليس من MySQL ولا من Streamlit، بل من دخول نص عربي خارج تعليق Python إلى الملف.


You're on the free plan
ChatGPT gets less accurate and may forget details in long conversations. Upgrade to chat longer with better memory.

Get Plus

New chat


Library
/
sales_system_app.py


import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import hashlib
import pandas as pd
import plotly.express as px
import uuid

# ============================================================
# نظام بيع - إدارة المبيعات والمصروفات والإقفال اليومي
# Developed by HASSAN ELNOUSH - 2026
# ============================================================

st.set_page_config(
    page_title="نظام بيع - المبيعات والمصروفات",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #dfe7f1 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #172554 0%, #111827 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .main-header {
        text-align: center;
        padding: 28px 20px;
        background: linear-gradient(135deg, #1e3a8a 0%, #4f46e5 100%);
        border-radius: 20px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 10px 35px rgba(30,58,138,.25);
    }

    .main-header h1 {
        font-size: 42px;
        font-weight: 800;
        margin: 0;
    }

    .main-header p {
        font-size: 17px;
        margin: 8px 0 0;
        opacity: .92;
    }

    .login-box {
        background: rgba(255,255,255,.96);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,.18);
        max-width: 470px;
        margin: 30px auto;
    }

    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,.08);
        text-align: center;
        min-height: 130px;
    }

    .metric-icon {
        font-size: 28px;
        margin-bottom: 7px;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 800;
        color: #1e3a8a;
    }

    .metric-label {
        color: #64748b;
        font-size: 14px;
        margin-top: 5px;
    }

    .revenue-card,
    .bank-card,
    .expense-card,
    .profit-card {
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,.12);
    }

    .revenue-card {
        background: linear-gradient(135deg, #059669, #10b981);
    }

    .bank-card {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    }

    .expense-card {
        background: linear-gradient(135deg, #dc2626, #ef4444);
    }

    .profit-card {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    }

    .section-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,.07);
        margin-bottom: 20px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 44px;
    }

    .small-note {
        color: #64748b;
        font-size: 13px;
    }

    @media (max-width: 700px) {
        .main-header h1 {
            font-size: 28px;
        }
        .metric-value {
            font-size: 21px;
        }
    }
    </style>
    """, unsafe_allow_html=True)


apply_custom_css()

# ============================================================
# إعدادات وقاعدة البيانات
# ============================================================

DEFAULT_CATEGORIES = [
    ("إيجار", "🏠"),
    ("رواتب", "👨‍💼"),
    ("كهرباء", "⚡"),
    ("ماء", "💧"),
    ("إنترنت", "🌐"),
    ("مواصلات", "🚗"),
    ("مشتريات", "🛒"),
    ("أخرى", "📌"),
]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_db_connection(show_error=True):
    try:
        mysql_cfg = st.secrets["mysql"]
        return mysql.connector.connect(
            host=mysql_cfg["host"],
            port=int(mysql_cfg.get("port", 3306)),
            user=mysql_cfg["user"],
            password=mysql_cfg["password"],
            database=mysql_cfg["database"],
            autocommit=False,
        )
    except Exception as exc:
        if show_error:
            st.error(f"❌ تعذر الاتصال بقاعدة البيانات: {exc}")
        return None


def close_db(conn, cursor=None):
    try:
        if cursor:
            cursor.close()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass


def execute_query(query, params=(), fetch=False, dictionary=False, commit=False):
    conn = get_db_connection()
    if not conn:
        return [] if fetch else False

    cursor = None
    try:
        cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(query, params)

        result = cursor.fetchall() if fetch else True

        if commit:
            conn.commit()

        return result
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        st.error(f"❌ خطأ في قاعدة البيانات: {exc}")
        return [] if fetch else False
    finally:
        close_db(conn, cursor)


# ============================================================
# إنشاء الجداول والبيانات الأساسية
# ============================================================

def ensure_database():
    conn = get_db_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(150) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                restaurant_name VARCHAR(150),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_active (username, is_active)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                amount DECIMAL(12,2) NOT NULL,
                payment_type VARCHAR(30) NOT NULL,
                transaction_ref VARCHAR(100),
                status VARCHAR(20) NOT NULL DEFAULT 'open',
                username VARCHAR(50) NOT NULL,
                restaurant_name VARCHAR(150),
                closing_batch VARCHAR(80),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_trans_user (username),
                INDEX idx_trans_status (status),
                INDEX idx_trans_date (created_at),
                INDEX idx_trans_batch (closing_batch)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                icon VARCHAR(10) DEFAULT '💰'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                expense_date DATE NOT NULL,
                closing_batch VARCHAR(80),
                username VARCHAR(50),
                restaurant_name VARCHAR(150),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_exp_date (expense_date),
                INDEX idx_exp_batch (closing_batch),
                INDEX idx_exp_user (username)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                action VARCHAR(100) NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_audit_user (username),
                INDEX idx_audit_time (timestamp)
            )
        """)

        for name, icon in DEFAULT_CATEGORIES:
            cursor.execute(
                "INSERT IGNORE INTO expense_categories (name, icon) VALUES (%s, %s)",
                (name, icon)
            )

        conn.commit()

        # إضافة مستخدمين افتراضيين فقط إذا لم يكونوا موجودين
        users = [
            ("developer", hash_password("dev123"), "المطور HASSAN ELNOUSH",
             "admin", "المطور", True),
            ("karoly", hash_password("karoly123"), "مطعم كرولي الصحافة",
             "user", "مطعم كرولي الصحافة", True),
            ("ghost", hash_password("ghost123"), "محل حلويات Ghost Sweet",
             "user", "محل حلويات Ghost Sweet", True),
        ]

        for username, password, full_name, role, restaurant, active in users:
            cursor.execute(
                """
                INSERT IGNORE INTO users
                (username, password, full_name, role, restaurant_name, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (username, password, full_name, role, restaurant, active)
            )

        conn.commit()
        return True

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        st.error(f"❌ فشل تجهيز قاعدة البيانات: {exc}")
        return False
    finally:
        close_db(conn, cursor)


# ============================================================
# المستخدمون والصلاحيات
# ============================================================

def authenticate_user(username, password):
    rows = execute_query(
        """
        SELECT id, username, full_name, role, restaurant_name, is_active
        FROM users
        WHERE username = %s
          AND password = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        (username.strip(), hash_password(password)),
        fetch=True,
        dictionary=True,
    )
    return rows[0] if rows else None


def get_user(username):
    rows = execute_query(
        """
        SELECT id, username, full_name, role, restaurant_name, is_active
        FROM users
        WHERE username = %s
        LIMIT 1
        """,
        (username,),
        fetch=True,
        dictionary=True,
    )
    return rows[0] if rows else None


def is_admin(username):
    user = get_user(username)
    return bool(user and user["role"] == "admin")


def log_activity(username, action, details=""):
    execute_query(
        """
        INSERT INTO audit_log (username, action, details)
        VALUES (%s, %s, %s)
        """,
        (username, action, details),
        commit=True,
    )


# ============================================================
# دوال الإيرادات
# ============================================================

def get_open_transactions(username):
    user = get_user(username)

    if user and user["role"] == "admin":
        query = """
            SELECT *
            FROM transactions
            WHERE status = 'open'
            ORDER BY created_at DESC
        """
        return execute_query(query, fetch=True, dictionary=True)

    query = """
        SELECT *
        FROM transactions
        WHERE status = 'open' AND username = %s
        ORDER BY created_at DESC
    """
    return execute_query(query, (username,), fetch=True, dictionary=True)


def get_today_transaction_totals(username):
    user = get_user(username)

    if user and user["role"] == "admin":
        query = """
            SELECT payment_type, COALESCE(SUM(amount),0) AS total,
                   COUNT(*) AS count
            FROM transactions
            WHERE status = 'open'
              AND DATE(created_at) = CURDATE()
            GROUP BY payment_type
        """
        rows = execute_query(query, fetch=True, dictionary=True)
    else:
        query = """
            SELECT payment_type, COALESCE(SUM(amount),0) AS total,
                   COUNT(*) AS count
            FROM transactions
            WHERE status = 'open'
              AND DATE(created_at) = CURDATE()
              AND username = %s
            GROUP BY payment_type
        """
        rows = execute_query(query, (username,), fetch=True, dictionary=True)

    cash_total = 0
    bank_total = 0
    cash_count = 0
    bank_count = 0

    for row in rows:
        if row["payment_type"] == "نقداً":
            cash_total = float(row["total"] or 0)
            cash_count = int(row["count"] or 0)
        elif row["payment_type"] == "بنكك":
            bank_total = float(row["total"] or 0)
            bank_count = int(row["count"] or 0)

    return cash_total, bank_total, cash_count, bank_count


def add_transaction(username, restaurant_name, amount, payment_type, ref):
    conn = get_db_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transactions
            (amount, payment_type, transaction_ref, status,
             username, restaurant_name)
            VALUES (%s, %s, %s, 'open', %s, %s)
            """,
            (amount, payment_type, ref, username, restaurant_name)
        )

        conn.commit()
        return True

    except Exception as exc:
        conn.rollback()
        st.error(f"❌ تعذر حفظ الإيراد: {exc}")
        return False
    finally:
        close_db(conn, cursor)


# ============================================================
# المصروفات
# ============================================================

def get_categories():
    rows = execute_query(
        "SELECT name FROM expense_categories ORDER BY name",
        fetch=True,
        dictionary=True,
    )
    return [row["name"] for row in rows] or [x[0] for x in DEFAULT_CATEGORIES]


def get_today_expenses(username):
    user = get_user(username)

    if user and user["role"] == "admin":
        query = """
            SELECT *
            FROM expenses
            WHERE expense_date = CURDATE()
              AND closing_batch IS NULL
            ORDER BY created_at DESC
        """
        return execute_query(query, fetch=True, dictionary=True)

    query = """
        SELECT *
        FROM expenses
        WHERE expense_date = CURDATE()
          AND closing_batch IS NULL
          AND username = %s
        ORDER BY created_at DESC
    """
    return execute_query(query, (username,), fetch=True, dictionary=True)


def get_today_expense_total(username):
    user = get_user(username)

    if user and user["role"] == "admin":
        query = """
            SELECT COALESCE(SUM(amount),0) AS total
            FROM expenses
            WHERE expense_date = CURDATE()
              AND closing_batch IS NULL
        """
        rows = execute_query(query, fetch=True, dictionary=True)
    else:
        query = """
            SELECT COALESCE(SUM(amount),0) AS total
            FROM expenses
            WHERE expense_date = CURDATE()
              AND closing_batch IS NULL
              AND username = %s
        """
        rows = execute_query(query, (username,), fetch=True, dictionary=True)

    return float(rows[0]["total"] or 0) if rows else 0


def add_expense(username, restaurant_name, description, amount, category):
    ok = execute_query(
        """
        INSERT INTO expenses
        (description, amount, category, expense_date,
         username, restaurant_name)
        VALUES (%s, %s, %s, CURDATE(), %s, %s)
        """,
        (description, amount, category, username, restaurant_name),
        commit=True,
    )
    return ok


# ============================================================
# الإقفال والأرشيف
# ============================================================

def create_closing(username, note=""):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = None
    batch = f"CLOSE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    try:
        cursor = conn.cursor(dictionary=True)

        # لا يسمح للمستخدم العادي بإقفال عمليات مستخدم آخر
        user = get_user(username)
        if user and user["role"] == "admin":
            cursor.execute("""
                SELECT
                    COALESCE(SUM(amount),0) AS total,
                    COUNT(*) AS count
                FROM transactions
                WHERE status = 'open'
                  AND DATE(created_at) = CURDATE()
            """)
            trans = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(amount),0) AS total, COUNT(*) AS count
                FROM expenses
                WHERE closing_batch IS NULL
                  AND expense_date = CURDATE()
            """)
            exp = cursor.fetchone()

            cursor.execute("""
                UPDATE transactions
                SET status = 'closed', closing_batch = %s
                WHERE status = 'open'
                  AND DATE(created_at) = CURDATE()
            """, (batch,))

            cursor.execute("""
                UPDATE expenses
                SET closing_batch = %s
                WHERE closing_batch IS NULL
                  AND expense_date = CURDATE()
            """, (batch,))
        else:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(amount),0) AS total,
                    COUNT(*) AS count
                FROM transactions
                WHERE status = 'open'
                  AND DATE(created_at) = CURDATE()
                  AND username = %s
            """, (username,))
            trans = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(amount),0) AS total, COUNT(*) AS count
                FROM expenses
                WHERE closing_batch IS NULL
                  AND expense_date = CURDATE()
                  AND username = %s
            """, (username,))
            exp = cursor.fetchone()

            cursor.execute("""
                UPDATE transactions
                SET status = 'closed', closing_batch = %s
                WHERE status = 'open'
                  AND DATE(created_at) = CURDATE()
                  AND username = %s
            """, (batch, username))

            cursor.execute("""
                UPDATE expenses
                SET closing_batch = %s
                WHERE closing_batch IS NULL
                  AND expense_date = CURDATE()
                  AND username = %s
            """, (batch, username))

        conn.commit()

        total_sales = float(trans["total"] or 0)
        total_expenses = float(exp["total"] or 0)

        return {
            "batch": batch,
            "sales": total_sales,
            "expenses": total_expenses,
            "profit": total_sales - total_expenses,
            "sales_count": int(trans["count"] or 0),
            "expense_count": int(exp["count"] or 0),
            "note": note,
        }

    except Exception as exc:
        conn.rollback()
        st.error(f"❌ فشل إقفال اليومية: {exc}")
        return None
    finally:
        close_db(conn, cursor)


def get_archive(username, start_date=None, end_date=None):
    user = get_user(username)
    params = []

    if user and user["role"] == "admin":
        query = """
            SELECT
                id,
                amount,
                payment_type,
                transaction_ref,
                status,
                username,
                restaurant_name,
                closing_batch,
                created_at,
                'إيراد' AS record_type
            FROM transactions
            WHERE 1=1
        """
    else:
        query = """
            SELECT
                id,
                amount,
                payment_type,
                transaction_ref,
                status,
                username,
                restaurant_name,
                closing_batch,
                created_at,
                'إيراد' AS record_type
            FROM transactions
            WHERE username = %s
        """
        params.append(username)

    if start_date:
        query += " AND DATE(created_at) >= %s"
        params.append(start_date)

    if end_date:
        query += " AND DATE(created_at) <= %s"
        params.append(end_date)

    query += " ORDER BY created_at DESC"

    return execute_query(query, tuple(params), fetch=True, dictionary=True)


def get_expense_archive(username, start_date=None, end_date=None):
    user = get_user(username)
    params = []

    if user and user["role"] == "admin":
        query = """
            SELECT
                id,
                description,
                amount,
                category,
                expense_date,
                closing_batch,
                username,
                restaurant_name,
                created_at
            FROM expenses
            WHERE 1=1
        """
    else:
        query = """
            SELECT
                id,
                description,
                amount,
                category,
                expense_date,
                closing_batch,
                username,
                restaurant_name,
                created_at
            FROM expenses
            WHERE username = %s
        """
        params.append(username)

    if start_date:
        query += " AND expense_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND expense_date <= %s"
        params.append(end_date)

    query += " ORDER BY created_at DESC"

    return execute_query(query, tuple(params), fetch=True, dictionary=True)


# ============================================================
# إدارة العملاء
# ============================================================

def get_all_restaurants():
    return execute_query(
        """
        SELECT id, username, full_name, role,
               restaurant_name, is_active, created_at
        FROM users
        WHERE role = 'user'
        ORDER BY restaurant_name
        """,
        fetch=True,
        dictionary=True,
    )


# ============================================================
# Session State
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.show_restaurants = False

# تجهيز قاعدة البيانات
if not ensure_database():
    st.stop()

# ============================================================
# تسجيل الدخول
# ============================================================

if not st.session_state.logged_in:

    st.markdown("""
    <div style="min-height:75vh; display:flex; align-items:center;
                justify-content:center;">
        <div style="width:100%; max-width:520px;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-box">
        <div style="text-align:center;">
            <div style="font-size:65px;">💰</div>
            <h1 style="color:#1e3a8a; margin-bottom:5px;">نظام بيع</h1>
            <p style="color:#64748b;">
                إدارة المبيعات والمصروفات والإيرادات
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username_input = st.text_input(
            "👤 اسم المستخدم",
            placeholder="أدخل اسم المستخدم",
        )
        password_input = st.text_input(
            "🔑 كلمة المرور",
            type="password",
            placeholder="أدخل كلمة المرور",
        )

        submit_login = st.form_submit_button(
            "🚪 دخول النظام",
            use_container_width=True,
            type="primary",
        )

        if submit_login:
            if not username_input.strip() or not password_input:
                st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور.")
            else:
                user = authenticate_user(username_input, password_input)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user["username"]
                    log_activity(
                        user["username"],
                        "تسجيل دخول",
                        "تم تسجيل الدخول بنجاح",
                    )
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")

    st.markdown("""
        <hr>
        <div style="text-align:center; color:#94a3b8; font-size:13px;">
            Developed by <b>HASSAN ELNOUSH</b> © 2026
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ============================================================
# بيانات المستخدم الحالي
# ============================================================

current_user = get_user(st.session_state.username)

if not current_user or not current_user["is_active"]:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.error("❌ الحساب غير متاح.")
    st.stop()

username = current_user["username"]
restaurant_name = current_user["restaurant_name"] or "—"
is_dev = current_user["role"] == "admin"

# ============================================================
# Header
# ============================================================

st.markdown(
    f"""
    <div class="main-header">
        <div style="font-size:42px;">{"👨‍💻" if is_dev else "💰"}</div>
        <h1>نظام بيع</h1>
        <p>إدارة المبيعات والمصروفات والإيرادات</p>
        <div style="margin-top:12px;">
            <span style="background:rgba(255,255,255,.18);
                         padding:7px 18px; border-radius:20px;">
                {"👨‍💻" + username + " - صلاحية كاملة"
                 if is_dev else "👨‍💼 " + username + " - " + restaurant_name}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding:12px 0 20px;">
            <div style="width:80px;height:80px;border-radius:50%;
                        background:linear-gradient(135deg,#667eea,#764ba2);
                        margin:auto;display:flex;align-items:center;
                        justify-content:center;font-size:35px;">
                {"👨‍💻" if is_dev else "💰"}
            </div>
            <h3>{username}</h3>
            <p style="font-size:13px;">
                {"المطور HASSAN ELNOUSH" if is_dev else restaurant_name}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_option = st.radio(
        "📋 القائمة الرئيسية",
        [
            "📊 لوحة التحكم",
            "💰 الإيرادات",
            "💸 المصروفات",
            "📅 أرشيف العمليات",
            "🔒 إقفال اليومية",
        ],
    )

    st.markdown("---")

    if is_dev:
        if st.button("👥 إدارة العملاء", use_container_width=True):
            st.session_state.show_restaurants = (
                not st.session_state.show_restaurants
            )
            st.rerun()

    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        log_activity(username, "تسجيل خروج", "تم تسجيل الخروج")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.show_restaurants = False
        st.rerun()

    st.markdown("---")
    st.caption(
        f"👨‍💻 HASSAN ELNOUSH\n\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

# ============================================================
# إدارة العملاء
# ============================================================

if st.session_state.show_restaurants and is_dev:
    st.title("👥 إدارة العملاء")

    restaurants = get_all_restaurants()

    if restaurants:
        df = pd.DataFrame(restaurants)
        df_display = df[
            [
                "id", "username", "full_name",
                "restaurant_name", "is_active", "created_at"
            ]
        ].copy()

        df_display.columns = [
            "ID", "اسم المستخدم", "الاسم",
            "المطعم", "نشط", "تاريخ الإنشاء"
        ]

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
        )

        st.metric("📊 عدد العملاء", len(restaurants))
    else:
        st.info("📭 لا يوجد عملاء.")

    if st.button("🔙 العودة للوحة الرئيسية", use_container_width=True):
        st.session_state.show_restaurants = False
        st.rerun()

    st.stop()

# ============================================================
# 1. لوحة التحكم
# ============================================================

if nav_option == "📊 لوحة التحكم":

    st.subheader(
        f"📊 لوحة التحكم {"- " + restaurant_name if not is_dev else ""}"
    )

    cash_total, bank_total, cash_count, bank_count = (
        get_today_transaction_totals(username)
    )

    expenses_today = get_today_expense_total(username)
    total_transactions = cash_count + bank_count
    total_amount = cash_total + bank_total
    net_profit = total_amount - expenses_today

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="revenue-card">
                <div style="font-size:28px;">💵</div>
                <div style="font-size:28px;font-weight:800;">
                    {cash_total:,.0f}
                </div>
                <div>إيرادات الكاش</div>
                <div style="opacity:.85;">{cash_count} عملية</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="bank-card">
                <div style="font-size:28px;">🏦</div>
                <div style="font-size:28px;font-weight:800;">
                    {bank_total:,.0f}
                </div>
                <div>إيرادات بنكك</div>
                <div style="opacity:.85;">{bank_count} عملية</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📈 ملخص اليوم")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-value">{total_transactions}</div>
                <div class="metric-label">عدد العمليات</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-value">{total_amount:,.0f}</div>
                <div class="metric-label">إجمالي الإيرادات</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">💸</div>
                <div class="metric-value" style="color:#dc2626;">
                    {expenses_today:,.0f}
                </div>
                <div class="metric-label">مصروفات اليوم</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        profit_color = "#059669" if net_profit >= 0 else "#dc2626"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-value" style="color:{profit_color};">
                    {net_profit:,.0f}
                </div>
                <div class="metric-label">صافي الربح</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    target = 20
    progress = min(total_transactions / target, 1.0)

    st.write(f"📊 **تقدم اليوم:** {total_transactions} من {target} عمليات")
    st.progress(progress)

    if total_transactions >= target:
        st.success("🎉 تم الوصول إلى الهدف اليومي.")

    if is_dev:
        st.markdown("---")
        st.subheader("📊 إحصائيات العملاء")

        restaurants = get_all_restaurants()
        data = []

        for restaurant in restaurants:
            trans = execute_query(
                """
                SELECT COALESCE(SUM(amount),0) AS total
                FROM transactions
                WHERE username = %s AND status = 'open'
                """,
                (restaurant["username"],),
                fetch=True,
                dictionary=True,
            )

            exp = execute_query(
                """
                SELECT COALESCE(SUM(amount),0) AS total
                FROM expenses
                WHERE username = %s AND closing_batch IS NULL
                """,
                (restaurant["username"],),
                fetch=True,
                dictionary=True,
            )

            sales = float(trans[0]["total"] or 0) if trans else 0
            expenses = float(exp[0]["total"] or 0) if exp else 0

            data.append({
                "العميل": restaurant["restaurant_name"],
                "الإيرادات": sales,
                "المصروفات": expenses,
                "صافي الربح": sales - expenses,
            })

        if data:
            df_clients = pd.DataFrame(data)
            st.dataframe(
                df_clients,
                use_container_width=True,
                hide_index=True,
            )

            fig = px.bar(
                df_clients,
                x="العميل",
                y=["الإيرادات", "المصروفات"],
                title="مقارنة العملاء",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 2. الإيرادات
# ============================================================

elif nav_option == "💰 الإيرادات":

    st.subheader("💰 الإيرادات")

    with st.expander("➕ إضافة إيراد جديد", expanded=True):

        with st.form("revenue_form", clear_on_submit=True):

            payment_type = st.selectbox(
                "💳 طريقة الدفع",
                ["نقداً", "بنكك"],
            )

            amount_mode = st.radio(
                "طريقة إدخال المبلغ",
                ["إدخال يدوي", "مضاعفات 500"],
                horizontal=True,
            )

            if amount_mode == "إدخال يدوي":
                amount = st.number_input(
                    "💵 المبلغ",
                    min_value=1.0,
                    step=500.0,
                    value=500.0,
                )
            else:
                multiplier = st.number_input(
                    "عدد مضاعفات 500",
                    min_value=1,
                    step=1,
                    value=1,
                )
                amount = multiplier * 500

                st.info(f"💰 المبلغ النهائي: {amount:,.0f} جنيه")

            transaction_ref = st.text_input(
                "🔢 رقم العملية المرجعي",
                placeholder="مطلوب فقط عند اختيار بنكك",
            )

            save_revenue = st.form_submit_button(
                "💾 حفظ الإيراد",
                use_container_width=True,
                type="primary",
            )

            if save_revenue:

                if amount <= 0:
                    st.warning("⚠️ يجب أن يكون المبلغ أكبر من صفر.")

                elif (
                    payment_type == "بنكك"
                    and not transaction_ref.strip()
                ):
                    st.warning("⚠️ رقم العملية المرجعي مطلوب لبنكك.")

                else:
                    ref = (
                        transaction_ref.strip()
                        if payment_type == "بنكك"
                        else None
                    )

                    if add_transaction(
                        username,
                        restaurant_name,
                        amount,
                        payment_type,
                        ref,
                    ):
                        log_activity(
                            username,
                            "إضافة إيراد",
                            f"{amount:,.0f} - {payment_type}",
                        )
                        st.success(
                            f"✅ تم حفظ الإيراد: {amount:,.0f} جنيه"
                        )
                        st.rerun()

    st.markdown("---")
    st.subheader("📊 إيرادات اليوم")

    cash_total, bank_total, cash_count, bank_count = (
        get_today_transaction_totals(username)
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "📊 عدد العمليات",
            cash_count + bank_count,
        )

    with c2:
        st.metric(
            "💰 إجمالي الإيرادات",
            f"{cash_total + bank_total:,.0f} جنيه",
        )

    with c3:
        st.metric(
            "💵 الكاش",
            f"{cash_total:,.0f} جنيه",
        )

    transactions = get_open_transactions(username)

    if transactions:
        df = pd.DataFrame(transactions)

        columns = [
            "id", "amount", "payment_type",
            "transaction_ref", "created_at"
        ]

        columns = [c for c in columns if c in df.columns]

        display_df = df[columns].copy()

        display_df.rename(
            columns={
                "id": "رقم العملية",
                "amount": "المبلغ",
                "payment_type": "طريقة الدفع",
                "transaction_ref": "المرجع",
                "created_at": "التاريخ",
            },
            inplace=True,
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        payment_totals = (
            df.groupby("payment_type", as_index=False)["amount"]
            .sum()
        )

        st.subheader("📊 توزيع الإيرادات حسب طريقة الدفع")

        chart_df = payment_totals.rename(
            columns={
                "payment_type": "طريقة الدفع",
                "amount": "المبلغ",
            }
        )

        st.dataframe(
            chart_df,
            use_container_width=True,
            hide_index=True,
        )

        if not payment_totals.empty:
            fig = px.pie(
                payment_totals,
                values="amount",
                names="payment_type",
                title="توزيع الإيرادات",
                hole=0.35,
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("📭 لا توجد عمليات إيراد مفتوحة حالياً.")

# ============================================================
# 3. المصروفات
# ============================================================

elif nav_option == "💸 المصروفات":

    st.subheader("💸 المصروفات")

    categories = get_categories()

    with st.expander("➕ إضافة مصروف جديد", expanded=True):

        with st.form("expense_form", clear_on_submit=True):

            description = st.text_input(
                "📝 وصف المصروف",
                placeholder="مثال: شراء مواد خام",
            )

            col1, col2 = st.columns(2)

            with col1:
                amount = st.number_input(
                    "💵 المبلغ",
                    min_value=1.0,
                    step=500.0,
                    value=500.0,
                )

            with col2:
                category = st.selectbox(
                    "📂 التصنيف",
                    categories,
                )

            save_expense = st.form_submit_button(
                "💾 حفظ المصروف",
                use_container_width=True,
                type="primary",
            )

            if save_expense:

                if not description.strip():
                    st.warning("⚠️ يرجى كتابة وصف المصروف.")

                elif amount <= 0:
                    st.warning("⚠️ يجب أن يكون المبلغ أكبر من صفر.")

                else:
                    if add_expense(
                        username,
                        restaurant_name,
                        description.strip(),
                        amount,
                        category,
                    ):
                        log_activity(
                            username,
                            "إضافة مصروف",
                            f"{amount:,.0f} - {category} - {description}",
                        )

                        st.success(
                            f"✅ تم حفظ المصروف: {amount:,.0f} جنيه"
                        )
                        st.rerun()

    st.markdown("---")

    expenses = get_today_expenses(username)
    total_expenses = sum(
        float(row["amount"] or 0)
        for row in expenses
    )

    st.metric(
        "💸 إجمالي مصروفات اليوم",
        f"{total_expenses:,.0f} جنيه",
    )

    if expenses:
        df_exp = pd.DataFrame(expenses)

        display_exp = df_exp[
            [
                "id",
                "description",
                "amount",
                "category",
                "expense_date",
                "created_at",
            ]
        ].copy()

        display_exp.columns = [
            "رقم",
            "الوصف",
            "المبلغ",
            "التصنيف",
            "التاريخ",
            "وقت الإدخال",
        ]

        st.dataframe(
            display_exp,
            use_container_width=True,
            hide_index=True,
        )

        category_totals = (
            df_exp.groupby("category", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )

        if not category_totals.empty:
            fig = px.bar(
                category_totals,
                x="category",
                y="amount",
                title="المصروفات حسب التصنيف",
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("📭 لا توجد مصروفات مفتوحة لليوم.")

# ============================================================
# 4. الأرشيف
# ============================================================

elif nav_option == "📅 أرشيف العمليات":

    st.subheader("📅 أرشيف العمليات")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "من تاريخ",
            value=date.today(),
        )

    with col2:
        end_date = st.date_input(
            "إلى تاريخ",
            value=date.today(),
        )

    if start_date > end_date:
        st.error("❌ تاريخ البداية يجب أن يكون قبل تاريخ النهاية.")
        st.stop()

    tab1, tab2 = st.tabs(["💰 الإيرادات", "💸 المصروفات"])

    with tab1:

        archive = get_archive(
            username,
            start_date,
            end_date,
        )

        if archive:
            df_archive = pd.DataFrame(archive)

            display = df_archive[
                [
                    "id",
                    "amount",
                    "payment_type",
                    "transaction_ref",
                    "status",
                    "restaurant_name",
                    "closing_batch",
                    "created_at",
                ]
            ].copy()

            display.columns = [
                "رقم",
                "المبلغ",
                "الدفع",
                "المرجع",
                "الحالة",
                "المطعم",
                "رقم الإقفال",
                "التاريخ",
            ]

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            total = df_archive["amount"].astype(float).sum()
            st.metric("💰 إجمالي الإيرادات في الفترة", f"{total:,.0f} جنيه")

        else:
            st.info("📭 لا توجد إيرادات في الفترة المحددة.")

    with tab2:

        expense_archive = get_expense_archive(
            username,
            start_date,
            end_date,
        )

        if expense_archive:
            df_exp_archive = pd.DataFrame(expense_archive)

            display = df_exp_archive[
                [
                    "id",
                    "description",
                    "amount",
                    "category",
                    "expense_date",
                    "restaurant_name",
                    "closing_batch",
                ]
            ].copy()

            display.columns = [
                "رقم",
                "الوصف",
                "المبلغ",
                "التصنيف",
                "التاريخ",
                "المطعم",
                "رقم الإقفال",
            ]

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            total = df_exp_archive["amount"].astype(float).sum()
            st.metric("💸 إجمالي المصروفات في الفترة", f"{total:,.0f} جنيه")

        else:
            st.info("📭 لا توجد مصروفات في الفترة المحددة.")

# ============================================================
# 5. إقفال اليومية
# ============================================================

elif nav_option == "🔒 إقفال اليومية":

    st.subheader("🔒 إقفال اليومية")

    cash_total, bank_total, cash_count, bank_count = (
        get_today_transaction_totals(username)
    )

    expenses_today = get_today_expense_total(username)

    total_sales = cash_total + bank_total
    net_profit = total_sales - expenses_today

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("💵 الكاش", f"{cash_total:,.0f}")

    with c2:
        st.metric("🏦 بنكك", f"{bank_total:,.0f}")

    with c3:
        st.metric("💸 المصروفات", f"{expenses_today:,.0f}")

    with c4:
        st.metric("📈 الصافي", f"{net_profit:,.0f}")

    st.markdown("---")

    st.warning(
        "⚠️ بعد إقفال اليومية ستنتقل عمليات اليوم إلى الأرشيف "
        "ولن تظهر ضمن العمليات المفتوحة."
    )

    note = st.text_area(
        "📝 ملاحظات الإقفال (اختياري)",
        placeholder="اكتب أي ملاحظات خاصة بإقفال اليوم...",
    )

    confirm = st.checkbox(
        "أؤكد أنني راجعت الإيرادات والمصروفات وأريد إقفال اليومية."
    )

    if st.button(
        "🔒 إقفال اليومية الآن",
        use_container_width=True,
        type="primary",
        disabled=not confirm,
    ):

        result = create_closing(username, note.strip())

        if result:
            log_activity(
                username,
                "إقفال اليومية",
                f"رقم الإقفال: {result['batch']} | "
                f"المبيعات: {result['sales']:,.0f} | "
                f"المصروفات: {result['expenses']:,.0f}",
            )

            st.success("✅ تم إقفال اليومية بنجاح.")

            st.info(
                f"""
                **رقم الإقفال:** `{result['batch']}`

                **الإيرادات:** {result['sales']:,.0f} جنيه

                **المصروفات:** {result['expenses']:,.0f} جنيه

                **صافي اليوم:** {result['profit']:,.0f} جنيه

                **عدد عمليات الإيراد:** {result['sales_count']}

                **عدد المصروفات:** {result['expense_count']}
                """
            )

            st.balloons()
            st.rerun()

# ============================================================
# نهاية التطبيق
# ============================================================
