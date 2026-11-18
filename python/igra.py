import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет личных финансов")
        self.root.geometry("680x480")
        self.root.resizable(False, False)
        
        self.conn = sqlite3.connect("finance.db")
        self.create_table()
        
        self.setup_styles()
        self.setup_ui()
        self.load_transactions()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    type TEXT,
                    category TEXT,
                    amount REAL,
                    comment TEXT
                )
            """)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

    def setup_ui(self):
        # Верхняя панель с балансом
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        top_frame.pack(fill=tk.X)
        
        self.balance_label = tk.Label(
            top_frame, text="Баланс: 0.00 ₽", 
            font=("Segoe UI", 16, "bold"), bg="#2c3e50", fg="white"
        )
        self.balance_label.pack(pady=15)

        # Панель добавления записи
        input_frame = tk.LabelFrame(self.root, text="Новая операция", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(input_frame, text="Тип:").grid(row=0, column=0, padx=5, sticky="w")
        self.type_var = tk.StringVar(value="Расход")
        type_cb = ttk.Combobox(input_frame, textvariable=self.type_var, values=["Расход", "Доход"], width=10, state="readonly")
        type_cb.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, sticky="w")
        self.cat_var = tk.StringVar(value="Продукты")
        cat_cb = ttk.Combobox(
            input_frame, textvariable=self.cat_var, 
            values=["Продукты", "Транспорт", "Жилье", "Развлечения", "Зарплата", "Подарки", "Другое"], 
            width=14
        )
        cat_cb.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Сумма:").grid(row=0, column=4, padx=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=12)
        self.amount_entry.grid(row=0, column=5, padx=5)

        tk.Label(input_frame, text="Комментарий:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.comment_entry = ttk.Entry(input_frame, width=42)
        self.comment_entry.grid(row=1, column=1, columnspan=4, padx=5, pady=8, sticky="w")

        add_btn = tk.Button(
            input_frame, text="Добавить", bg="#27ae60", fg="white", 
            font=("Segoe UI", 9, "bold"), width=12, command=self.add_transaction
        )
        add_btn.grid(row=1, column=5, padx=5, pady=8)

        # Таблица транзакций
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ("id", "date", "type", "category", "amount", "comment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("comment", text="Комментарий")

        self.tree.column("id", width=35, anchor="center")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("type", width=75, anchor="center")
        self.tree.column("category", width=110)
        self.tree.column("amount", width=95, anchor="e")
        self.tree.column("comment", width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Нижняя кнопка удаления
        del_btn = tk.Button(
            self.root, text="Удалить выбранную запись", bg="#c0392b", fg="white",
            font=("Segoe UI", 9), command=self.delete_transaction
        )
        del_btn.pack(pady=8)

    def add_transaction(self):
        t_type = self.type_var.get()
        category = self.cat_var.get().strip()
        comment = self.comment_entry.get().strip()
        
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную положительную сумму.")
            return

        if not category:
            messagebox.showerror("Ошибка", "Укажите категорию.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "INSERT INTO transactions (date, type, category, amount, comment) VALUES (?, ?, ?, ?, ?)",
                (date_str, t_type, category, amount, comment)
            )

        self.amount_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)
        self.load_transactions()

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись в таблице для удаления.")
            return
        
        item_id = self.tree.item(selected[0])["values"][0]
        with self.conn:
            self.conn.execute("DELETE FROM transactions WHERE id = ?", (item_id,))
        self.load_transactions()

    def load_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, date, type, category, amount, comment FROM transactions ORDER BY id DESC")
        rows = cursor.fetchall()

        balance = 0.0
        for row in rows:
            t_id, date, t_type, category, amount, comment = row
            if t_type == "Доход":
                balance += amount
                formatted_amount = f"+{amount:.2f}"
            else:
                balance -= amount
                formatted_amount = f"-{amount:.2f}"
                
            self.tree.insert("", tk.END, values=(t_id, date, t_type, category, formatted_amount, comment))

        color = "#2ecc71" if balance >= 0 else "#e74c3c"
        self.balance_label.config(text=f"Текущий баланс: {balance:.2f} ₽", fg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
