import streamlit as st
import mysql.connector
from datetime import datetime
import hashlib
import pandas as pd
import time
from io import StringIO

# إعدادات صفحة Streamlit لتصميم أنيق وواضح
st.set_page_config(
    page_title="نظام المبيعات - حسن",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ===================== دوال المساعدة =====================

# دالة لتشفير كلمة المرور
def hash_password(password):
    """تشفير كلمة المرور باستخدام SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


# دالة الاتصال بقاعدة البيانات مع إعادة المحاولة
def get_db_connection(max_retries=3):
    """الاتصال بقاعدة البيانات مع إعادة المحاولة في حالة الفشل"""
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
                st.error(f"❌ فشل الاتصال بقاعدة البيانات بعد {max_retries} محاولات: {e}")
                return None
            time.sleep(1)  # انتظر ثانية قبل المحاولة مجدداً
    return None


# دالة تسجيل سجل العمليات (Audit Log)
def log_activity(username, action, details=""):
    """تسجيل نشاط المستخدم في سجل التدقيق"""
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
            st.warning(f"⚠️ تعذر تسجيل النشاط: {e}")
            return False
    return False


# دالة التحقق من تسجيل الدخول (مع تشفير كلمة المرور)
def authenticate_user(username, password):
    """التحقق من صحة بيانات تسجيل الدخول مع تشفير كلمة المرور"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # استخدام كلمة المرور المشفرة
            hashed_pw = hash_password(password)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username.strip(), hashed_pw))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            st.error(f"خطأ في التحقق من المستخدم: {e}")
            return None
    return None


# دالة الحصول على مجاميع اليوم المفتوحة
def get_daily_totals():
    """الحصول على مجاميع العمليات المفتوحة اليوم"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT payment_type, SUM(amount) as total, COUNT(*) as count \
                 FROM transactions WHERE status = 'open' GROUP BY payment_type"
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
            st.error(f"خطأ في جلب المجاميع: {e}")
            return 0, 0, 0, 0
    return 0, 0, 0, 0


# ===================== حالة الجلسة =====================

# تهيئة حالة تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page_num = 0  # للتصفح في الأرشيف

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
        "<p style='text-align: center; color: gray; font-size: 14px;'>"
        "Developed by <b>HASSAN ELNOUSH</b> © 2026"
        "</p>",
        unsafe_allow_html=True
    )

# ===================== الواجهة الرئيسية (بعد تسجيل الدخول) =====================

else:
    # ----------------- الشريط الجانبي (Sidebar) -----------------
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
        "<p style='text-align: center; color: gray; font-size: 12px;'>"
        "👨‍💻 Developer: <b>HASSAN ELNOUSH</b><br>"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        "</p>",
        unsafe_allow_html=True
    )

    # ==================== 1. شاشة تسجيل مبيعات =====================

    if nav_option == "📊 تسجيل مبيعات":
        st.title("📊 لوحة تحكم نظام المبيعات")

        # إحصائيات سريعة
        cash_total, bank_total, cash_count, bank_count = get_daily_totals()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="📊 عدد العمليات اليوم",
                value=total_transactions,
                delta="عمليات مفتوحة"
            )
        with col2:
            st.metric(
                label="💰 إجمالي المبيعات",
                value=f"{total_amount:,.0f} جنيه",
                delta="اليومية"
            )
        with col3:
            st.metric(
                label="⏱️ آخر تحديث",
                value=datetime.now().strftime("%H:%M"),
                delta="الآن"
            )

        st.markdown("---")

        # نموذج إضافة مبيعات
        with st.form("sales_form", clear_on_submit=True):
            st.subheader("➕ إضافة عملية بيع جديدة")

            col_form1, col_form2 = st.columns(2)
            with col_form1:
                amount = st.number_input(
                    "💵 مبلغ العملية:",
                    min_value=1,
                    step=1,
                    format="%d",
                    help="أدخل المبلغ بالأرقام الصحيحة فقط"
                )
            with col_form2:
                payment_type = st.selectbox(
                    "💳 طريقة الدفع:",
                    ["نقداً", "بنكك"],
                    help="اختر طريقة الدفع المناسبة"
                )

            transaction_ref = st.text_input(
                "🔢 رقم العملية المرجعي:",
                placeholder="مطلوب فقط للدفع عبر بنكك",
                help="أدخل رقم التحويل أو المرجع في حالة الدفع عبر بنكك"
            )

            submit_sale = st.form_submit_button("💾 حفظ العملية", use_container_width=True, type="primary")

        if submit_sale:
            # التحقق من صحة البيانات
            if amount <= 0:
                st.warning("⚠️ يرجى إدخال مبلغ أكبر من الصفر!")
            elif payment_type == "بنكك" and not transaction_ref.strip():
                st.warning("⚠️ يرجى إدخال رقم العملية المرجعي للدفع عبر بنكك!")
            elif payment_type == "بنكك" and len(transaction_ref.strip()) > 50:
                st.error("❌ رقم العملية المرجعي طويل جداً (حد أقصى 50 حرف)!")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        ref_val = transaction_ref.strip() if payment_type == "بنكك" else None
                        query = "INSERT INTO transactions (amount, payment_type, transaction_ref, status) VALUES (%s, %s, %s, 'open')"
                        cursor.execute(query, (amount, payment_type, ref_val))
                        conn.commit()

                        # تسجيل النشاط
                        log_activity(
                            st.session_state.username,
                            "إضافة مبيعات",
                            f"المبلغ: {amount}, الطريقة: {payment_type}"
                        )

                        cursor.close()
                        conn.close()
                        st.success(f"✅ تم تسجيل عملية المبيعات بنجاح! (المبلغ: {amount:,} جنيه)")
                        st.balloons()  # تأثير احتفالي
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء حفظ العملية: {e}")

        st.markdown("---")
        st.subheader("📈 ملخص المجاميع المفتوحة (اليومية الحالية)")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(
                label="💵 إجمالي الكاش المفتوح",
                value=f"{cash_total:,.0f} جنيه",
                delta=f"{cash_count} عملية"
            )
        with col_b:
            st.metric(
                label="🏦 إجمالي بنكك المفتوح",
                value=f"{bank_total:,.0f} جنيه",
                delta=f"{bank_count} عملية"
            )

    # ==================== 2. شاشة أرشيف العمليات المقفلة =====================

    elif nav_option == "📅 أرشيف العمليات":
        st.title("📅 أرشيف الإقفالات والعمليات السابقة")
        st.info("ℹ️ هنا يتم عرض العمليات التي تم إقفالها مقسمة ومنظمة حسب مجموعات الإقفال.")

        # خيارات التصفية
        with st.expander("🔍 خيارات التصفية والبحث", expanded=False):
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                date_from = st.date_input("📅 من تاريخ", value=None)
            with col_filter2:
                date_to = st.date_input("📅 إلى تاريخ", value=None)
            with col_filter3:
                payment_filter = st.selectbox(
                    "💳 طريقة الدفع",
                    ["الكل", "نقداً", "بنكك"]
                )

            if st.button("🔄 تطبيق التصفية", use_container_width=True):
                st.session_state.page_num = 0
                st.rerun()

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                page_size = 20
                offset = st.session_state.page_num * page_size

                # بناء الاستعلام مع التصفية
                query = "SELECT id, amount, payment_type, transaction_ref, closing_batch, created_at FROM transactions WHERE status = 'closed'"
                count_query = "SELECT COUNT(*) as total FROM transactions WHERE status = 'closed'"
                params = []

                if date_from:
                    query += " AND DATE(created_at) >= %s"
                    count_query += " AND DATE(created_at) >= %s"
                    params.append(date_from)
                if date_to:
                    query += " AND DATE(created_at) <= %s"
                    count_query += " AND DATE(created_at) <= %s"
                    params.append(date_to)
                if payment_filter != "الكل":
                    query += " AND payment_type = %s"
                    count_query += " AND payment_type = %s"
                    params.append(payment_filter)

                # جلب العدد الكلي
                cursor.execute(count_query, params)
                total_records = cursor.fetchone()['total']
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1

                # جلب الصفحة الحالية
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([page_size, offset])
                cursor.execute(query, params)
                archive_data = cursor.fetchall()

                if archive_data:
                    # عرض البيانات في جدول
                    st.dataframe(archive_data, use_container_width=True)

                    # أزرار التنقل بين الصفحات
                    col_pagi1, col_pagi2, col_pagi3 = st.columns([1, 2, 1])
                    with col_pagi1:
                        if st.button("⬅️ السابق", disabled=(st.session_state.page_num == 0)):
                            st.session_state.page_num -= 1
                            st.rerun()
                    with col_pagi2:
                        st.write(
                            f"📄 صفحة {st.session_state.page_num + 1} من {total_pages} (إجمالي {total_records} عملية)")
                    with col_pagi3:
                        if st.button("التالي ➡️", disabled=(st.session_state.page_num >= total_pages - 1)):
                            st.session_state.page_num += 1
                            st.rerun()

                    # زر تصدير البيانات
                    if st.button("📥 تصدير الأرشيف إلى CSV", use_container_width=True):
                        df = pd.DataFrame(archive_data)
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📂 تحميل ملف CSV",
                            data=csv,
                            file_name=f"archive_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.info("📭 لا توجد عمليات مقفلة في الأرشيف تطابق المعايير.")

                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"❌ خطأ في تحميل الأرشيف: {e}")

    # ==================== 3. شاشة إقفال اليومية =====================

    elif nav_option == "🔒 إقفال اليومية":
        st.title("🔒 إقفال اليومية")

        # عرض إحصائيات قبل الإقفال
        cash_total, bank_total, cash_count, bank_count = get_daily_totals()
        total_transactions = cash_count + bank_count
        total_amount = cash_total + bank_total

        st.warning(
            f"⚠️ **تنبيه:** سوف يتم إقفال {total_transactions} عملية بمبلغ إجمالي {total_amount:,.0f} جنيه.\n\n"
            "عند الضغط على إقفال اليومية، سيتم نقل كافة العمليات المفتوحة إلى الأرشيف وإعطاؤها رقم إقفال خاص."
        )

        col_warn1, col_warn2 = st.columns(2)
        with col_warn1:
            st.metric("📊 عدد العمليات المفتوحة", total_transactions)
        with col_warn2:
            st.metric("💰 إجمالي المبلغ", f"{total_amount:,.0f} جنيه")

        # حقل تأكيد الإقفال
        confirm_text = st.text_input(
            "✍️ اكتب 'إقفال' لتأكيد العملية:",
            placeholder="اكتب إقفال هنا",
            help="لتأكيد الإقفال، يجب كتابة كلمة 'إقفال' بالضبط"
        )

        if st.button("🔒 تأكيد إقفال اليومية", type="primary", use_container_width=True,
                     disabled=(confirm_text != "إقفال")):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    # توليد معرف إقفال فريد
                    batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                    # تحديث العمليات المفتوحة إلى مقفلة
                    query = "UPDATE transactions SET status = 'closed', closing_batch = %s WHERE status = 'open'"
                    cursor.execute(query, (batch_id,))
                    affected_rows = cursor.rowcount
                    conn.commit()

                    # تسجيل النشاط
                    log_activity(
                        st.session_state.username,
                        "إقفال يومية",
                        f"رقم الإقفال: {batch_id}, عدد العمليات: {affected_rows}"
                    )

                    cursor.close()
                    conn.close()

                    st.success(f"✅ تم إقفال اليومية بنجاح!")
                    st.info(f"📋 رقم الإقفال: **{batch_id}**")
                    st.info(f"📊 عدد العمليات المقفلة: **{affected_rows}**")
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء إقفال اليومية: {e}")

# ===================== نهاية الملف =====================