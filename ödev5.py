import tkinter as tk
from tkinter import Menu, messagebox
import sqlite3
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, Menu, simpledialog
import sqlite3
from collections import Counter


# Veritabanına bağlan ve metinleri kaydet
def connect_and_save(text1, text2):
    conn = sqlite3.connect('texts.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS Texts')
    cursor.execute('CREATE TABLE Texts (id INTEGER PRIMARY KEY, text TEXT)')
    cursor.execute('INSERT INTO Texts (text) VALUES (?)', (text1,))
    cursor.execute('INSERT INTO Texts (text) VALUES (?)', (text2,))
    conn.commit()
    conn.close()

# Metinleri yükle ve 'Counter' yöntemi ile karşılaştır
def load_and_compare_texts():
    conn = sqlite3.connect('texts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM Texts')
    texts = [text[0].lower() for text in cursor.fetchall()]
    conn.close()
    words_text1 = Counter(texts[0].split())
    words_text2 = Counter(texts[1].split())
    all_words = set(words_text1).union(words_text2)
    intersection = sum(min(words_text1[word], words_text2[word]) for word in all_words)
    total_words = sum(words_text1[word] + words_text2[word] for word in all_words)
    similarity_score = (2.0 * intersection) / total_words if total_words > 0 else 1.0
    return similarity_score

# Jaccard benzerlik algoritmasını kullanarak metinleri karşılaştır
def jaccard_similarity():
    conn = sqlite3.connect('texts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM Texts')
    texts = [text[0].lower() for text in cursor.fetchall()]
    conn.close()
    words_text1 = set(texts[0].split())
    words_text2 = set(texts[1].split())
    intersection = words_text1.intersection(words_text2)
    union = words_text1.union(words_text2)
    if not union:
        return 1.0  # Boş kümeler %100 benzerdir.
    similarity_score = len(intersection) / len(union)
    return similarity_score



def connect_db():
    return sqlite3.connect('application.db')

def verify_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    if not username or not password:
        messagebox.showwarning("Registration Failed", "Username and password cannot be empty.")
        return False
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Failed", "This username is already taken.")
        return False
    finally:
        conn.close()

def change_password_prompt(username):
    new_password = simpledialog.askstring("Change Password", "Enter new password:", show='*')
    if new_password:
        update_password(username, new_password)

def update_password(username, new_password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Password updated successfully.")

def load_and_compare_texts(method):
    file1 = filedialog.askopenfilename(title="Select first text file", filetypes=[("Text files", "*.txt")])
    file2 = filedialog.askopenfilename(title="Select second text file", filetypes=[("Text files", "*.txt")])
    if file1 and file2:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            text1, text2 = f1.read(), f2.read()
        if method == "counter":
            score = counter_similarity(text1, text2)
        elif method == "jaccard":
            score = jaccard_similarity(text1, text2)
        messagebox.showinfo("Similarity Result", f"The similarity score is {score:.2f}")

def counter_similarity(text1, text2):
    words1 = Counter(text1.lower().split())
    words2 = Counter(text2.lower().split())
    intersection = sum(min(words1[word], words2[word]) for word in set(words1) | set(words2))
    total_words = sum(words1[word] + words2[word] for word in set(words1) | set(words2))
    return (2 * intersection) / total_words if total_words > 0 else 1.0

def jaccard_similarity(text1, text2):
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 1.0

def create_main_window(user):
    window = tk.Tk()
    window.title("Text Comparison Tool")
    menu_bar = Menu(window)
    window.config(menu=menu_bar)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Exit", command=window.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    compare_menu = Menu(menu_bar, tearoff=0)
    compare_menu.add_command(label="Compare Using Counter", command=lambda: load_and_compare_texts("counter"))
    compare_menu.add_command(label="Compare Using Jaccard", command=lambda: load_and_compare_texts("jaccard"))
    menu_bar.add_cascade(label="Compare", menu=compare_menu)
    settings_menu = Menu(menu_bar, tearoff=0)
    settings_menu.add_command(label="Change Password", command=lambda: change_password_prompt(user))
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    window.mainloop()

def login_or_register():
    login_window = tk.Tk()
    login_window.title("Login or Register")
    tk.Label(login_window, text="Username:").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()
    tk.Label(login_window, text="Password:").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()
    def attempt_login():
        user = username_entry.get()
        pwd = password_entry.get()
        if verify_user(user, pwd):
            messagebox.showinfo("Login Success", "Welcome!")
            login_window.destroy()
            create_main_window(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    def attempt_register():
        user = username_entry.get()
        pwd = password_entry.get()
        if register_user(user, pwd):
            messagebox.showinfo("Registration Success", "You are now registered and logged in.")
            login_window.destroy()
            create_main_window(user)
    tk.Button(login_window, text="Login", command=attempt_login).pack()
    tk.Button(login_window, text="Register", command=attempt_register).pack()
    login_window.mainloop()

if __name__ == "__main__":
    login_or_register()








