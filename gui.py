import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
import os
import db

def get_movie_poster(movie_id, size=(100,140)):
    poster_folder = "posters"
    path = os.path.join(poster_folder, f"{movie_id}.jpg")
    if not os.path.exists(path):
        path = os.path.join(poster_folder, "placeholder.jpg")
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#181818")

        # Topbar (fixed at top)
        self.topbar = tk.Frame(self, bg="#232232")
        self.topbar.pack(fill='x')
        self.profile_img = None
        self.profile_btn = None
        self.make_topbar()

        # --- Scrollable page region (everything else in here!) ---
        self.canvas = tk.Canvas(self, bg="#181818", borderwidth=0, highlightthickness=0)
        self.page_frame = tk.Frame(self.canvas, bg="#181818")
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.create_window((0,0), window=self.page_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.canvas.pack(fill="both", expand=True, side="left")
        self.vscroll.pack(fill="y", side="right")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.page_frame.bind('<Configure>', on_frame_configure)

        # Centered BookMyShow Title
        tk.Label(
            self.page_frame, 
            text="BookMyShow", 
            font=("Arial Rounded MT Bold", 32), 
            fg="#E61C5D", 
            bg="#181818"
        ).pack(pady=8, anchor='center')

        # Centered search bar + city, movie, theatre dropdowns
        search_frame = tk.Frame(self.page_frame, bg="#181818")
        search_frame.pack(anchor='center', pady=6)

        # City Dropdown (NEW)
        tk.Label(search_frame, text="City:", fg="#ECC94B", bg="#181818", font=("Arial", 12)).pack(side='left', padx=4)
        self.city_var = tk.StringVar()
        city_list = sorted(set(t[2] for t in db.get_theatres()))
        self.city_dd = ttk.Combobox(search_frame, textvariable=self.city_var, values=city_list, state='readonly', width=12)
        self.city_dd.pack(side='left', padx=4)
        self.city_dd.bind("<<ComboboxSelected>>", lambda e: self.update_state())

        # Movie search
        tk.Label(search_frame, text="Search:", fg="#ECC94B", bg="#181818", font=("Arial", 12)).pack(side='left', padx=4)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=24)
        search_entry.pack(side='left', padx=4)
        ttk.Button(search_frame, text="Go", command=self.search_movies).pack(side='left', padx=6)

        # Theatre dropdown (filtered by city)
        self.theatre_var = tk.StringVar()
        tk.Label(search_frame, text="Theatre:", fg="#ECC94B", bg="#181818", font=("Arial", 12)).pack(side='left', padx=8)
        self.theatre_dd = ttk.Combobox(search_frame, textvariable=self.theatre_var, values=[], width=20)
        self.theatre_dd.pack(side='left', padx=6)
        ttk.Button(search_frame, text="Show", command=self.search_theatre).pack(side='left', padx=6)

        # Trending Movies
        tk.Label(self.page_frame, text="Trending Movies", font=("Arial Rounded MT Bold", 20), fg="#ECC94B", bg="#181818").pack(pady=10, anchor="center")
        self.trending_frame = tk.Frame(self.page_frame, bg="#181818")
        self.trending_frame.pack(pady=6, anchor="center")

        # All Movies (centered)
        tk.Label(self.page_frame, text="All Movies", font=("Arial Rounded MT Bold", 16), fg="#fff", bg="#181818").pack(pady=8, anchor="center")
        self.all_movies_frame = tk.Frame(self.page_frame, bg="#181818")
        self.all_movies_frame.pack(anchor="center")

        # Offers
        tk.Label(
            self.page_frame, 
            text="Special Offers: Flat 10% Off With Loyalty Points!", 
            font=("Arial", 12), 
            fg="#ECC94B", 
            bg="#232232"
        ).pack(fill='x', pady=10, anchor="center")
        tk.Label(
            self.page_frame, 
            text="© 2025 BookMyShow Mini Project | Contact: support@bms.com", 
            font=("Arial", 11), 
            fg="#ecc", 
            bg="#181818"
        ).pack(side='bottom', pady=8, anchor="center")

        # State
        self.selected_city = None
        self.city_var.set(city_list[0] if city_list else "")  # pick default
        self.update_state()

    def make_topbar(self):
        for widget in self.topbar.winfo_children():
            widget.destroy()
        tk.Label(
            self.topbar,
            text="BookMyShow",
            font=("Arial Rounded MT Bold", 28),
            fg="#E61C5D",
            bg="#232232"
        ).pack(side='left', padx=10)
        if self.controller.user_id is None:
            ttk.Button(
                self.topbar,
                text="Sign In",
                command=lambda: self.controller.show_frame("LoginPage")
            ).pack(side='right', padx=10)
            ttk.Button(
                self.topbar,
                text="Sign Up",
                command=lambda: self.controller.show_frame("RegisterPage")
            ).pack(side='right', padx=0)
        else:
            profile_icon_path = "profile_icon.png"
            if os.path.exists(profile_icon_path):
                self.profile_img = PhotoImage(file=profile_icon_path)
            else:
                self.profile_img = None
            self.profile_btn = ttk.Menubutton(
                self.topbar,
                text=f"Welcome, {self.controller.user_name}  ",
                image=self.profile_img,
                compound="left" if self.profile_img else "none"
            )
            self.profile_btn.pack(side='right', padx=10)
            menu = tk.Menu(self.profile_btn, tearoff=0)
            menu.add_command(
                label="My Profile",
                command=lambda: self.controller.show_frame("ProfilePage")
            )
            menu.add_command(
                label="Booking History",
                command=lambda: self.controller.show_frame("BookingsPage")
            )
            menu.add_separator()
            menu.add_command(
                label="Logout",
                command=self.handle_logout
            )
            self.profile_btn['menu'] = menu
            self.profile_btn.image = self.profile_img

    def update_state(self):
        city = self.city_var.get()
        self.selected_city = city
        # Theatre dropdown options filtered by city
        theatre_list = [t[1] for t in db.get_theatres() if t[2] == city]
        self.theatre_dd['values'] = theatre_list
        # Show trending and all movies by city
        theatre_ids = [t[0] for t in db.get_theatres() if t[2] == city]
        screen_ids = [s[0] for s in db.get_screens() if s[1] in theatre_ids]
        city_movie_ids = set(db.get_movies_in_screens(screen_ids))
        all_movies = [m for m in db.get_movies_with_rating() if m[0] in city_movie_ids]
        trending = sorted(all_movies, key=lambda x: x[2], reverse=True)[:4]  # top 4 by rating IN CITY
        self.show_trending_movies(trending)
        self.show_all_movies(all_movies)

    def handle_logout(self):
        self.controller.user_id = None
        self.controller.user_name = None
        self.city_var.set("")
        self.make_topbar()
        self.update_state()
        self.controller.show_frame("LandingPage")

    def on_movie_click(self, movie_id):
        if self.controller.user_id is None:
            res = messagebox.askquestion("Login Required", "You need to sign in to book tickets.\nDo you want to sign in?")
            if res == "yes":
                self.controller.show_frame("LoginPage")
            else:
                return
        else:
            selected_city = self.city_var.get()
            self.controller.frames["MovieDetailPage"].show_movie(movie_id, selected_city)
            self.controller.show_frame("MovieDetailPage")


    def show_trending_movies(self, trending_movies):
        for w in self.trending_frame.winfo_children():
            w.destroy()
        self.trending_photos = []
        for i, tup in enumerate(trending_movies):
            movie_id, title = tup[0], tup[1]
            rating = tup[2] if len(tup) > 2 else None
            poster = get_movie_poster(movie_id)
            self.trending_photos.append(poster)
            movie_col = tk.Frame(self.trending_frame, bg="#181818")
            movie_col.grid(row=0, column=i, padx=8)
            lbl = tk.Label(movie_col, image=poster, bg="#181818", cursor="hand2")
            lbl.pack()
            tk.Label(movie_col, text=title, fg="#fff", bg="#181818", font=("Arial", 11)).pack()
            tk.Label(movie_col, text=f"Rating: {rating:.1f} ★" if rating else "Rating: N/A", fg="#ECC94B", bg="#181818", font=("Arial", 10)).pack()
            lbl.bind("<Button-1>", lambda e, mid=movie_id: self.on_movie_click(mid))

    def show_all_movies(self, all_movies):
        for w in self.all_movies_frame.winfo_children():
            w.destroy()
        self.all_photos = []
        for i, (movie_id, title, rating) in enumerate(all_movies):
            poster = get_movie_poster(movie_id)
            self.all_photos.append(poster)
            fr = tk.Frame(self.all_movies_frame, bg="#181818")
            fr.grid(row=i//5, column=i%5, padx=8, pady=3)
            lbl = tk.Label(fr, image=poster, bg="#181818", cursor="hand2")
            lbl.pack()
            tk.Label(fr, text=title, fg="#aaa", bg="#181818", font=("Arial", 10)).pack()
            tk.Label(fr, text=f"Rating: {rating:.1f} ★" if rating else "Rating: N/A", fg="#ECC94B", bg="#181818", font=("Arial", 10)).pack()
            lbl.bind("<Button-1>", lambda e, mid=movie_id: self.on_movie_click(mid))

    def search_movies(self):
        query = self.search_var.get().lower().strip()
        city = self.city_var.get()
        theatre_ids = [t[0] for t in db.get_theatres() if t[2] == city]
        screen_ids = [s[0] for s in db.get_screens() if s[1] in theatre_ids]
        city_movie_ids = set(db.get_movies_in_screens(screen_ids))
        all_movies = [m for m in db.get_movies_with_rating() if m[0] in city_movie_ids]
        if query:
            filtered = [(mid, title, rating) for mid, title, rating in all_movies if query in title.lower()]
            self.show_all_movies(filtered)
        else:
            self.show_all_movies(all_movies)

    def search_theatre(self):
        theatre_name = self.theatre_var.get().strip()
        if not theatre_name:
            return
        city = self.city_var.get()
        theatres = [t for t in db.get_theatres() if t[2] == city]
        theatre_lookup = {t[1]: t[0] for t in theatres}
        theatre_id = theatre_lookup.get(theatre_name)
        if not theatre_id:
            messagebox.showerror("Not Found", "Theatre not found.")
            return
        theatre_details = [t for t in db.get_theatres() if t[0] == theatre_id][0]
        results = db.get_movies_by_theatre_with_screens(theatre_id)
        self.controller.frames["TheatreDetailPage"].show_theatre(theatre_details, results)
        self.controller.show_frame("TheatreDetailPage")

    def show_movies_by_theatre(self, theatre_details, results):
        for w in self.all_movies_frame.winfo_children():
            w.destroy()
        # Unpack all fields from Theatre except theatre_id
        # Structure: (theatre_id, name, city, address, contact_no)
        _, name, city, address, contact_no = theatre_details

        tk.Label(self.all_movies_frame, text=f"{name}", font=("Arial Rounded MT Bold", 16), fg="#ECC94B", bg="#181818").pack(anchor='w', pady=(6,2))
        tk.Label(self.all_movies_frame, text=f"Address: {address}", font=("Arial", 11), fg="#fff", bg="#181818").pack(anchor='w')
        tk.Label(self.all_movies_frame, text=f"City: {city}", font=("Arial", 10), fg="#fa5", bg="#181818").pack(anchor='w')
        tk.Label(self.all_movies_frame, text=f"Contact: {contact_no}", font=("Arial", 10), fg="#ECC94B", bg="#181818").pack(anchor='w', pady=(0,8))

        if not results:
            tk.Label(self.all_movies_frame, text="No movies found for this theatre.", fg="#ECC94B", bg="#181818").pack()
            return

        from collections import defaultdict
        movies = defaultdict(lambda: defaultdict(list))
        for mtitle, screen_no, sdate, stime, show_id in results:
            movies[mtitle][screen_no].append((sdate, stime, show_id))

        for mtitle, screens in movies.items():
            tk.Label(self.all_movies_frame, text=mtitle, font=("Arial Rounded MT Bold", 13), fg="#47C9AF", bg="#181818").pack(anchor='w', pady=(10,3), padx=16)
            for screen_no, times in screens.items():
                tk.Label(self.all_movies_frame, text=f"Screen: {screen_no}", font=("Arial", 11), fg="#ECC94B", bg="#181818").pack(anchor='w', padx=28)
                for sdate, stime, show_id in times:
                    tk.Label(self.all_movies_frame, text=f"{sdate}  {stime}", font=("Arial", 10), fg="#fff", bg="#181818").pack(anchor='w', padx=48)

    def prompt_city_after_login(self):
        messagebox.showinfo("Choose City", "Please select your preferred city from the city dropdown at the top!")
        self.city_dd.focus_set()

class TheatreDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#232232")

        # Scrollable area
        self.canvas = tk.Canvas(self, bg="#232232", borderwidth=0, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.canvas, bg="#232232")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.canvas.pack(fill="both", expand=True, side="left")
        self.scrollbar.pack(fill="y", side="right")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.scroll_frame.bind('<Configure>', on_frame_configure)

        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("LandingPage")).pack(side='bottom', pady=14)

        self.header_frame = tk.Frame(self.scroll_frame, bg="#232232")
        self.header_frame.pack(pady=16, anchor='center')
        self.showtimes_frame = tk.Frame(self.scroll_frame, bg="#232232")
        self.showtimes_frame.pack(fill='both', padx=30, pady=8)

    def show_theatre(self, theatre_details, results):
        # Clear old
        for w in self.header_frame.winfo_children():
            w.destroy()
        for w in self.showtimes_frame.winfo_children():
            w.destroy()

        _, name, city, address, contact_no = theatre_details
        # Header details card
        tk.Label(self.header_frame, text=name, font=("Arial Rounded MT Bold", 22), fg="#ECC94B", bg="#232232").pack()
        tk.Label(self.header_frame, text=f"Address: {address}", font=("Arial", 12), fg="#fff", bg="#232232").pack()
        tk.Label(self.header_frame, text=f"City: {city}", font=("Arial", 12), fg="#fa5", bg="#232232").pack()
        tk.Label(self.header_frame, text=f"Contact: {contact_no}", font=("Arial", 12), fg="#ECC94B", bg="#232232").pack()

        if not results:
            tk.Label(self.showtimes_frame, text="No movies found for this theatre.", fg="#ECC94B", bg="#232232").pack()
            return

        from collections import defaultdict
        movies = defaultdict(lambda: defaultdict(list))
        for mtitle, screen_no, sdate, stime, show_id in results:
            movies[mtitle][screen_no].append((sdate, stime, show_id))

        for mtitle, screens in movies.items():
            tk.Label(self.showtimes_frame, text=mtitle, font=("Arial Rounded MT Bold", 14), fg="#47C9AF", bg="#232232").pack(anchor='w', pady=(11,2))
            for screen_no, times in screens.items():
                tk.Label(self.showtimes_frame, text=f"Screen: {screen_no}", font=("Arial", 11), fg="#ECC94B", bg="#232232").pack(anchor='w', padx=26, pady=(1,1))
                for sdate, stime, show_id in times:
                    time_fr = tk.Frame(self.showtimes_frame, bg="#232232")
                    time_fr.pack(anchor='w', padx=46, pady=(1,1))
                    tk.Label(time_fr, text=f"{sdate}", font=("Arial", 10), fg="#47C9AF", bg="#232232").pack(side='left')
                    book_btn = ttk.Button(
                        time_fr, 
                        text=f"{stime}  Book", 
                        width=12,
                        command=lambda mid=mtitle, tn=name, sc=screen_no, sd=sdate, st=stime, sid=show_id: BookingWindow(
                            self.controller.frames["LandingPage"], sid, mid, tn, sd, st, sc, self.controller.user_id
                        )
                    )
                    book_btn.pack(side='left', padx=6)


class BookingWindow(tk.Toplevel):
    def __init__(self, master, show_id, movie_name, theatre_name, show_date, show_time, screen_no, user_id):
        super().__init__(master)
        self.title("Book Your Seats")
        self.geometry("1200x700")
        self.show_id = show_id
        self.user_id = user_id
        # store context for payment/confirmation
        self.movie_name = movie_name
        self.theatre_name = theatre_name
        self.show_date = show_date
        self.show_time = show_time
        self.screen_no = screen_no
        self.max_tickets = 6
        self.selected = {}  # {show_seat_id: price}
        self.selected_labels = {}  # {show_seat_id: seat_no}
        self.total_price = tk.IntVar(value=0)
        self.seat_buttons = {}  # Track seat buttons for toggling
        self.configure(bg="#f0f0f0")
        
        # Top Info
        self.display_top_info(movie_name, theatre_name, show_date, show_time, screen_no)
        
        # Main content frame
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Seats display
        self.seat_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.seat_frame.pack(fill="both", expand=True)
        self.display_seats()
        
        # Legend
        legend_frame = tk.Frame(self, bg="#f0f0f0")
        legend_frame.pack(pady=10)
        tk.Label(legend_frame, text="Available", bg="#90EE90", relief="raised", width=12).pack(side='left', padx=5)
        tk.Label(legend_frame, text="Selected", bg="#FFD700", relief="raised", width=12).pack(side='left', padx=5)
        tk.Label(legend_frame, text="Booked/Reserved", bg="#D3D3D3", relief="raised", width=14).pack(side='left', padx=5)
        
        # Bottom section
        bottom_frame = tk.Frame(self, bg="#f0f0f0")
        bottom_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(bottom_frame, text="Total Price:", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(side='left')
        tk.Label(bottom_frame, textvariable=self.total_price, font=("Arial", 16, "bold"), fg="#FF6B6B", bg="#f0f0f0").pack(side='left', padx=10)
        tk.Button(bottom_frame, text="Pay & Confirm", font=("Arial", 14, "bold"), command=self.pay, bg="#47C9AF", fg="white", padx=20, pady=8).pack(side='right')
        
        # Auto-refresh seats every 5 seconds to show real-time reservations
        self._auto_refresh_seats()

    def display_top_info(self, movie, theatre, date, time, screen):
        info_frame = tk.Frame(self, bg="#232232")
        info_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(info_frame, text=f"{movie}", font=("Arial", 18, "bold"), fg="#ECC94B", bg="#232232").pack()
        tk.Label(info_frame, text=f"Theatre: {theatre} | Screen: {screen}", font=("Arial", 14), fg="#fff", bg="#232232").pack()
        tk.Label(info_frame, text=f"Show Date: {date} | Time: {time}", font=("Arial", 13), fg="#aaa", bg="#232232").pack()

    def _auto_refresh_seats(self):
        """Refresh seat display every 5 seconds to show real-time reservations from other users"""
        try:
            # Clear and redraw seats
            for w in self.seat_frame.winfo_children():
                w.destroy()
            # Preserve user selections before refresh
            old_selected = dict(self.selected)
            self.display_seats()
            # Restore user selections
            self.selected = old_selected
            # Re-apply selection colors
            for sid in self.selected.keys():
                btn = self.seat_buttons.get(sid)
                if btn:
                    btn.config(bg="#FFD700")
        except Exception:
            pass
        # Schedule next refresh in 5 seconds
        if self.winfo_exists():
            self.after(5000, self._auto_refresh_seats)

    def display_seats(self):
        seats = db.get_seat_data(self.show_id)
        
        # Group seats by row and type
        from collections import defaultdict
        rows_by_type = defaultdict(lambda: defaultdict(list))
        
        for seat in seats:
            sid, seat_no, seat_type, price, status = seat
            # Extract row letter (first char) and seat number
            row_letter = seat_no[0] if seat_no else "A"
            rows_by_type[seat_type][row_letter].append(seat)
        
        # Display by seat type with headers
        type_order = ['Regular', 'Gold', 'Platinum']
        type_colors = {'Regular': '#90EE90', 'Gold': '#FFD700', 'Platinum': '#D3D3D3'}
        
        for seat_type in type_order:
            if seat_type not in rows_by_type or not rows_by_type[seat_type]:
                continue
            
            # Section header with type and price
            type_frame = tk.Frame(self.seat_frame, bg="#f0f0f0")
            type_frame.pack(anchor="w", pady=(15, 5))
            
            price_sample = list(rows_by_type[seat_type].values())[0][0][3] if rows_by_type[seat_type] else 0
            tk.Label(type_frame, text=f"₹{price_sample} {seat_type.upper()}", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w")
            
            # Seats grid for this type
            seats_grid_frame = tk.Frame(self.seat_frame, bg="#f0f0f0")
            seats_grid_frame.pack(anchor="w", padx=20)
            
            row_list = sorted(rows_by_type[seat_type].keys())
            
            for row_letter in row_list:
                row_frame = tk.Frame(seats_grid_frame, bg="#f0f0f0")
                row_frame.pack(anchor="w", pady=3)
                
                # Row letter on left
                tk.Label(row_frame, text=row_letter, font=("Arial", 11, "bold"), width=3, bg="#f0f0f0").pack(side='left', padx=(0, 10))
                
                # Seats in this row
                seats_in_row = sorted(rows_by_type[seat_type][row_letter], key=lambda x: int(x[1][1:]) if x[1][1:].isdigit() else 0)
                
                for seat in seats_in_row:
                    sid, seat_no, seat_type_val, price, status = seat
                    
                    # Treat 'reserved' seats same as 'booked' (unavailable to other users)
                    if status == "booked" or status == "reserved":
                        btn = tk.Label(
                            row_frame, text=seat_no, font=("Arial", 9),
                            bg="#D3D3D3", relief="sunken", width=4, height=2
                        )
                    else:
                        btn = tk.Button(
                            row_frame, text=seat_no, font=("Arial", 9),
                            bg="#90EE90", relief="raised", width=4, height=2,
                            command=lambda s=seat, btn_ref=None: self.toggle_seat(s, btn_ref)
                        )
                    
                    btn.pack(side='left', padx=2)
                    self.seat_buttons[sid] = btn

    def toggle_seat(self, seat, btn_ref=None):
        sid, seat_no, seat_type, price, status = seat
        # Block selection if seat is booked or reserved
        if status == "booked" or status == "reserved":
            messagebox.showwarning("Unavailable", "This seat is already booked or reserved!")
            return
        
        if sid in self.selected:
            del self.selected[sid]
            if sid in self.selected_labels:
                del self.selected_labels[sid]
            # Change button back to green
            if sid in self.seat_buttons:
                self.seat_buttons[sid].config(bg="#90EE90")
        else:
            if len(self.selected) >= self.max_tickets:
                messagebox.showwarning("Limit", f"Max {self.max_tickets} seats per booking.")
                return
            self.selected[sid] = price
            self.selected_labels[sid] = seat_no
            # Change button to gold
            if sid in self.seat_buttons:
                self.seat_buttons[sid].config(bg="#FFD700")
        
        self.total_price.set(sum(self.selected.values()))
    def pay(self):
        # Open payment modal with selected seats and totals
        if not self.selected:
            messagebox.showinfo("No seats", "Please select at least one seat.")
            return
        selected_details = [(sid, self.selected_labels.get(sid, ""), price) for sid, price in self.selected.items()]
        # Controller is available via the master frame
        controller = getattr(self.master, 'controller', None)
        PaymentWindow(self, controller, self.show_id, self, selected_details, self.total_price.get())


class PaymentWindow(tk.Toplevel):
    def __init__(self, master, controller, show_id, booking_window, selected_details, total_price):
        super().__init__(master)
        self.title("Payment")
        self.geometry("700x520")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        self.controller = controller
        self.show_id = show_id
        self.booking_window = booking_window
        self.user_id = booking_window.user_id
        self.selected_details = selected_details  # list of (show_seat_id, seat_no, price)
        self.total_price = total_price
        
        # Movie poster (try to find movie id from title)
        movie_title = getattr(booking_window, 'movie_name', '')
        movie_id = None
        try:
            movies = db.get_movies()
            for mid, mtitle in movies:
                if mtitle == movie_title:
                    movie_id = mid
                    break
        except Exception:
            movie_id = None

        poster_img = get_movie_poster(movie_id, size=(140,200)) if movie_id else None

        top = tk.Frame(self, bg="#ffffff")
        top.pack(fill='x', pady=10)
        if poster_img:
            lbl = tk.Label(top, image=poster_img, bg="#ffffff")
            lbl.image = poster_img
            lbl.pack(side='left', padx=12)

        info_fr = tk.Frame(top, bg="#ffffff")
        info_fr.pack(side='left', fill='x', expand=True, padx=8)
        tk.Label(info_fr, text=movie_title, font=("Arial", 16, "bold"), bg="#ffffff").pack(anchor='w')
        tk.Label(info_fr, text=f"Theatre: {booking_window.theatre_name} | Screen: {booking_window.screen_no}", bg="#ffffff").pack(anchor='w', pady=2)
        tk.Label(info_fr, text=f"Show: {booking_window.show_date} | {booking_window.show_time}", bg="#ffffff").pack(anchor='w', pady=2)

        # Seats and amounts
        body = tk.Frame(self, bg="#ffffff")
        body.pack(fill='both', expand=True, padx=16, pady=6)

        seats_lbl = tk.Label(body, text="Seats Booked:", font=("Arial", 12, "bold"), bg="#ffffff")
        seats_lbl.pack(anchor='w')
        seats_list = ", ".join([sno for (_id, sno, _p) in self.selected_details])
        tk.Label(body, text=seats_list if seats_list else "-", bg="#ffffff").pack(anchor='w', pady=(0,8))

        amt_lbl = tk.Label(body, text=f"Amount: ₹{self.total_price}", font=("Arial", 12), bg="#ffffff")
        amt_lbl.pack(anchor='w')

        # Loyalty check
        self.use_loyalty = tk.BooleanVar(value=False)
        try:
            pts = db.get_user_loyalty(self.user_id) if self.user_id else 0
        except Exception:
            pts = 0
        discount_pct = db.get_user_discount(self.user_id) if self.user_id else 0
        self.final_amount = self.total_price
        if pts >= 500 and discount_pct and self.user_id:
            # Ask user if they want to apply loyalty
            resp = messagebox.askyesno("Loyalty Available", f"You have {pts} loyalty points. Apply {discount_pct}% discount?")
            if resp:
                discount_amt = int(self.total_price * (discount_pct/100.0))
                self.final_amount = max(0, self.total_price - discount_amt)
                tk.Label(body, text=f"Loyalty discount applied: -₹{discount_amt}", fg="#0a7", bg="#ffffff").pack(anchor='w', pady=(4,0))

        tk.Label(body, text=f"To Pay: ₹{self.final_amount}", font=("Arial", 14, "bold"), bg="#ffffff", fg="#D43F52").pack(anchor='w', pady=(8,12))

        # Payment mode selector
        mode_frame = tk.Frame(body, bg="#ffffff")
        mode_frame.pack(anchor='w', pady=(6,8))
        tk.Label(mode_frame, text="Payment Method:", bg="#ffffff").pack(side='left')
        self.mode_var = tk.StringVar(value="UPI")
        ttk.Combobox(mode_frame, textvariable=self.mode_var, values=["UPI", "Wallet", "Credit Card", "Net Banking"]).pack(side='left', padx=8)

        # Payment buttons
        btn_fr = tk.Frame(self, bg="#ffffff")
        btn_fr.pack(fill='x', pady=6, padx=12)
        self.confirm_btn = tk.Button(btn_fr, text="Confirm & Pay", bg="#47C9AF", fg="white", font=("Arial", 12, "bold"), command=self.confirm_payment)
        self.confirm_btn.pack(side='right')
        tk.Button(btn_fr, text="Cancel", command=self.on_cancel).pack(side='right', padx=6)

        # Create pending tickets and start payment timer (30s)
        self.ticket_ids = []
        try:
            seat_ids = [sid for sid, _sno, _p in self.selected_details]
            self.ticket_ids = db.create_pending_tickets(self.user_id, self.show_id, seat_ids)
            # Mark buttons in booking window as reserved visually
            try:
                for sid in seat_ids:
                    btn = getattr(self.booking_window, 'seat_buttons', {}).get(sid)
                    if btn:
                        btn.config(bg="#FFA07A", state='disabled')
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not start payment: {e}")
            self.destroy()
            return

        self.remaining_seconds = 120  # 2-minute window
        self.countdown_label = tk.Label(self, text=f"Time left to complete payment: {self.remaining_seconds}s", bg="#ffffff", fg="#D43F52", font=("Arial", 10, "bold"))
        self.countdown_label.pack(pady=(4,8))
        self._tick()

    def confirm_payment(self):
        # Finalize payment for pending tickets
        if not self.ticket_ids:
            messagebox.showerror("Error", "No pending tickets to finalize.")
            return
        try:
            mode = self.mode_var.get() if hasattr(self, 'mode_var') else 'UPI'
            payment_id = db.finalize_payment_for_tickets(self.ticket_ids, self.final_amount, mode)
            # Redeem loyalty if applicable
            if self.final_amount < self.total_price:
                try:
                    # Redeem based on first ticket
                    db.redeem_loyalty_discount(self.user_id, self.ticket_ids[0])
                except Exception:
                    pass
            messagebox.showinfo("Payment Successful", f"Payment completed. Payment ID: {payment_id}")
            # Show confirmation using first ticket id
            ConfirmationWindow(self, self.controller, self.ticket_ids[0], self.booking_window.movie_name, self.booking_window.theatre_name, self.booking_window.show_date, self.booking_window.show_time, [sno for (_id, sno, _p) in self.selected_details], self.final_amount)
            # Close booking and payment windows
            try:
                self.booking_window.destroy()
            except Exception:
                pass
            self.destroy()
        except Exception as e:
            err = str(e)
            if 'Cannot pay for cancelled ticket' in err or 'cancelled' in err.lower():
                messagebox.showerror("Payment Blocked", "Payment blocked: the ticket is cancelled. Please select other seats or contact support.")
            else:
                messagebox.showerror("Error", err)

    def on_cancel(self):
        # User cancelled payment: cancel the pending tickets and release seats
        try:
            if getattr(self, 'ticket_ids', None):
                try:
                    db.cancel_tickets(self.ticket_ids)
                except Exception:
                    pass
                # restore seat button states in booking window
                try:
                    for sid in [sid for sid, _sno, _p in self.selected_details]:
                        btn = getattr(self.booking_window, 'seat_buttons', {}).get(sid)
                        if btn:
                            btn.config(bg="#90EE90", state='normal')
                except Exception:
                    pass
        finally:
            messagebox.showinfo("Cancelled", "Payment cancelled. Booking has been released.")
            self.destroy()

    def _tick(self):
        # Countdown tick every second
        if self.remaining_seconds <= 0:
            # Timeout: cancel pending tickets
            try:
                if getattr(self, 'ticket_ids', None):
                    db.cancel_tickets(self.ticket_ids)
            except Exception:
                pass
            try:
                for sid in [sid for sid, _sno, _p in self.selected_details]:
                    btn = getattr(self.booking_window, 'seat_buttons', {}).get(sid)
                    if btn:
                        btn.config(bg="#90EE90", state='normal')
            except Exception:
                pass
            self.confirm_btn.config(state='disabled')
            self.countdown_label.config(text="Payment timed out. Booking cancelled.")
            messagebox.showwarning("Timeout", "Payment window timed out. Booking has been cancelled.")
            return
        else:
            self.countdown_label.config(text=f"Time left to complete payment: {self.remaining_seconds}s")
            self.remaining_seconds -= 1
            self.after(1000, self._tick)


class ConfirmationWindow(tk.Toplevel):
    def __init__(self, master, controller, ticket_id, movie, theatre, show_date, show_time, seats, amount):
        super().__init__(master)
        self.title("Booking Confirmed")
        self.geometry("600x380")
        self.configure(bg="#ffffff")
        self.controller = controller
        tk.Label(self, text="Booking Confirmed!", font=("Arial", 18, "bold"), bg="#ffffff", fg="#47C9AF").pack(pady=10)
        tk.Label(self, text=f"Ticket ID: {ticket_id}", bg="#ffffff").pack()
        tk.Label(self, text=f"Movie: {movie}", bg="#ffffff").pack()
        tk.Label(self, text=f"Theatre: {theatre}", bg="#ffffff").pack()
        tk.Label(self, text=f"Show: {show_date} | {show_time}", bg="#ffffff").pack()
        tk.Label(self, text=f"Seats: {', '.join(seats)}", bg="#ffffff").pack(pady=6)
        tk.Label(self, text=f"Amount Paid: ₹{amount}", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=8)
        tk.Button(self, text="Back to Home", command=self.back_home, bg="#232323", fg="white").pack(pady=12)

    def back_home(self):
        try:
            if self.controller:
                self.controller.show_frame("LandingPage")
        except Exception:
            pass
        self.destroy()

class MovieDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#232232")

        self.poster_label = tk.Label(self, bg="#232232")
        self.poster_label.pack(pady=16)

        self.info_label = tk.Label(self, bg="#232232", fg="#fff", font=("Arial Rounded MT Bold", 16), justify="left")
        self.info_label.pack(pady=2)

        # Scrollable area for showtimes
        self.canvas = tk.Canvas(self, bg="#232232", borderwidth=0, highlightthickness=0)
        self.showtimes_frame = tk.Frame(self.canvas, bg="#232232")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0,0), window=self.showtimes_frame, anchor="nw")
        self.canvas.pack(fill="both", expand=True, side="left")
        self.scrollbar.pack(fill="y", side="right")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.showtimes_frame.bind('<Configure>', on_frame_configure)

        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("LandingPage")).pack(side='bottom', pady=12)

    def show_movie(self, movie_id, city):
        for w in self.showtimes_frame.winfo_children():
            w.destroy()
        details = db.get_movie_details(movie_id)
        poster = get_movie_poster(movie_id, size=(130,180))
        self.poster_label.config(image=poster)
        self.poster_label.image = poster
        if details:
            title, genre, language, duration, release_date = details
            info = f"{title}  ({language})\nGenre: {genre}\nRuntime: {duration} mins\nRelease: {release_date}"
        else:
            info = "No info found."
        self.info_label.config(text=info)
        showtimes = db.get_movie_showtimes(movie_id, city)
        if not showtimes:
            tk.Label(self.showtimes_frame, text="No shows available.", fg="#ECC94B", bg="#232232").pack()
        else:
            from collections import defaultdict
            shows_by_theatre = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            for row in showtimes:
                if len(row) >= 5:
                    tname, screen_no, sdate, stime, show_id = row[0], row[1], row[2], row[3], row[4]
                else:
                    tname, screen_no, sdate, stime = row[0], row[1], row[2], row[3]
                    show_id = None
                shows_by_theatre[tname][screen_no][sdate].append((stime, show_id))
            for tname, screens in shows_by_theatre.items():
                tk.Label(self.showtimes_frame, text=tname, fg="#ECC94B", bg="#232232", font=("Arial Rounded MT Bold", 14)).pack(anchor='w', pady=(14,2))
                for screen_no, dates in screens.items():
                    tk.Label(self.showtimes_frame, text=f"Screen: {screen_no}", fg="#fa5", bg="#232232", font=("Arial Rounded MT Bold", 11)).pack(anchor='w', padx=24, pady=(4,1))
                    for sdate, times in dates.items():
                        date_frame = tk.Frame(self.showtimes_frame, bg="#232232")
                        date_frame.pack(anchor='w', padx=32)
                        tk.Label(date_frame, text=sdate, fg="#47C9AF", bg="#232232", font=("Arial", 12)).pack(side='left')
                        for t, sid in times:
                            if sid:
                                book_btn = ttk.Button(
                                    date_frame, 
                                    text=f"{t}  Book", 
                                    width=12,
                                    command=lambda tn=tname, sc=screen_no, sd=sdate, st=t, mid=movie_id, sid=sid: BookingWindow(
                                        self.controller.frames["LandingPage"], sid, title, tn, sd, st, sc, self.controller.user_id
                                    )
                                )
                                book_btn.pack(side='left', padx=6)
                            else:
                                btn = ttk.Button(date_frame, text=f"{t}", width=8, command=lambda: None)
                                btn.pack(side='left', padx=6)

class BookMyShowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BookMyShow Mini Project")
        self.geometry("950x680")
        self.resizable(width=True, height=True)
        self.user_id = None
        self.user_name = None
        self.admin_id = None
        self.admin_name = None
        self.frames = {}
        for F in (LandingPage, TheatreDetailPage, MovieDetailPage, LoginPage, RegisterPage, Dashboard, BookPage, ProfilePage, BookingsPage, ClaimLoyaltyPage, AdminDashboard):
            # use the class __name__ as the page identifier
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)
        self.show_frame("LandingPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "LandingPage":
            frame.update_state()
        elif page_name == "AdminDashboard":
            frame.refresh()
        frame.tkraise()

    def user_login(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        self.admin_id = None
        self.admin_name = None
        self.frames["LandingPage"].make_topbar()
        self.frames["LandingPage"].update_state()
        self.frames["LandingPage"].prompt_city_after_login()
        self.show_frame("LandingPage")

    def admin_login(self, admin_id, admin_name):
        self.admin_id = admin_id
        self.admin_name = admin_name
        self.user_id = None
        self.user_name = None
        self.show_frame("AdminDashboard")

    def start_booking_with_movie(self, movie_id):
        book_frame = self.frames["BookPage"]
        book_frame.preselect_movie(movie_id)
        self.show_frame("BookPage")


# --- Login and Registration logic ---
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.init_widgets()
    
    def init_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12), foreground='#ffffff', background='#D43F52')
        bg = '#181818'
        self.configure(bg=bg)
        
        # Tab section for User/Admin login
        tk.Label(self, text="BookMyShow", font=("Arial Rounded MT Bold", 28), fg="#D43F52", bg=bg).pack(pady=20)
        
        # Tab buttons
        tab_frame = tk.Frame(self, bg=bg)
        tab_frame.pack(pady=10)
        self.user_tab_btn = tk.Button(tab_frame, text="User Login", bg="#47C9AF", fg="white", font=("Arial", 11, "bold"), command=self.show_user_login)
        self.admin_tab_btn = tk.Button(tab_frame, text="Admin Login", bg="#D3D3D3", fg="black", font=("Arial", 11, "bold"), command=self.show_admin_login)
        self.user_tab_btn.pack(side='left', padx=10)
        self.admin_tab_btn.pack(side='left', padx=10)
        
        # Container for login forms
        self.form_frame = tk.Frame(self, bg=bg)
        self.form_frame.pack(pady=20, expand=True)
        
        self.show_user_login()
    
    def clear_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
    
    def show_user_login(self):
        self.clear_form()
        self.user_tab_btn.config(bg="#47C9AF", fg="white")
        self.admin_tab_btn.config(bg="#D3D3D3", fg="black")
        
        tk.Label(self.form_frame, text="User Login", font=("Arial", 16, "bold"), fg="#ECC94B", bg="#181818").pack(pady=10)
        frm = tk.Frame(self.form_frame, bg="#181818")
        frm.pack(pady=8)
        tk.Label(frm, text="Email:", font=("Arial", 12), fg="#fff", bg="#181818").grid(row=0, column=0, sticky='w', pady=5)
        tk.Label(frm, text="Password:", font=("Arial", 12), fg="#fff", bg="#181818").grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(frm, width=28)
        pw_entry = ttk.Entry(frm, width=28, show="*")
        email_entry.grid(row=0, column=1, padx=8)
        pw_entry.grid(row=1, column=1, padx=8)
        
        def try_user_login():
            res = db.user_login(email_entry.get(), pw_entry.get())
            if res:
                self.controller.user_login(res[0], res[1])
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")
        
        ttk.Button(self.form_frame, text="Login", command=try_user_login).pack(pady=8)
        ttk.Button(self.form_frame, text="New user? Register", command=lambda: self.controller.show_frame("RegisterPage")).pack()
    
    def show_admin_login(self):
        self.clear_form()
        self.admin_tab_btn.config(bg="#47C9AF", fg="white")
        self.user_tab_btn.config(bg="#D3D3D3", fg="black")
        
        tk.Label(self.form_frame, text="Admin Login", font=("Arial", 16, "bold"), fg="#ECC94B", bg="#181818").pack(pady=10)
        frm = tk.Frame(self.form_frame, bg="#181818")
        frm.pack(pady=8)
        tk.Label(frm, text="Email:", font=("Arial", 12), fg="#fff", bg="#181818").grid(row=0, column=0, sticky='w', pady=5)
        tk.Label(frm, text="Password:", font=("Arial", 12), fg="#fff", bg="#181818").grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(frm, width=28)
        pw_entry = ttk.Entry(frm, width=28, show="*")
        email_entry.grid(row=0, column=1, padx=8)
        pw_entry.grid(row=1, column=1, padx=8)
        
        def try_admin_login():
            res = db.admin_login(email_entry.get(), pw_entry.get())
            if res:
                self.controller.admin_login(res[0], res[1])
            else:
                messagebox.showerror("Login Failed", "Invalid admin credentials. (admin@bookmyshow.com / admin123)")
        
        ttk.Button(self.form_frame, text="Login", command=try_admin_login).pack(pady=8)
        tk.Label(self.form_frame, text="Default: admin@bookmyshow.com / admin123", fg="#888", bg="#181818", font=("Arial", 9)).pack(pady=4)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#232232")
        tk.Label(self, text="Sign Up", font=("Arial Rounded MT Bold", 26), fg="#ECC94B", bg="#232232").pack(pady=30)
        fields = ['Name', 'Email', 'Phone', 'Password']
        self.entries = {f: ttk.Entry(self, width=30) for f in fields}
        for i, f in enumerate(fields):
            tk.Label(self, text=f+":", bg="#232232", fg="#fff", font=("Arial", 12)).pack()
            self.entries[f].pack(pady=2)
        def try_reg():
            try:
                db.user_register(self.entries['Name'].get(), self.entries['Email'].get(), self.entries['Phone'].get(), self.entries['Password'].get())
                messagebox.showinfo("Registered", "Account created!")
                # Optionally, you can auto-login after registration or show login page
                self.controller.show_frame("LoginPage")
            except Exception as e:
                messagebox.showerror("Registration Failed", str(e))
        ttk.Button(self, text="Register", command=try_reg).pack(pady=8)
        ttk.Button(self, text="Back to Login", command=lambda: self.controller.show_frame("LoginPage")).pack()

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#181818")
        self.init_ui()
    def init_ui(self):
        tk.Label(self, text="Welcome to BookMyShow!", font=("Arial Rounded MT Bold", 24), fg="#D43F52", bg="#181818").pack(pady=25)
        btn_f = tk.Frame(self, bg="#181818")
        btn_f.pack(pady=12)
        ttk.Button(btn_f, text="Book Ticket", command=lambda: self.controller.show_frame("BookPage")).grid(row=0, column=0, padx=6)
        ttk.Button(btn_f, text="My Bookings", command=lambda: self.controller.show_frame("BookingsPage")).grid(row=0, column=1, padx=6)
        ttk.Button(btn_f, text="Profile", command=lambda: self.controller.show_frame("ProfilePage")).grid(row=0, column=2, padx=6)
        ttk.Button(btn_f, text="Claim Loyalty Discount", command=lambda: self.controller.show_frame("ClaimLoyaltyPage")).grid(row=0, column=3, padx=6)
        ttk.Button(self, text="Logout", command=lambda: self.controller.show_frame("LandingPage")).pack(pady=16)
        self.points_label = tk.Label(self, fg="#ECC94B", bg="#181818", font=("Arial", 14))
        self.points_label.pack()
        self.update_points()
    def update_points(self):
        uid = self.controller.user_id
        pts = db.get_user_loyalty(uid)
        disc = db.get_user_discount(uid)
        self.points_label.config(text=f"Loyalty Points: {pts:>3}   Discount: {disc}% (auto at payment)")

class BookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.mv_var = tk.StringVar()
        self.setup()
    def setup(self):
        self.configure(bg="#232232")
        self.title_lbl = tk.Label(self, text="Book a Ticket", font=("Arial Rounded MT Bold", 22), fg="#D43F52", bg="#232232")
        self.title_lbl.pack(pady=18)
        self.mv_menu = ttk.Combobox(self, textvariable=self.mv_var, width=32)
        self.mv_menu.pack()
        self.mv_var.trace('w', self.load_shows)
        self.show_var = tk.StringVar()
        self.show_menu = tk.OptionMenu(self, self.show_var, "")
        self.show_menu.pack()
        self.seat_var = tk.StringVar()
        self.seat_menu = tk.OptionMenu(self, self.seat_var, "")
        self.seat_menu.pack()
        self.pay_amt_e = ttk.Entry(self, width=12)
        self.pay_amt_e.insert(0, "250")
        tk.Label(self, text="Amount (before discount):", bg="#232232", fg="#fff").pack()
        self.pay_amt_e.pack()
        self.pay_mode = tk.StringVar(value="UPI")
        ttk.Combobox(self, textvariable=self.pay_mode, values=["UPI", "Wallet", "Credit Card", "Net Banking"]).pack()
        ttk.Button(self, text="Book Now", command=self.book).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("Dashboard")).pack()
        self.load_movies()
    def load_movies(self):
        movies = db.get_movies()
        self.mv_menu['values'] = [f"{m[0]} - {m[1]}" for m in movies]
        if movies:
            self.mv_var.set(f"{movies[0][0]} - {movies[0][1]}")
    def preselect_movie(self, movie_id):
        movies = db.get_movies()
        for m in movies:
            if str(m[0]) == str(movie_id):
                self.mv_var.set(f"{m[0]} - {m[1]}")
                self.load_shows()
                break
    def load_shows(self, *_):
        movie_id = self.mv_var.get().split()[0]
        shows = db.get_shows_for_movie(movie_id)
        menu = self.show_menu["menu"]
        menu.delete(0, "end")
        if shows:
            for s in shows:
                label = f"ShowID:{s[0]} | {s[4]} {s[5]} | Theatre:{s[3]}"
                menu.add_command(label=label, command=lambda v=s[0]: self.show_var.set(v))
            self.show_var.set(str(shows[0][0]))
        else:
            self.show_var.set('')
        self.load_seats()
    def load_seats(self, *_):
        seats = db.get_seats_for_show(self.show_var.get()) if self.show_var.get() else []
        menu = self.seat_menu["menu"]
        menu.delete(0, "end")
        for sid, sno in seats:
            menu.add_command(label=f"{sno} (ID {sid})", command=lambda v=sid: self.seat_var.set(v))
        if seats: self.seat_var.set(str(seats[0][0]))
        else: self.seat_var.set('')
    def book(self):
        try:
            show_id = int(self.show_var.get())
            seat_id = int(self.seat_var.get())
            amount = float(self.pay_amt_e.get())
            mode = self.pay_mode.get()
            tid = db.book_ticket(self.controller.user_id, show_id, [seat_id], amount, mode)
            messagebox.showinfo("Success", "Booked and paid (discount auto-applied by DB)!")
            self.controller.show_frame("Dashboard")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class BookingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#181818")
        self.refresh()
    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        tk.Label(self, text="My Bookings", font=("Arial Rounded MT Bold", 19), fg="#ECC94B", bg="#181818").pack(pady=11)
        bookings = db.get_my_bookings(self.controller.user_id)
        if not bookings:
            tk.Label(self, text="No bookings", fg="#fff", bg="#181818").pack()
        else:
            for tid, sid, title, status in bookings:
                t = f"Ticket {tid} - {title} (Show {sid}) - {status}"
                tk.Label(self, text=t, fg="#fff", bg="#181818").pack()
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("LandingPage")).pack(pady=7)
    def tkraise(self, aboveThis=None):
        self.refresh()
        super().tkraise(aboveThis)

class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#242424")
        self.update_info()
    def update_info(self):
        for w in self.winfo_children(): w.destroy()
        tk.Label(self, text="My Profile", font=("Arial Rounded MT Bold", 20), fg="#47C9AF", bg="#242424").pack(pady=19)
        uid = self.controller.user_id
        details = db.get_user_details(uid)
        if details:
            info = (
                f"User ID: {details[0]}\n"
                f"Name: {details[1]}\n"
                f"Email: {details[2]}\n"
                f"Phone: {details[3]}\n"
                f"Loyalty Points: {details[4]}"
            )
        else:
            info = "User details not found."
        tk.Label(self, text=info, font=("Arial", 14), fg="#ccc", bg="#242424").pack(pady=10)
        ttk.Button(self, text="Change Password", command=self.change_password_popup).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("LandingPage")).pack(pady=16)
    def tkraise(self, aboveThis=None):
        self.update_info()
        super().tkraise(aboveThis)
    def change_password_popup(self):
        win = tk.Toplevel(self)
        win.title("Change Password")
        win.geometry("320x180")
        win.config(bg="#2a2a34")
        tk.Label(win, text="Create New Password", bg="#2a2a34", fg="#ECC94B").pack(pady=4)
        new_pw = ttk.Entry(win, show="*")
        new_pw.pack(pady=2)
        tk.Label(win, text="Confirm New Password", bg="#2a2a34", fg="#ECC94B").pack(pady=4)
        confirm_pw = ttk.Entry(win, show="*")
        confirm_pw.pack(pady=2)
        def do_change():
            p1 = new_pw.get()
            p2 = confirm_pw.get()
            if p1 != p2 or not p1:
                messagebox.showerror("Error", "Passwords do not match or are empty!")
                return
            db.change_password(self.controller.user_id, p1)
            messagebox.showinfo("Success", "Password changed successfully! Please log in again.")
            win.destroy()
            self.controller.user_id = None
            self.controller.user_name = None
            self.controller.show_frame("LoginPage")
        ttk.Button(win, text="Update Password", command=do_change).pack(pady=8)


class ClaimLoyaltyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#292929")
        self.update_screen()
    def update_screen(self):
        for w in self.winfo_children(): w.destroy()
        tk.Label(self, text="Claim Loyalty Discount", font=("Arial Rounded MT Bold", 19), fg="#ECC94B", bg="#292929").pack(pady=11)
        points = db.get_user_loyalty(self.controller.user_id)
        disc = db.get_user_discount(self.controller.user_id)
        tk.Label(self, text=f"Loyalty Points: {points}\nEligible Discount: {disc}%", font=("Arial", 14), fg="#fff", bg="#292929").pack()
        if points >= 500:
            bookings = db.get_my_bookings(self.controller.user_id)
            eligible = [t for t in bookings if t[3] == 'Pending']
            if eligible:
                tk.Label(self, text="Select Ticket to claim:", bg="#292929", fg="#fff").pack()
                var = tk.StringVar()
                var.set(str(eligible[0][0]))
                options = [f"{t[0]} ({t[2]})" for t in eligible]
                menu = ttk.Combobox(self, textvariable=var, values=options)
                menu.pack()
                def apply_redeem():
                    ticket_id = int(var.get().split()[0])
                    db.redeem_loyalty_discount(self.controller.user_id, ticket_id)
                    messagebox.showinfo("Success", "Discount redeemed and applied to this booking/payment!")
                    self.controller.show_frame("LandingPage")
                ttk.Button(self, text="Redeem", command=apply_redeem).pack(pady=6)
            else:
                tk.Label(self, text="No pending bookings eligible for claim.", bg="#292929", fg="#ecc").pack()
        else:
            tk.Label(self, text="You need at least 500 points to claim.", bg="#292929", fg="#ecc").pack()
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("LandingPage")).pack(pady=9)
    def tkraise(self, aboveThis=None):
        self.update_screen()
        super().tkraise(aboveThis)


class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#1a1a1a")
        self.init_ui()
    
    def init_ui(self):
        # Top bar with admin info
        top_bar = tk.Frame(self, bg="#232232")
        top_bar.pack(fill='x', padx=0, pady=0)
        tk.Label(top_bar, text="🔒 Admin Dashboard", font=("Arial", 18, "bold"), fg="#47C9AF", bg="#232232").pack(side='left', padx=20, pady=12)
        ttk.Button(top_bar, text="Logout", command=self.logout).pack(side='right', padx=20, pady=12)
        
        # Main content scrollable area
        canvas = tk.Canvas(self, bg="#1a1a1a", borderwidth=0, highlightthickness=0)
        scroll_frame = tk.Frame(canvas, bg="#1a1a1a")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind('<Configure>', on_frame_configure)
        
        # Admin welcome
        admin_name = getattr(self.controller, 'admin_name', 'Admin')
        tk.Label(scroll_frame, text=f"Welcome, {admin_name}!", font=("Arial", 16, "bold"), fg="#ECC94B", bg="#1a1a1a").pack(pady=16)
        
        # Filters
        filter_frame = tk.Frame(scroll_frame, bg="#1a1a1a")
        filter_frame.pack(padx=20, pady=10, fill='x')
        
        tk.Label(filter_frame, text="Select City:", fg="#fff", bg="#1a1a1a", font=("Arial", 11)).pack(side='left', padx=8)
        self.city_var = tk.StringVar()
        city_list = db.get_cities()
        self.city_dd = ttk.Combobox(filter_frame, textvariable=self.city_var, values=city_list, state='readonly', width=14)
        self.city_dd.pack(side='left', padx=4)
        self.city_dd.bind("<<ComboboxSelected>>", lambda e: self.load_movies())
        
        tk.Label(filter_frame, text="Select Movie:", fg="#fff", bg="#1a1a1a", font=("Arial", 11)).pack(side='left', padx=8)
        self.movie_var = tk.StringVar()
        self.movie_dd = ttk.Combobox(filter_frame, textvariable=self.movie_var, values=[], state='readonly', width=20)
        self.movie_dd.pack(side='left', padx=4)
        self.movie_dd.bind("<<ComboboxSelected>>", lambda e: self.load_shows())
        
        tk.Label(filter_frame, text="Select Show:", fg="#fff", bg="#1a1a1a", font=("Arial", 11)).pack(side='left', padx=8)
        self.show_var = tk.StringVar()
        self.show_dd = ttk.Combobox(filter_frame, textvariable=self.show_var, values=[], state='readonly', width=25)
        self.show_dd.pack(side='left', padx=4)
        self.show_dd.bind("<<ComboboxSelected>>", lambda e: self.load_earnings())
        
        # Earnings summary
        summary_frame = tk.Frame(scroll_frame, bg="#232232")
        summary_frame.pack(padx=20, pady=12, fill='x')
        tk.Label(summary_frame, text="Total Earnings:", font=("Arial", 12, "bold"), fg="#ECC94B", bg="#232232").pack(anchor='w', padx=12, pady=6)
        self.earnings_label = tk.Label(summary_frame, text="₹0", font=("Arial", 20, "bold"), fg="#47C9AF", bg="#232232")
        self.earnings_label.pack(anchor='w', padx=12, pady=(0, 6))
        
        # User earnings table
        tk.Label(scroll_frame, text="Earnings by User:", font=("Arial", 13, "bold"), fg="#ECC94B", bg="#1a1a1a").pack(anchor='w', padx=20, pady=(16, 8))
        
        # Table frame
        table_frame = tk.Frame(scroll_frame, bg="#1a1a1a")
        table_frame.pack(padx=20, pady=6, fill='both', expand=True)
        
        # Create table with Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background="#2a2a2a", foreground="#fff", fieldbackground="#2a2a2a", font=("Arial", 10))
        style.map('Treeview', background=[('selected', '#47C9AF')])
        
        columns = ('User ID', 'User Name', 'Tickets', 'Amount Paid', 'Loyalty Points')
        self.tree = ttk.Treeview(table_frame, columns=columns, height=15, show='headings')
        
        self.tree.column('User ID', width=60, anchor='center')
        self.tree.column('User Name', width=150, anchor='w')
        self.tree.column('Tickets', width=70, anchor='center')
        self.tree.column('Amount Paid', width=120, anchor='e')
        self.tree.column('Loyalty Points', width=120, anchor='center')
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill='both', expand=True)
        
        # Scrollbar for table
        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=table_scroll.set)
        table_scroll.pack(side='right', fill='y')
        
        # Initialize with first city if available
        if city_list:
            self.city_var.set(city_list[0])
            self.load_movies()
    
    def logout(self):
        """Logout admin and return to landing page."""
        try:
            self.controller.admin_id = None
            self.controller.admin_name = None
            messagebox.showinfo("Logged Out", "Admin has been logged out.")
        except Exception:
            pass
        try:
            self.controller.show_frame("LandingPage")
        except Exception:
            pass
    
    def load_movies(self):
        city = self.city_var.get()
        if not city:
            return
        movies = db.get_movies_by_city(city)
        self.movie_dd['values'] = [f"{m[0]} - {m[1]}" for m in movies]
        self.movie_var.set("")
        self.show_dd['values'] = []
        self.show_var.set("")
        self.earnings_label.config(text="₹0")
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def load_shows(self):
        city = self.city_var.get()
        movie_str = self.movie_var.get()
        if not city or not movie_str:
            return
        try:
            movie_id = int(movie_str.split()[0])
        except:
            return
        shows = db.get_shows_by_movie_city(movie_id, city)
        self.show_dd['values'] = [f"{s[0]} - {s[1]} - {s[2]} {s[3]} (Screen {s[4]})" for s in shows]
        self.show_var.set("")
        self.earnings_label.config(text="₹0")
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def load_earnings(self):
        show_str = self.show_var.get()
        if not show_str:
            return
        try:
            show_id = int(show_str.split()[0])
        except:
            return
        # Fetch total earnings and per-user breakdown from DB
        try:
            total = db.get_total_earnings_for_show(show_id)
            self.earnings_label.config(text=f"₹{total}")
        except Exception:
            self.earnings_label.config(text="₹0")

        # Fill earnings table per user
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            rows = db.get_earnings_by_user_for_show(show_id)
            # rows: (user_id, name, loyalty_points, tickets, total_paid)
            for r in rows:
                uid, name, loyalty, tickets, total_paid = r
                self.tree.insert('', 'end', values=(uid, name, tickets, f"₹{total_paid}", loyalty))
        except Exception:
            pass

    def refresh(self):
        """Refresh admin dashboard when shown: reload cities, reset filters and update earnings view."""
        try:
            # Update city list (in case DB changed)
            city_list = db.get_cities()
            self.city_dd['values'] = city_list
            if city_list:
                # select first city by default
                self.city_var.set(city_list[0])
            else:
                self.city_var.set("")
            # Clear movie/show selections
            self.movie_dd['values'] = []
            self.movie_var.set("")
            self.show_dd['values'] = []
            self.show_var.set("")
            self.earnings_label.config(text="₹0")
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Load movies for selected city
            if self.city_var.get():
                self.load_movies()
        except Exception:
            pass


if __name__ == "__main__":
    # Quick startup for the GUI. Ensure your DB settings in db.py are correct.
    app = BookMyShowApp()
    app.mainloop()