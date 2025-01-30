import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

proje = tk.Tk()
proje.title("FİNANS UYGULAMASI")
proje.geometry("720x520+400+100")
proje.configure(bg="#c5cfde")
proje.resizable(False, False)


balance = 0
# file_name = "finans_deneme.csv"
file_name = "finans_ilk_deneme.csv"

# VERİLERİ KAYDETME
def save_to_csv():
    data = []
    for item in transaction_table.get_children():
        item_values = transaction_table.item(item)["values"]
        data.append(item_values)

    df = pd.DataFrame(data, columns=["TÜR", "AÇIKLAMA", "MİKTAR", "TARİH"])
    df.to_csv(file_name, index=False)


# VERİLERİ YÜKLEME
def load_csv():
    try:
        df = pd.read_csv(file_name)
        df = df.sort_values(by="TARİH", ascending=False)
        for index, row in df.iterrows():
            transaction_table.insert("", tk.END, values=(row["TÜR"],row["AÇIKLAMA"], row["MİKTAR"], row["TARİH"]))
        balance_update()
    except FileNotFoundError:
        pass    


# BAKİYE FONKSİYONU
def balance_update():
    global balance
    total_income = 0
    total_expense = 0

    for item in transaction_table.get_children():
        item_values = transaction_table.item(item)["values"]
        if item_values[0] == "GELEN":
            total_income += item_values[2]
        elif item_values[0] == "GİDEN":
            total_expense += item_values[2]

    balance = total_income - total_expense      
    balance_label.config(text=f"{balance} TL")


# EKLE BUTONU FONKSİYONU
def add_entry():
    global balance
    income_amount = income_entry.get()
    expense_amount = expense_entry.get()

    current_date = datetime.now().strftime("%Y.%m.%d")

    if income_entry.get() and income_type_entry.get():
        if not income_amount.isnumeric():
            messagebox.showwarning("Hata", "Gelen para miktarı sayısal olmalıdır!")
            return

        transaction_table.insert("", tk.END, values=("GELEN", income_type_entry.get(), income_amount, current_date))
        balance_update()
        save_to_csv()
        income_entry.delete(0, tk.END)
        income_type_entry.delete(0, tk.END)

    elif expense_entry.get() and expense_type_entry.get():
        if not expense_amount.isnumeric():
            messagebox.showwarning("Hata", "Giden para miktarı sayısal olmalıdır!")
            return
        
        transaction_table.insert("", tk.END, values=("GİDEN", expense_type_entry.get(), expense_amount, current_date))
        balance_update()
        save_to_csv()
        expense_entry.delete(0, tk.END)
        expense_type_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Eksik girdi", "Lütfen tüm alanları doldurun!")      


# SİL BUTONU FONKSİYONU
def delete_entry():
    selected_item = transaction_table.selection()
    if selected_item:
        transaction_table.delete(selected_item)
        balance_update()
        save_to_csv()
    else:
        messagebox.showwarning("Seçim hatası", "Silinecek bir işlem seçin!")


# AYLIK KAR-ZARAR GRAFİĞİ
def monthly_status():
    df = pd.read_csv(file_name)
    df["TARİH"] = pd.to_datetime(df["TARİH"])
    
    df["AY"] = df["TARİH"].dt.strftime("%Y-%m")
    monthly_data = df.groupby(["AY", "TÜR"])["MİKTAR"].sum().unstack().fillna(0)

    # Kar Zarar Hesaplama
    monthly_data["KAR/ZARAR"] = monthly_data.get("GELEN", 0) - monthly_data.get("GİDEN", 0)

    months = monthly_data.index
    profit_loss_values = monthly_data["KAR/ZARAR"]

    # Grafik Çizme
    fig, ax = plt.subplots(figsize=(8,7))
    colors = ["green" if val >= 0 else "red" for val in profit_loss_values]
    bars = ax.bar(months, profit_loss_values, color=colors)

    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45)
    ax.set_xlabel("Aylar")
    ax.set_ylabel("Kâr / Zarar (TL)")
    ax.set_title("Aylık Kâr ve Zarar Tablosu")
    ax.axhline(0, color="black", linewidth=1)
    ax.bar_label(bars, fmt="%.0f", label_type="center", fontsize=10, color="black")
    plt.get_current_fig_manager().window.wm_geometry("+50+30")
    plt.tight_layout()
    plt.show()


#AYLIK GELİR GRAFİĞİ
def monthly_income_chart():
    df = pd.read_csv(file_name)
    df["TARİH"] = pd.to_datetime(df["TARİH"])
    df["AY"] = df["TARİH"].dt.to_period("M")

    monthly_income = df[df["TÜR"] == "GELEN"].groupby("AY")["MİKTAR"].sum()

    if monthly_income.empty:
        messagebox.showwarning("Veri yok", "Grafik için yeterli veri yok!")
        return

    ax = monthly_income.plot(kind="bar", color="#929695", figsize=(7,6))
    ax.bar_label(ax.containers[0], label_type="center")
    plt.title("Aylık Gelir Grafiği")
    plt.xlabel("AY")
    plt.ylabel("TOPLAM GELİR")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.get_current_fig_manager().window.wm_geometry("+50+30")
    plt.show()


#AYLIK GİDER GRAFİĞİ
def monthly_expense_chart():
    df = pd.read_csv(file_name)
    df["TARİH"] = pd.to_datetime(df["TARİH"])
    df["AY"] = df["TARİH"].dt.to_period("M")

    monthly_income = df[df["TÜR"] == "GİDEN"].groupby("AY")["MİKTAR"].sum()

    if monthly_income.empty:
        messagebox.showwarning("Veri yok", "Grafik için yeterli veri yok!")
        return

    ax = monthly_income.plot(kind="bar", color="#929695", figsize=(7,6))
    ax.bar_label(ax.containers[0], label_type="center")
    plt.title("Aylık Gider Grafiği")
    plt.xlabel("AY")
    plt.ylabel("TOPLAM GİDER")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.get_current_fig_manager().window.wm_geometry("+50+30")
    plt.show()


# Aylık gider pasta grafiği
def expense_pie_chart(selected_month):
    expenses = {}

    for item in transaction_table.get_children():
        item_values = transaction_table.item(item)["values"]
        if item_values[0] == "GİDEN":
            transaction_date = pd.to_datetime(item_values[3]) 
            if transaction_date.month == selected_month.month and transaction_date.year == selected_month.year:
                description = item_values[1]
                amount = int(item_values[2])
                if description in expenses:
                    expenses[description] += amount
                else:
                    expenses[description] = amount

    labels = list(expenses.keys())
    sizes = list(expenses.values())

    if not sizes:
        messagebox.showwarning("Veri yok", "Bu ay için gider verisi yok!")
        return
    
    # Pasta dilimlerinde hem yüzdeleri hem de toplam tutarı göstermek için özel bir fonksiyon
    def format_label(pct, all_values):
        absolute = int(pct/100.*sum(all_values))
        return f"{pct:.1f}%\n{absolute} TL"

    explode = [0.00] * len(sizes)
    plt.figure(figsize=(6, 6.2))
    plt.pie(sizes, labels=labels, shadow=False, explode=explode, autopct=lambda pct:format_label(pct, sizes), startangle=90)
    plt.axis("equal")
    plt.title(f"Aylık Gider Grafiği - {selected_month.strftime('%B %Y')}")
    plt.get_current_fig_manager().window.wm_geometry("+50+30")
    
    # Ay girişi için Entry ekle
    month_input = tk.Entry(plt.gcf().canvas.manager.window, width=7, font="Helvatica 14")
    month_input.insert(0, selected_month.strftime('%Y-%m'))
    month_input.pack(pady=10)

    # Değişiklikleri onaylamak için bir buton ekle
    confirm_button = tk.Button(plt.gcf().canvas.manager.window, font="Helvatica 11" ,text="Farklı Ay Göster", command=lambda: show_custom_expense_pie_chart(month_input.get()))
    confirm_button.pack(pady=1)

    plt.show()


# Kullanıcının belirlediği ay için Gider Pasta Grafiği
def show_custom_expense_pie_chart(month_input):
    try:
        selected_month = pd.to_datetime(month_input + "-01")  # Ayın ilk günü
        expense_pie_chart(selected_month)
    except ValueError:
        messagebox.showwarning("Hata", "Geçersiz tarih formatı! Lütfen 'YYYY-AA' formatında girin.")


# Mevcut Ay Gider Pasta Grafiği
def current_month_expense_pie_chart():
    today = datetime.now()
    selected_month = pd.to_datetime(today.strftime("%Y-%m-1"))  # Ayın ilk günü
    expense_pie_chart(selected_month)


# GELİR KATAGORİ YENİ PENCERE EKLEME
def income_new_window():
    catagory_window = tk.Toplevel(proje)
    catagory_window.title("Katagoriye Göre Gelirler")
    catagory_window.geometry("380x580+50+100")
    catagory_window.config(bg="#c5cfde")
    catagory_window.resizable(False, False)

    # GELENLERİ BULMA VE TOPLAMA
    income = {}
    for item in transaction_table.get_children():
        item_values = transaction_table.item(item)["values"]
        if item_values[0] == "GELEN":
            description = item_values[1]
            amount = item_values[2]
            if description in income:
                income[description] += int(amount)
            else:
                income[description] = int(amount)

    if not income:
        messagebox.showwarning("Veri yok","Gider verisi bulunamadı")
        catagory_window.destroy()
        return

    # YENİ PENCERE ETİKETLERİ
    new_window_title = tk.Label(catagory_window, text="KATEGORİYE GÖRE GELİR TABLOLARI", font="Helvatica 13", bg="#c5cfde")
    new_window_title.pack(pady=(17,25))

    # Seperator Ekleme
    separator = ttk.Separator(catagory_window, orient="horizontal")
    separator.place(x=40, y=55, relwidth=0.8)

    # Butonları Oluşturma
    for description, amount in sorted(income.items()):
        description_button = tk. Button(catagory_window, text=f"{description}", font="Helvatica 11", width=25, command=lambda desc=description, amt=amount:income_detail_table(desc))
        description_button.pack(pady=3)

    # DETAY İÇİN YENİ PENCERE OLUŞTURMA
    def income_detail_table(description):
        income_detail_window = tk.Toplevel()
        income_detail_window.title(f"{description} Detay Tablosu")
        income_detail_window.geometry("550x420+120+100")
        income_detail_window.configure(bg="#c5cfde")
        income_detail_window.resizable(False, False)

        # DETAY TREE TABLOSU
        columns = ("AÇIKLAMA", "MİKTAR", "TARİH")
        income_tree_table = ttk.Treeview(income_detail_window, columns=columns, show="headings")
        for col in columns:
            income_tree_table.heading(col, text=col)

        income_tree_table.column("AÇIKLAMA", width=150)    
        income_tree_table.column("MİKTAR", width=75)    
        income_tree_table.column("TARİH", width=75)    

        # GELEN DETAYLAR
        for item in transaction_table.get_children():
            item_values = transaction_table.item(item)["values"]
            if item_values[0] == "GELEN" and item_values[1] == description:
                income_tree_table.insert("", tk.END, values=(item_values[1], item_values[2], item_values[3]))


        # Treeview için scrolbar
        scrollbar = ttk.Scrollbar(income_detail_window, orient="vertical", command=income_tree_table.yview)
        income_tree_table.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.91, rely=0.22, relheight=0.59)

        income_tree_table.place(relx=0.04, rely=0.175, relwidth=0.92, relheight=0.67)

        detail_window_title = tk.Label(income_detail_window, text=f"{description} Detay Tablosu", font="Helvatica 17", bg="#c5cfde")
        detail_window_title.place(relx=0.5, rely=0.075, anchor="center") 

        # Seperator Ekleme
        separator = ttk.Separator(income_detail_window, orient='horizontal')
        separator.place(relx=0.1, rely=0.135, relwidth=0.8) 

        # Sİl BUTONU FONKSİYONU
        def delete_entry_from_details():
            selected_item = income_tree_table.selection()
            if selected_item:
                income_tree_table.delete(selected_item)

                for item in transaction_table.get_children():
                    item_values = transaction_table.item(item)["values"]
                    if item_values[0] == "GELEN" and item_values[1] == description:
                        transaction_table.delete(item)
                        break
                    
                balance_update()
                save_to_csv()

            else:
                messagebox.showwarning("Seçim hatası", "Silinecek bir işlem seçin!")
        delete_button = tk.Button(income_detail_window, text="Sil", font="Helvatica 11", width=10, command=delete_entry_from_details)
        delete_button.place(relx=0.5, rely=0.92, anchor="center")


# GİDER KATAGORİ YENİ PENCERE EKLEME
def new_window():
    catagory_window = tk.Toplevel(proje)
    catagory_window.title("Katagoriye Göre Giderler")
    catagory_window.geometry("380x580+50+100")
    catagory_window.config(bg="#c5cfde")
    catagory_window.resizable(False, False)

    #GİDERLERİ BULMA VE TOPLAMA
    expenses = {}
    for item in transaction_table.get_children():
        item_values = transaction_table.item(item)["values"]
        if item_values[0] == "GİDEN":
            description = item_values[1]
            amount = item_values[2]
            if description in expenses:
                expenses[description] += int(amount)
            else:
                expenses[description] = int(amount)    

    if not expenses:
        messagebox.showwarning("Veri yok","Gider verisi bulunamadı")
        catagory_window.destroy()
        return
    
    # YENİ PENCERE ETİKETLERİ
    new_window_title = tk.Label(catagory_window, text="KATEGORİYE GÖRE GİDER TABLOLARI", font="Helvatica 13", bg="#c5cfde")
    new_window_title.pack(pady=(17,25))

    # Separator (çizgi) ekleme
    separator = ttk.Separator(catagory_window, orient='horizontal')
    separator.place(x=40, y=55, relwidth=0.8) 

    # BUTONLAR OLUŞTURMA
    for description, amount in sorted(expenses.items()):
        description_button = tk.Button(catagory_window, text=f"{description}", font="Helvatica 11", width=25, command=lambda desc=description, amt=amount:expense_detail_table(desc))
        description_button.pack(pady=3)

    # DETAY İÇİN YENİ PENCERE OLUŞTURMA
    def expense_detail_table(description):
        expense_detail_window = tk.Toplevel()
        expense_detail_window.title(F"{description} Detay Tablosu")
        expense_detail_window.geometry("550x420+120+100")
        expense_detail_window.configure(bg="#c5cfde")
        expense_detail_window.resizable(False, False)

        # DETAY TREE TABLOSU
        columns = ("AÇIKLAMA", "MİKTAR", "TARİH")
        expense_tree_table = ttk.Treeview(expense_detail_window, columns=columns, show="headings")
        for col in columns:
            expense_tree_table.heading(col, text=col)

        expense_tree_table.column("AÇIKLAMA", width=150)
        expense_tree_table.column("MİKTAR", width=75)
        expense_tree_table.column("TARİH", width=75)

        # GİDER DETAYLARI
        for item in transaction_table.get_children():
            item_values = transaction_table.item(item)["values"]
            if item_values[0] == "GİDEN" and item_values[1] == description:
                expense_tree_table.insert("", tk.END, values=(item_values[1], item_values[2], item_values[3]))

        # Treeview için kaydırma çubuğu ekleme
        scrollbar = ttk.Scrollbar(expense_detail_window, orient="vertical", command=expense_tree_table.yview)
        expense_tree_table.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.91, rely=0.22, relheight=0.59)        
        
        # TABLOYU KONUMLANDIR
        expense_tree_table.place(relx=0.04, rely=0.175, relwidth=0.92, relheight=0.67)        

        # DETAY PENCERESİ ETİKETLERİ
        detail_window_title = tk.Label(expense_detail_window, text=f"{description} Detay Tablosu", font="Helvatica 17", bg="#c5cfde")
        detail_window_title.place(relx=0.5, rely=0.075, anchor="center")     

        # Separator (çizgi) ekleme
        separator = ttk.Separator(expense_detail_window, orient='horizontal')
        separator.place(relx=0.1, rely=0.135, relwidth=0.8)   

        # SİL BUTONU FONKSİYONU
        def delete_entry_from_details():
            selected_item = expense_tree_table.selection()
            if selected_item:
                # Detay tablosundan sil
                expense_tree_table.delete(selected_item)

                # Ana tablodaki ilgili veriyi bul ve sil
                for item in transaction_table.get_children():
                    item_values = transaction_table.item(item)["values"]
                    if item_values[0] == "GİDEN" and item_values[1] == description:
                        transaction_table.delete(item)
                        break  # İlk bulduğunda sil ve döngüden çık

                balance_update()  
                save_to_csv()  

            else:
                messagebox.showwarning("Seçim hatası", "Silinecek bir işlem seçin!")

        # Sil BUTONU
        delete_button = tk.Button(expense_detail_window, text="Sil", font="Helvatica 11", width=10, command=delete_entry_from_details)
        delete_button.place(relx=0.5, rely=0.92, anchor="center")


# GELEN PARA TÜR VE MİKTAR 
income_type_label = tk.Label(proje, text="Açıklama", font="Helvatica 11")
income_type_label.place(relx=0.1, rely=0.055, anchor="center")
income_type_entry = tk.Entry(proje)
income_type_entry.place(relx=0.26, rely=0.055, anchor="center")

income_label = tk.Label(proje, text="Gelen Para", font="Helvatica 11")
income_label.place(relx=0.1, rely=0.13, anchor="center")
income_entry = tk.Entry(proje)
income_entry.place(relx=0.26, rely=0.13, anchor="center")

# GİDEN PARA TÜR VE MİKTAR
expense_type_label = tk.Label(proje, text="Açıklama", font="Helvatica 11")
expense_type_label.place(relx=0.46, rely=0.055, anchor="center")
expense_type_entry = tk.Entry(proje)
expense_type_entry.place(relx=0.62, rely=0.055, anchor="center")

expense_label = tk.Label(proje, text="Giden Para", font="Helvatica 11")
expense_label.place(relx=0.46, rely=0.13, anchor="center")
expense_entry = tk.Entry(proje)
expense_entry.place(relx=0.62, rely=0.13, anchor="center")

# BAKİYE BİLGİSİ
balance_label = tk.Label(proje, text=f"{balance} TL", font="Helvatica 14")
balance_label.place(relx=0.875, rely=0.055, anchor="center")

# EKLE BUTONU
add_button = tk.Button(proje, text="Ekle", font="Helvatica 10", width=6, command=add_entry)
add_button.place(relx=0.82, rely=0.13, anchor="center")

# Sil BUTONU
delete_button = tk.Button(proje, text="Sil", font="Helvatica 10", width=6, command=delete_entry)
delete_button.place(relx=0.92, rely=0.13, anchor="center")

# Separator (çizgi) ekleme
separator = ttk.Separator(proje, orient='horizontal')
separator.place(relx=0.1, rely=0.19, relwidth=0.8) 

# TABLO
colums=("TÜR", "AÇIKLAMA", "MİKTAR", "TARİH")
transaction_table = ttk.Treeview(proje, columns=colums, show="headings")

for col in colums:
    transaction_table.heading(col, text=col)

transaction_table.column("TÜR", width=100)
transaction_table.column("AÇIKLAMA", width=100)
transaction_table.column("MİKTAR", width=100)
transaction_table.column("TARİH", width=100)

# TABLOYU EKLEMEK
transaction_table.place(relx=0.1, rely=0.23, relwidth=0.8, relheight=0.55)

# Treeview için kaydırma çubuğu ekleme
scrollbar = ttk.Scrollbar(proje, orient="vertical", command=transaction_table.yview)
transaction_table.configure(yscroll=scrollbar.set)
scrollbar.place(relx=0.9, rely=0.23, relheight=0.55)

# KAR / ZARAR GRAFİĞİ BUTONU
profit_loss_button = tk.Button(proje, text="Kâr ve Zarar Grafiği", font="Helvatica 11", width=14, command=monthly_status)
profit_loss_button.place(relx=0.82, rely=0.85, anchor="center")

# AYLIK GİDER PASTA GRAFİĞİ BUTONU
current_month_pie_chart_button = tk.Button(proje, text="Aylık Gider Grafiği", font="Helvatica 11", width=13, command=current_month_expense_pie_chart)
current_month_pie_chart_button.place(relx=0.61, rely=0.85, anchor="center")

# GELİR GRAFİĞİ BUTONU
monthly_income_button = tk.Button(proje, text="Gelir Grafiği", font="Helvatica 11", width=10, command=monthly_income_chart)
monthly_income_button.place(relx=0.43, rely=0.85, anchor="center")

# GİDER GRAFİĞİ BUTONU
monthly_expense_button = tk.Button(proje, text="Gider Grafiği", font="Helvatica 11", width=10, command=monthly_expense_chart)
monthly_expense_button.place(relx=0.43, rely=0.93, anchor="center")

# KATAGORİ GELİR BUTONU
category_income_button = tk.Button(proje, text="Kategori Gelir Tabloları", font="Helvatica 11", width=17, command=income_new_window)
category_income_button.place(relx=0.22, rely=0.85, anchor="center")

# KATAGORİ GİDER BUTONU
category_expense_button = tk.Button(proje, text="Kategori Gider Tabloları", font="Helvatica 11", width=17, command=new_window)
category_expense_button.place(relx=0.22, rely=0.93, anchor="center")


load_csv()
proje.mainloop()