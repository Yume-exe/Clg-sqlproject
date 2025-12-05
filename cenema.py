import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk 
import os
from datetime import datetime

DB_NAME = "cinema_booking.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT,
        duration_min INTEGER,
        image_filename TEXT,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS theaters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        theater_id INTEGER,
        show_time TEXT,
        total_seats INTEGER DEFAULT 20,
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (theater_id) REFERENCES theaters (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        show_id INTEGER,
        seat_number INTEGER,
        customer_name TEXT,
        timestamp TEXT,
        FOREIGN KEY (show_id) REFERENCES shows (id),
        UNIQUE(show_id, seat_number) 
    )
    """)

    cursor.execute("SELECT count(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        print("Seeding new data...")
        
        desc_inception = "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
        desc_dark_knight = "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."
        desc_interstellar = "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."

        cursor.execute("INSERT INTO movies (title, genre, duration_min, image_filename, description) VALUES (?, ?, ?, ?, ?)", 
                       ("Inception", "Sci-Fi", 148, "inception.jpg", desc_inception))
        cursor.execute("INSERT INTO movies (title, genre, duration_min, image_filename, description) VALUES (?, ?, ?, ?, ?)", 
                       ("The Dark Knight", "Action", 152, "dark_knight.jpg", desc_dark_knight))
        cursor.execute("INSERT INTO movies (title, genre, duration_min, image_filename, description) VALUES (?, ?, ?, ?, ?)", 
                       ("Interstellar", "Sci-Fi", 169, "interstellar.jpg", desc_interstellar))
        
        cursor.execute("INSERT INTO theaters (name, location) VALUES (?, ?)", ("Grand Cinema", "Alwar"))
        cursor.execute("INSERT INTO theaters (name, location) VALUES (?, ?)", ("Galaxy Multiplex", "Delhi"))
        
        cursor.execute("INSERT INTO shows (movie_id, theater_id, show_time) VALUES (1, 1, '18:00')")
        cursor.execute("INSERT INTO shows (movie_id, theater_id, show_time) VALUES (2, 1, '20:00')")
        cursor.execute("INSERT INTO shows (movie_id, theater_id, show_time) VALUES (3, 2, '19:30')")
        cursor.execute("INSERT INTO shows (movie_id, theater_id, show_time) VALUES (1, 2, '21:00')")
        
        conn.commit()
    conn.close()

class MovieBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Absolute Cinema")
        self.root.geometry("1000x700") 

        self.selected_show_id = None
        self.selected_seat_num = None
        self.poster_image_ref = None 

        tk.Label(root, text="Cinema Booking System", font=("Helvetica", 20, "bold"), bg="#222", fg="white").pack(fill=tk.X)

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Label(left_frame, text="Now Showing", font=("Arial", 12, "bold")).pack(anchor="w")
        
        cols = ("ID", "Movie", "Theater", "Time")
        self.tree = ttk.Treeview(left_frame, columns=cols, show='headings', height=25)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Movie", text="Movie")
        self.tree.heading("Theater", text="Theater")
        self.tree.heading("Time", text="Time")
        self.tree.column("ID", width=30); self.tree.column("Movie", width=120)
        self.tree.column("Theater", width=120); self.tree.column("Time", width=60)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_show_select)

        center_frame = tk.Frame(main_frame, width=250, bg="#f9f9f9", relief=tk.RIDGE, borderwidth=2)
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.poster_label = tk.Label(center_frame, text="Select a movie", bg="#ddd", width=25, height=15)
        self.poster_label.pack(pady=10, padx=10)
        
        self.lbl_movie_title = tk.Label(center_frame, text="", font=("Arial", 14, "bold"), bg="#f9f9f9", wraplength=230)
        self.lbl_movie_title.pack(pady=5)
        
        tk.Label(center_frame, text="Synopsis:", font=("Arial", 10, "bold"), bg="#f9f9f9", anchor="w").pack(fill=tk.X, padx=10)
        
        self.txt_description = tk.Text(center_frame, height=10, width=30, wrap=tk.WORD, bg="#f9f9f9", bd=0, font=("Arial", 10))
        self.txt_description.pack(padx=10, pady=5)
        self.txt_description.config(state=tk.DISABLED) 

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_frame, text="Select Seat", font=("Arial", 12, "bold")).pack(anchor="w")
        self.seat_grid = tk.Frame(right_frame)
        self.seat_grid.pack(pady=10)

        control_frame = tk.Frame(right_frame, pady=10, relief=tk.GROOVE, borderwidth=1)
        control_frame.pack(fill=tk.X, pady=10)

        tk.Label(control_frame, text="Selected Seat:").grid(row=0, column=0, sticky="e")
        self.lbl_selected_seat = tk.Label(control_frame, text="None", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_selected_seat.grid(row=0, column=1, sticky="w", padx=10)

        tk.Label(control_frame, text="Customer Name:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_name = tk.Entry(control_frame)
        self.entry_name.grid(row=1, column=1, sticky="w", padx=10)

        self.btn_book = tk.Button(control_frame, text="CONFIRM BOOKING", bg="#28a745", fg="white", 
                                  font=("Arial", 10, "bold"), command=self.book_ticket)
        self.btn_book.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

        tk.Label(right_frame, text="Recent Transaction Logs", font=("Courier", 10, "bold")).pack(anchor="w", pady=(20, 0))
        
        log_frame = tk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_list = tk.Listbox(log_frame, height=8, font=("Courier", 9), bg="#eee")
        self.log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_list.config(yscrollcommand=scrollbar.set)

        self.load_shows()

    def load_shows(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT s.id, m.title, t.name, s.show_time, m.image_filename, m.genre, m.duration_min, m.description
            FROM shows s
            JOIN movies m ON s.movie_id = m.id
            JOIN theaters t ON s.theater_id = t.id
        """
        self.shows_data = cursor.execute(query).fetchall()
        conn.close()

        for row in self.shows_data:
            self.tree.insert("", tk.END, values=(row["id"], row["title"], row["name"], row["show_time"]))

    def on_show_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return

        item_values = self.tree.item(selected_item)['values']
        self.selected_show_id = item_values[0]
        
        show_details = next((row for row in self.shows_data if row['id'] == self.selected_show_id), None)

        if show_details:
            self.load_poster(show_details['image_filename'])
            self.lbl_movie_title.config(text=show_details['title'])
            
            self.txt_description.config(state=tk.NORMAL) 
            self.txt_description.delete("1.0", tk.END)  
            self.txt_description.insert("1.0", show_details['description']) 
            self.txt_description.config(state=tk.DISABLED) 

        self.selected_seat_num = None
        self.lbl_selected_seat.config(text="None")
        self.refresh_seats()

    def load_poster(self, filename):
        try:
            if not filename or not os.path.exists(filename): raise FileNotFoundError
            load = Image.open(filename).resize((200, 280))
            render = ImageTk.PhotoImage(load)
            self.poster_label.config(image=render, text="", width=200, height=280)
            self.poster_image_ref = render 
        except FileNotFoundError:
            self.poster_label.config(image="", text="[No Image]", width=25, height=15)

    def refresh_seats(self):
        for widget in self.seat_grid.winfo_children(): widget.destroy()

        conn = get_db_connection()
        cursor = conn.cursor()
        show = cursor.execute("SELECT total_seats FROM shows WHERE id=?", (self.selected_show_id,)).fetchone()
        bookings = cursor.execute("SELECT seat_number FROM bookings WHERE show_id=?", (self.selected_show_id,)).fetchall()
        conn.close()

        if not show: return
        booked_seats = [b['seat_number'] for b in bookings]

        for i in range(1, show['total_seats'] + 1):
            row = (i - 1) // 5
            col = (i - 1) % 5
            if i in booked_seats:
                btn = tk.Button(self.seat_grid, text="X", width=4, bg="#ffcccc", state="disabled", relief="flat")
            else:
                btn = tk.Button(self.seat_grid, text=str(i), width=4, bg="#ccffcc", cursor="hand2",
                                command=lambda seat=i: self.select_seat(seat))
            btn.grid(row=row, column=col, padx=3, pady=3)

    def select_seat(self, seat_num):
        self.selected_seat_num = seat_num
        self.lbl_selected_seat.config(text=str(seat_num))

    def add_log(self, message):
        """Adds a message to the log box with a timestamp"""
        time_now = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{time_now}] {message}"
        self.log_list.insert(0, log_entry)
        self.log_list.itemconfig(0, {'fg': 'green'})

    def book_ticket(self):
        name = self.entry_name.get()
        if not self.selected_show_id or not self.selected_seat_num or not name:
            messagebox.showwarning("Warning", "Please select Seat and enter Name.")
            return

        conn = get_db_connection()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("INSERT INTO bookings (show_id, seat_number, customer_name, timestamp) VALUES (?, ?, ?, ?)", 
                         (self.selected_show_id, self.selected_seat_num, name, timestamp))
            conn.commit()
            
            messagebox.showinfo("Success", "Booking Confirmed!")
            
            movie_title = self.lbl_movie_title.cget("text")
            self.add_log(f"Seat {self.selected_seat_num} booked for {name}")
            
            self.entry_name.delete(0, tk.END)
            self.selected_seat_num = None
            self.lbl_selected_seat.config(text="None")
            self.refresh_seats()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Seat taken!")
        finally:
            conn.close()

if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = MovieBookingApp(root)
    root.mainloop()