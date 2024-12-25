import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import pyodbc

# MSSQL bağlantısı
connection = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=localhost;'
    'Database=AkilliEvDB;'
    'Trusted_Connection=yes;'
)
cursor = connection.cursor()

def fetch_users_and_rooms():
    """Kullanıcılar ve odalarını getirir."""
    query = '''
        SELECT k.Ad + ' ' + k.Soyad AS Kullanici, ISNULL(o.OdaAdi, 'Yok') AS Oda
        FROM Kullanıcılar k
        LEFT JOIN OdaErisim oe ON k.KullaniciID = oe.KullaniciID
        LEFT JOIN Odalar o ON oe.OdaID = o.OdaID
    '''
    cursor.execute(query)
    return cursor.fetchall()

def fetch_rooms():
    """Tüm odaları getirir."""
    cursor.execute("SELECT OdaAdi FROM Odalar")
    return [row[0] for row in cursor.fetchall()]

def add_user():
    """Yeni kullanıcı ekler."""
    ad = entry_ad.get()
    soyad = entry_soyad.get()
    email = entry_email.get()
    sifre = entry_sifre.get()
    if ad and soyad and email and sifre:
        try:
            query = "INSERT INTO Kullanıcılar (Ad, Soyad, Email, SifreHash) VALUES (?, ?, ?, HASHBYTES('SHA2_256', ?))"
            cursor.execute(query, ad, soyad, email, sifre)
            connection.commit()
            messagebox.showinfo("Başarılı", "Kullanıcı eklendi!")
            refresh_user_table()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Tüm alanları doldurun!")

def delete_user():
    """Seçili kullanıcıyı siler."""
    selected_item = user_table.selection()
    if selected_item:
        user = user_table.item(selected_item, 'values')[0]
        try:
            query = "DELETE FROM Kullanıcılar WHERE Ad + ' ' + Soyad = ?"
            cursor.execute(query, user)
            connection.commit()
            messagebox.showinfo("Başarılı", "Kullanıcı silindi!")
            refresh_user_table()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Silmek için bir kullanıcı seçin!")

def assign_room():
    """Seçili kullanıcıya oda atar."""
    selected_user = user_table.selection()
    selected_room = room_listbox.get(room_listbox.curselection())
    if selected_user and selected_room:
        user = user_table.item(selected_user, 'values')[0]
        try:
            # Kullanıcı ID ve Oda ID'yi al
            cursor.execute("SELECT KullaniciID FROM Kullanıcılar WHERE Ad + ' ' + Soyad = ?", user)
            kullanici_id = cursor.fetchone()[0]

            cursor.execute("SELECT OdaID FROM Odalar WHERE OdaAdi = ?", selected_room)
            oda_id = cursor.fetchone()[0]

            # Oda atamasını gerçekleştir
            query = "INSERT INTO OdaErisim (KullaniciID, OdaID) VALUES (?, ?)"
            cursor.execute(query, kullanici_id, oda_id)
            connection.commit()
            messagebox.showinfo("Başarılı", "Oda kullanıcıya atandı!")
            refresh_user_table()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Kullanıcı ve oda seçin!")

def add_room():
    """Yeni oda ekler."""
    oda_adi = entry_room_name.get()
    if oda_adi:
        try:
            query = "INSERT INTO Odalar (OdaAdi) VALUES (?)"
            cursor.execute(query, oda_adi)
            connection.commit()
            messagebox.showinfo("Başarılı", "Oda eklendi!")
            refresh_room_table()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Oda adı girin!")

def delete_room():
    """Seçili odayı siler."""
    selected_item = room_table.selection()
    if selected_item:
        room = room_table.item(selected_item, 'values')[0]
        try:
            query = "DELETE FROM Odalar WHERE OdaAdi = ?"
            cursor.execute(query, room)
            connection.commit()
            messagebox.showinfo("Başarılı", "Oda silindi!")
            refresh_room_table()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Silmek için bir oda seçin!")

def refresh_user_table():
    """Kullanıcı tablosunu yeniler."""
    for row in user_table.get_children():
        user_table.delete(row)
    for user, room in fetch_users_and_rooms():
        user_table.insert("", "end", values=(user, room))

def refresh_room_table():
    """Oda tablosunu yeniler."""
    for row in room_table.get_children():
        room_table.delete(row)
    for room in fetch_rooms():
        room_table.insert("", "end", values=(room,))


def fetch_devices_and_properties():
    """Cihazları ve özelliklerini getirir."""
    query = '''
        SELECT c.CihazAdi, ISNULL(co.DurumDeğeri, 'Yok') AS Ozellik
        FROM Cihazlar c
        LEFT JOIN CihazOzellikleri co ON c.CihazID = co.CihazID
    '''
    cursor.execute(query)
    return cursor.fetchall()


def fetch_controls():
    """Tüm kontrol seçeneklerini getirir, aynı şey iki defa yazdırılmaz."""
    cursor.execute("SELECT DISTINCT OzellikAdi FROM CihazOzellikleri")
    return [row[0] for row in cursor.fetchall()]


def add_device():
    """Yeni cihaz ekler."""
    cihaz_adi = entry_device_name.get()
    if cihaz_adi:
        try:
            query = "INSERT INTO Cihazlar (CihazAdi) VALUES (?)"
            cursor.execute(query, cihaz_adi)
            connection.commit()
            messagebox.showinfo("Başarılı", "Cihaz eklendi!")
            refresh_device_table()
            refresh_comboboxes()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Cihaz adı girin!")

def delete_device():
    """Seçili cihazı siler."""
    selected_item = device_table.selection()
    if selected_item:
        device = device_table.item(selected_item, 'values')[0]
        try:
            query = "DELETE FROM Cihazlar WHERE CihazAdi = ?"
            cursor.execute(query, device)
            connection.commit()
            messagebox.showinfo("Başarılı", "Cihaz silindi!")
            refresh_device_table()
            refresh_comboboxes()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Silmek için bir cihaz seçin!")

def assign_control():
    """Seçili cihaza kontrol atar (CihazOzellikleri tablosuna)."""
    selected_device = device_table.selection()
    selected_control = control_listbox.get(control_listbox.curselection())
    if selected_device and selected_control:
        device = device_table.item(selected_device, 'values')[0]
        try:
            # Cihaz ID'yi al
            cursor.execute("SELECT CihazID FROM Cihazlar WHERE CihazAdi = ?", device)
            cihaz_id = cursor.fetchone()[0]

            # Seçilen kontrolün adı, burada 'selected_control' özelliğin adı olabilir
            ozellik_adi = selected_control
            durum_degeri = "NULL"  # Burada varsayılan bir değer kullanabilirsiniz

            # Özellik atamasını gerçekleştir
            query = "INSERT INTO CihazOzellikleri (CihazID, OzellikAdi, DurumDeğeri) VALUES (?, ?, ?)"
            cursor.execute(query, cihaz_id, ozellik_adi, durum_degeri)
            connection.commit()
            messagebox.showinfo("Başarılı", "Kontrol cihaza atandı!")
            refresh_device_table()
            refresh_comboboxes()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    else:
        messagebox.showwarning("Uyarı", "Cihaz ve kontrol seçin!")


def refresh_device_table():
    """Cihaz tablosunu yeniler."""
    for row in device_table.get_children():
        device_table.delete(row)
    for device, property in fetch_devices_and_properties():
        device_table.insert("", "end", values=(device, property))

def fetch_device_features(device_id):
    """Belirli bir cihazın özelliklerini getirir."""
    query = """
        SELECT OzellikAdi, DurumDeğeri
        FROM CihazOzellikleri
        WHERE CihazID = ?
    """
    cursor.execute(query, (device_id,))
    return cursor.fetchall()

def update_device_feature(device_id, feature_name, new_value):
    """Cihaz özelliğini günceller."""
    query = """
        UPDATE CihazOzellikleri
        SET DurumDeğeri = ?
        WHERE CihazID = ? AND OzellikAdi = ?
    """
    cursor.execute(query, (new_value, device_id, feature_name))
    connection.commit()
    messagebox.showinfo("Başarılı", "Özellik güncellendi!")

def on_device_select(event):
    """Cihaz seçildiğinde özellikleri yükler."""
    selected_device = device_combobox.get()
    if selected_device:
        cursor.execute("SELECT CihazID FROM Cihazlar WHERE CihazAdi = ?", (selected_device,))
        device_id = cursor.fetchone()[0]
        features = fetch_device_features(device_id)

        # Combobox'ı güncelle
        feature_combobox['values'] = [feature[0] for feature in features]
        feature_combobox.set('')
        feature_value_entry.delete(0, tk.END)

def on_feature_select(event):
    """Özellik seçildiğinde değerini gösterir."""
    selected_device = device_combobox.get()
    selected_feature = feature_combobox.get()
    if selected_device and selected_feature:
        cursor.execute("SELECT CihazID FROM Cihazlar WHERE CihazAdi = ?", (selected_device,))
        device_id = cursor.fetchone()[0]
        cursor.execute(
            "SELECT DurumDeğeri FROM CihazOzellikleri WHERE CihazID = ? AND OzellikAdi = ?",
            (device_id, selected_feature)
        )
        feature_value = cursor.fetchone()
        if feature_value:
            feature_value_entry.delete(0, tk.END)
            feature_value_entry.insert(0, feature_value[0])

def set_feature_value():
    """Seçili özelliğin değerini ayarlar."""
    selected_device = device_combobox.get()
    selected_feature = feature_combobox.get()
    new_value = feature_value_entry.get()

    if selected_device and selected_feature and new_value:
        cursor.execute("SELECT CihazID FROM Cihazlar WHERE CihazAdi = ?", (selected_device,))
        device_id = cursor.fetchone()[0]
        update_device_feature(device_id, selected_feature, new_value)
        refresh_device_table()
        refresh_comboboxes()
        on_device_select(None)
    else:
        messagebox.showwarning("Uyarı", "Lütfen tüm seçimleri ve girişleri yapın!")


def refresh_comboboxes(selected_device=None):
    """Cihaz ve özellik comboboxlarını günceller."""
    cursor.execute("SELECT CihazAdi FROM Cihazlar")
    devices = [row[0] for row in cursor.fetchall()]
    device_combobox['values'] = devices

    # Eğer bir cihaz seçilmişse, özellik combobox'ını güncelle
    if selected_device:
        cursor.execute("""
            SELECT OzellikAdi
            FROM CihazOzellikleri
            INNER JOIN Cihazlar ON CihazOzellikleri.CihazID = Cihazlar.CihazID
            WHERE Cihazlar.CihazAdi = ?
        """, (selected_device,))
        features = [row[0] for row in cursor.fetchall()]
        feature_combobox['values'] = features
        feature_combobox.set('') # Özellik combobox'ını sıfırla
    else:
        feature_combobox['values'] = []
        feature_combobox.set('')

def load_kontrol_data(kontrol_table):
    """Kontroller tablosundaki verileri yükler."""
    kontrol_table.delete(*kontrol_table.get_children())
    # Örnek veri: Bu veriyi SQL sorgusuyla doldurabilirsiniz.
    data = [
        (1, 101, 201, "2024-12-25 12:00:00", "Açıldı"),
        (2, 102, 202, "2024-12-24 15:30:00", "Kapandı"),
    ]
    for row in data:
        kontrol_table.insert("", "end", values=row)

def clear_kontrol_table(kontrol_table):
    """Kontroller tablosundaki tüm verileri siler."""
    # Buraya SQL sorgusu ile tabloyu temizleyen kod eklenmeli
    print("Tüm geçmiş silindi.")
    kontrol_table.delete(*kontrol_table.get_children())


def load_distinct_features(ozellik_listbox):
    """Distinct özellik adlarını yükler."""
    # Örnek veri: Bu veriyi SQL sorgusuyla doldurabilirsiniz.
    features = ["WiFi", "Bluetooth", "GPS"]
    for feature in features:
        ozellik_listbox.insert("end", feature)


def load_device_list(device_select):
    """Cihazlar listesini yükler."""
    # Örnek veri: Bu veriyi SQL sorgusuyla doldurabilirsiniz.
    devices = ["Telefon", "Tablet", "Laptop"]
    device_select['values'] = devices

def add_kontrol(feature_name, device_name, ozellik_listbox):
    """Yeni kontrolü ekler."""
    # Buraya SQL sorgusu ile kontrol ekleme işlemi yapılmalı
    print(f"Eklendi: Özellik - {feature_name}, Cihaz - {device_name}")
    ozellik_listbox.insert("end", feature_name)


def setup_ui():
    """Arayüzü oluşturur."""
    global entry_ad, entry_soyad, entry_email, entry_sifre, user_table, room_listbox, room_table, entry_room_name,\
        entry_device_name, device_table, control_listbox, feature_combobox, feature_value_entry, device_combobox

    root = ctk.CTk()
    root.title("Akıllı Ev Yönetimi")

    tab_control = ttk.Notebook(root)

    ############### Kullanıcılar Sekmesi ###############
    tab_users = ctk.CTkFrame(tab_control)
    tab_control.add(tab_users, text="Kullanıcılar")

    # Kullanıcı Ekleme Alanı
    frame_add_user = ctk.CTkFrame(tab_users)
    frame_add_user.pack(pady=10)

    ctk.CTkLabel(frame_add_user, text="Ad:").grid(row=0, column=0, padx=5, pady=5)
    entry_ad = ctk.CTkEntry(frame_add_user)
    entry_ad.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_add_user, text="Soyad:").grid(row=1, column=0, padx=5, pady=5)
    entry_soyad = ctk.CTkEntry(frame_add_user)
    entry_soyad.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_add_user, text="Email:").grid(row=2, column=0, padx=5, pady=5)
    entry_email = ctk.CTkEntry(frame_add_user)
    entry_email.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_add_user, text="Şifre:").grid(row=3, column=0, padx=5, pady=5)
    entry_sifre = ctk.CTkEntry(frame_add_user, show="*")
    entry_sifre.grid(row=3, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_add_user, text="Kullanıcı Ekle", command=add_user).grid(row=4, column=0, columnspan=2, pady=10)

    # Kullanıcı Tablosu
    frame_table = ctk.CTkFrame(tab_users)
    frame_table.pack(pady=10)

    user_table = ttk.Treeview(frame_table, columns=("Kullanıcı", "Oda"), show="headings")
    user_table.heading("Kullanıcı", text="Kullanıcı")
    user_table.heading("Oda", text="Oda")
    user_table.pack()

    # Kullanıcı Silme
    ctk.CTkButton(tab_users, text="Kullanıcı Sil", command=delete_user).pack(pady=10)

    # Oda Atama
    frame_assign_room = ctk.CTkFrame(tab_users)
    frame_assign_room.pack(pady=10)

    ctk.CTkLabel(frame_assign_room, text="Odalar:").pack()
    room_listbox = tk.Listbox(frame_assign_room)
    room_listbox.pack()

    for room in fetch_rooms():
        room_listbox.insert("end", room)

    ctk.CTkButton(frame_assign_room, text="Oda Ata", command=assign_room).pack(pady=10)

    ############### Odalar Sekmesi ###############
    tab_rooms = ctk.CTkFrame(tab_control)
    tab_control.add(tab_rooms, text="Odalar")

    # Oda Tablosu
    frame_room_table = ctk.CTkFrame(tab_rooms)
    frame_room_table.pack(pady=10)

    room_table = ttk.Treeview(frame_room_table, columns=("Oda"), show="headings")
    room_table.heading("Oda", text="Oda")
    room_table.pack()

    # Oda Ekle/Sil Alanı
    frame_manage_room = ctk.CTkFrame(tab_rooms)
    frame_manage_room.pack(pady=10)

    ctk.CTkLabel(frame_manage_room, text="Oda Adı:").grid(row=0, column=0, padx=5, pady=5)
    entry_room_name = ctk.CTkEntry(frame_manage_room)
    entry_room_name.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_manage_room, text="Oda Ekle", command=add_room).grid(row=1, column=0, padx=5, pady=5)
    ctk.CTkButton(frame_manage_room, text="Oda Sil", command=delete_room).grid(row=1, column=1, padx=5, pady=5)

    #tab_control.pack(expand=1, fill="both")

    ############### Cihazlar Sekmesi ###############
    tab_devices = ctk.CTkFrame(tab_control)
    tab_control.add(tab_devices, text="Cihazlar")

    # Cihaz Tablosu
    frame_device_table = ctk.CTkFrame(tab_devices)
    frame_device_table.pack(pady=10)

    device_table = ttk.Treeview(frame_device_table, columns=("Cihaz", "Özellik"), show="headings")
    device_table.heading("Cihaz", text="Cihaz")
    device_table.heading("Özellik", text="Özellik")
    device_table.pack()

    # Cihaz Ekle/Sil Alanı
    frame_manage_device = ctk.CTkFrame(tab_devices)
    frame_manage_device.pack(pady=10)

    ctk.CTkLabel(frame_manage_device, text="Cihaz Adı:").grid(row=0, column=0, padx=5, pady=5)
    entry_device_name = ctk.CTkEntry(frame_manage_device)
    entry_device_name.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_manage_device, text="Cihaz Ekle", command=add_device).grid(row=1, column=0, padx=5, pady=5)
    ctk.CTkButton(frame_manage_device, text="Cihaz Sil", command=delete_device).grid(row=1, column=1, padx=5, pady=5)

    # Kontrol Atama
    frame_assign_control = tk.Frame(tab_devices)
    frame_assign_control.pack(pady=10)

    tk.Label(frame_assign_control, text="Kontroller:").pack()
    control_listbox = tk.Listbox(frame_assign_control)
    control_listbox.pack()

    for control in fetch_controls():
        control_listbox.insert("end", control)

    tk.Button(frame_assign_control, text="Kontrol Ata", command=assign_control).pack(pady=10)

    # Özellikleri Seçme ve Düzenleme Alanı
    frame_select_device = ctk.CTkFrame(tab_devices)
    frame_select_device.pack(pady=10)

    ctk.CTkLabel(frame_select_device, text="Cihazlar:").grid(row=0, column=0, padx=5, pady=5)
    device_combobox = ttk.Combobox(frame_select_device, state="readonly")
    device_combobox.grid(row=0, column=1, padx=5, pady=5)
    device_combobox.bind("<<ComboboxSelected>>", on_device_select)

    # Özellikleri Seçme ve Düzenleme Alanı
    frame_edit_features = ctk.CTkFrame(tab_devices)
    frame_edit_features.pack(pady=10)

    ctk.CTkLabel(frame_edit_features, text="Özellikler:").grid(row=0, column=0, padx=5, pady=5)
    feature_combobox = ttk.Combobox(frame_edit_features, state="readonly")
    feature_combobox.grid(row=0, column=1, padx=5, pady=5)
    feature_combobox.bind("<<ComboboxSelected>>", on_feature_select)

    ctk.CTkLabel(frame_edit_features, text="Değer:").grid(row=1, column=0, padx=5, pady=5)
    feature_value_entry = ctk.CTkEntry(frame_edit_features)
    feature_value_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_edit_features, text="Set", command=set_feature_value).grid(row=2, column=0, columnspan=2,
                                                                                   pady=10)

    ############### Kontroller Sekmesi ###############

    # Sekme oluşturma
    tab_kontroller = ctk.CTkFrame(tab_control)
    tab_control.add(tab_kontroller, text="Kontroller")

    # Kontroller Tablosu
    frame_kontrol_table = ctk.CTkFrame(tab_kontroller)
    frame_kontrol_table.pack(pady=10)

    kontrol_table = ttk.Treeview(frame_kontrol_table,
                                 columns=("KontrolID", "KullaniciID", "CihazID", "KontrolTarihi", "YapilanIslem"),
                                 show="headings")
    kontrol_table.heading("KontrolID", text="Kontrol ID")
    kontrol_table.heading("KullaniciID", text="Kullanıcı ID")
    kontrol_table.heading("CihazID", text="Cihaz ID")
    kontrol_table.heading("KontrolTarihi", text="Kontrol Tarihi")
    kontrol_table.heading("YapilanIslem", text="Yapılan İşlem")
    kontrol_table.pack()

    # Geçmişi Sil Butonu
    ctk.CTkButton(tab_kontroller, text="Geçmişi Sil", command=lambda: clear_kontrol_table(kontrol_table)).pack(pady=10)

    # Cihaz Özellikleri Listesi
    frame_cihaz_ozellikleri = ctk.CTkFrame(tab_kontroller)
    frame_cihaz_ozellikleri.pack(pady=10)

    ctk.CTkLabel(frame_cihaz_ozellikleri, text="Cihaz Özellikleri:").pack()
    ozellik_listbox = tk.Listbox(frame_cihaz_ozellikleri, height=5)
    ozellik_listbox.pack()

    # Özellik Ekleme Alanı
    frame_add_feature = ctk.CTkFrame(tab_kontroller)
    frame_add_feature.pack(pady=10)

    ctk.CTkLabel(frame_add_feature, text="Yeni Özellik:").grid(row=0, column=0, padx=5, pady=5)
    entry_new_feature = ctk.CTkEntry(frame_add_feature)
    entry_new_feature.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_add_feature, text="Cihaz Seç:").grid(row=1, column=0, padx=5, pady=5)
    device_select = ttk.Combobox(frame_add_feature)
    device_select.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_add_feature, text="Kontrol Ekle",
                  command=lambda: add_kontrol(entry_new_feature.get(), device_select.get(), ozellik_listbox)).grid(
        row=2, column=0, columnspan=2, pady=10)

    # Verilerin yüklenmesi için fonksiyonları çağır
    load_kontrol_data(kontrol_table)
    load_distinct_features(ozellik_listbox)
    load_device_list(device_select)

    tab_control.pack(expand=1, fill="both")

    refresh_user_table()
    refresh_room_table()
    refresh_device_table()
    refresh_comboboxes()
    root.mainloop()

setup_ui()
