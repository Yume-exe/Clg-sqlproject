# Cinema Booking System

A Python-based **movie ticket booking application** built using **Tkinter GUI** and **SQLite database**.
This project simulates a real-world cinema ticketing system where users can select movies, view show timings, choose seats, and confirm bookings — all with a modern, user-friendly interface.

---

## Features

### Movie & Show Management

* Displays list of all available movie shows
* Shows movie poster, title, genre, and description
* Each movie mapped to a theater and showtime

### Seat Booking

* Interactive seat grid (20 seats, auto-arranged)
* Booked seats turn **red** (disabled)
* Available seats shown in **green**
* Click any seat to select it

### Booking Confirmation

* Enter customer name
* Confirm booking with one click
* Auto-updates seat status
* Real-time **transaction logs**

### Database (SQLite)

* Auto-creates all tables on first run
* Inserts default movies, shows, and theaters
* Prevents double bookings using SQL UNIQUE constraints

---

## Technologies Used

* **Python 3**
* **Tkinter** (GUI)
* **SQLite3** (database)
* **PIL / Pillow** (for loading images)

---

## 🧠 How It Works

### ➤ Step 1: Select a Show

Choose a movie from the left table.

### ➤ Step 2: View Details

* Poster
* Title
* Description

### ➤ Step 3: Pick a Seat

Green = available
Red = already booked

### ➤ Step 4: Enter Customer Name

Click **CONFIRM BOOKING** → saved in database.

### ➤ Step 5: View Logs

Real-time booking logs displayed at the bottom-right.

---

## 🎓 Learning Outcomes

By completing this project, you will learn:

* GUI development using Tkinter
* Building relational databases with SQLite
* Using foreign keys & constraints
* Image handling using Pillow
* Event-driven programming
* Data validation and real-time UI updates

---

## 🖼 Screenshots

<img width="1506" height="1098" alt="image" src="https://github.com/user-attachments/assets/f3d2e99e-15c9-4616-8cf0-88968f244084" />


## 📄 License

MIT License © Jitesh Jangid

