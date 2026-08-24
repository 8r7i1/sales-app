# ----------------- 2. شاشة أرشيف العمليات المقفلة -----------------
elif nav_option == "أرشيف العمليات":
st.title("📅 أرشيف الإقفالات والعمليات السابقة")
st.info("هنا يتم عرض العمليات التي تم إقفالها مقسمة ومنظمة حسب مجموعات الإقفال.")

conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    # جلب العمليات المقفلة فقط مرتبطة بـ closing_batch
    cursor.execute(
        "SELECT id, amount, payment_type, transaction_ref, closing_batch, created_at FROM transactions WHERE status = 'closed' ORDER BY created_at DESC")
    archive_data = cursor.fetchall()

    if archive_data:
        st.dataframe(archive_data, use_container_width=True)

        st.markdown("---")
        # زر تصفير وحذف الأرشيف المقفل تماماً
        if st.button("🗑️ تصفير الأرشيف المقفل نهائياً", type="secondary"):
            confirm_cursor = conn.cursor()
            confirm_cursor.execute("DELETE FROM transactions WHERE status = 'closed'")
            conn.commit()
            confirm_cursor.close()
            st.success("تم تصفير الأرشيف وحذف كافة العمليات المقفلة بنجاح!")
            st.rerun()
    else:
        st.info("لا توجد عمليات مقفلة في الأرشيف حتى الآن.")

    cursor.close()
    conn.close()