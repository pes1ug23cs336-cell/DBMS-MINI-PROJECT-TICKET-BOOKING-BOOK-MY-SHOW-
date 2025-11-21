import mysql.connector

def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sathwik",
        database="bookmyshow"
    )

def user_login(email, password):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name FROM User WHERE email=%s AND password=%s", (email, password))
    result = cursor.fetchone()
    conn.close()
    return result  # (user_id, user_name)

def user_register(name, email, phone, password):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO User (name, email, phone_no, password) VALUES (%s, %s, %s, %s)", (name, email, phone, password))
    conn.commit()
    conn.close()
    return True

def get_movies():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title FROM Movie")
    results = cursor.fetchall()
    conn.close()
    return results

def get_trending_movies():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, rating FROM Movie ORDER BY rating DESC LIMIT 4")
    results = cursor.fetchall()
    conn.close()
    return results  # (movie_id, title, rating)

def get_user_details(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, phone_no, loyalty_points FROM User WHERE user_id = %s", (user_id,))
    details = cursor.fetchone()
    conn.close()
    return details

def get_theatres():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT theatre_id, name, city, address, contact_no FROM Theatre")
    rows = cursor.fetchall()
    conn.close()
    return rows  # Now each row has 5 columns!


def get_screens():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT screen_id, theatre_id FROM Screen ORDER BY screen_id")
    rows = cursor.fetchall()
    conn.close()
    return rows  # [(screen_id, theatre_id), ...]

def get_movies_in_screens(screen_ids):
    if not screen_ids:
        return []
    conn = db_connect()
    cursor = conn.cursor()
    # Build SQL safely (careful for large lists)
    placeholders = ",".join(str(int(s)) for s in screen_ids)
    cursor.execute(f"SELECT DISTINCT movie_id FROM ShowTable WHERE screen_id IN ({placeholders})")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]



def get_movies_by_theatre(theatre_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.movie_id, m.title, m.genre, m.language, m.duration, m.release_date, m.rating,
               s.theatre_id, t.name, st.show_date, st.start_time
        FROM ShowTable st
        JOIN Movie m ON st.movie_id = m.movie_id
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE s.theatre_id = %s
        ORDER BY m.title, st.show_date, st.start_time
    """, (theatre_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_movie_details(movie_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT title, genre, language, duration, release_date FROM Movie WHERE movie_id = %s", (movie_id,))
    data = cursor.fetchone()
    conn.close()
    return data  # (title, genre, language, duration, release_date)

def get_movie_showtimes(movie_id, city):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name, s.screen_no, st.show_date, st.start_time, st.show_id
        FROM ShowTable st
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE st.movie_id = %s AND t.city = %s
        ORDER BY t.name, s.screen_no, st.show_date, st.start_time
    """, (movie_id, city))
    rows = cursor.fetchall()
    conn.close()
    return rows  # [(theatre, screen_no, show_date, start_time, show_id), ...]

def get_movies_by_theatre_with_screens(theatre_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.title, s.screen_no, st.show_date, st.start_time, st.show_id
        FROM ShowTable st
        JOIN Movie m ON st.movie_id = m.movie_id
        JOIN Screen s ON st.screen_id = s.screen_id
        WHERE s.theatre_id = %s
        ORDER BY m.title, s.screen_no, st.show_date, st.start_time
    """, (theatre_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows





def change_password(user_id, new_password):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE User SET password=%s WHERE user_id=%s", (new_password, user_id))
    conn.commit()
    conn.close()

def get_shows_for_movie(movie_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT st.show_id, s.screen_id, t.theatre_id, t.name, st.show_date, st.start_time
        FROM ShowTable st
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE st.movie_id = %s
    """, (movie_id,))
    shows = cursor.fetchall()
    conn.close()
    return shows

def get_shows_today():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT st.show_id, m.title, t.name, st.show_date, st.start_time
        FROM ShowTable st
        JOIN Movie m ON st.movie_id = m.movie_id
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE st.show_date = CURDATE()
    """)
    shows = cursor.fetchall()
    conn.close()
    return shows

def get_seats_for_show(show_id):
    # Return available seats for a show using ShowSeat status
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.show_seat_id, s.seat_no
        FROM ShowSeat ss
        JOIN Seat s ON ss.seat_id = s.seat_id
        WHERE ss.show_id = %s AND ss.status <> 'booked'
        ORDER BY s.seat_no
    """, (show_id,))
    seats = cursor.fetchall()
    conn.close()
    return seats

def get_seat_data(show_id):
    conn = db_connect()  # your connection function
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.show_seat_id, s.seat_no, s.seat_type, s.price, ss.status
        FROM ShowSeat ss
        JOIN seat s ON ss.seat_id = s.seat_id
        WHERE ss.show_id = %s
        ORDER BY FIELD(s.seat_type,'Regular','Gold','Platinum'), s.seat_no
    """, (show_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def book_seats(user_id, show_id, selected_show_seat_ids, total_price, mode='UPI'):
    # Atomic booking for multiple seats with transaction and availability check
    conn = db_connect()
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        # Lock the selected ShowSeat rows
        format_strings = ','.join(['%s'] * len(selected_show_seat_ids))
        cursor.execute(f"SELECT show_seat_id, status FROM ShowSeat WHERE show_seat_id IN ({format_strings}) FOR UPDATE", tuple(selected_show_seat_ids))
        rows = cursor.fetchall()
        # Ensure none are already booked
        for _id, status in rows:
            if status == 'booked':
                conn.rollback()
                raise Exception('One or more selected seats are already booked.')

        # Insert one ticket row per seat (Ticket requires seat_id)
        ticket_id = None
        ticket_ids = []
        for ssid in selected_show_seat_ids:
            # get underlying seat_id
            cursor.execute("SELECT seat_id FROM ShowSeat WHERE show_seat_id = %s", (ssid,))
            r = cursor.fetchone()
            seat_id = r[0] if r else None
            # qr_code is nullable; set to NULL (will be generated later on ticket confirmation)
            cursor.execute("""
                INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
                VALUES (%s, %s, %s, 'Confirmed', NULL)
            """, (user_id, show_id, seat_id))
            tid = cursor.lastrowid
            ticket_ids.append(tid)
            if ticket_id is None:
                ticket_id = tid

        # Mark seats as booked
        cursor.execute(f"UPDATE ShowSeat SET status='booked' WHERE show_seat_id IN ({format_strings})", tuple(selected_show_seat_ids))

        # Insert payment record (associate with first ticket_id)
        cursor.execute("""
            INSERT INTO payment (ticket_id, amount, mode, status)
            VALUES (%s, %s, %s, 'Success')
        """, (ticket_id, total_price, mode))

        conn.commit()
        return ticket_id
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def book_ticket(user_id, show_id, selected_show_seat_ids, total_price=0, mode='UPI'):
    """Book ticket with multiple seats (show_seat_ids from ShowSeat table)"""
    # Use transactional booking with availability check
    if not selected_show_seat_ids:
        raise ValueError('No seats provided to book.')
    conn = db_connect()
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        # Lock and check availability
        format_strings = ','.join(['%s'] * len(selected_show_seat_ids))
        cursor.execute(f"SELECT show_seat_id, status FROM ShowSeat WHERE show_seat_id IN ({format_strings}) FOR UPDATE", tuple(selected_show_seat_ids))
        rows = cursor.fetchall()
        for _id, status in rows:
            if status == 'booked':
                conn.rollback()
                raise Exception('One or more seats already booked.')

        # Insert one ticket row per selected seat (Ticket requires seat_id)
        ticket_id = None
        ticket_ids = []
        for ssid in selected_show_seat_ids:
            cursor.execute("SELECT seat_id FROM ShowSeat WHERE show_seat_id = %s", (ssid,))
            r = cursor.fetchone()
            seat_id = r[0] if r else None
            # qr_code is nullable; set to NULL (will be generated later on ticket confirmation)
            cursor.execute("""
                INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
                VALUES (%s, %s, %s, 'Confirmed', NULL)
            """, (user_id, show_id, seat_id))
            tid = cursor.lastrowid
            ticket_ids.append(tid)
            if ticket_id is None:
                ticket_id = tid

        # Mark seats booked
        cursor.execute(f"UPDATE ShowSeat SET status='booked' WHERE show_seat_id IN ({format_strings})", tuple(selected_show_seat_ids))

        # Insert payment record (associate with first ticket_id)
        cursor.execute("""
            INSERT INTO payment (ticket_id, amount, mode, status)
            VALUES (%s, %s, %s, 'Success')
        """, (ticket_id, total_price, mode))

        conn.commit()
        return ticket_id
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()

def get_user_total_confirmed_bookings(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ticket WHERE user_id = %s AND status = 'Confirmed'", (user_id,))
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 0

def get_available_seats_for_show(show_id):
    # returns list of (show_seat_id, seat_no) for seats not booked
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.show_seat_id, s.seat_no
        FROM ShowSeat ss
        JOIN Seat s ON ss.seat_id = s.seat_id
        WHERE ss.show_id = %s AND ss.status <> 'booked'
        ORDER BY s.seat_no
    """, (show_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_total_earnings_for_show(show_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(p.amount),0) FROM payment p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.show_id = %s AND p.status = 'Success'
    """, (show_id,))
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 0

def make_payment(ticket_id, amount, mode):
    conn = db_connect()
    cursor = conn.cursor()
    query = "INSERT INTO payment (ticket_id, amount, mode, status) VALUES (%s, %s, %s, 'Success')"
    cursor.execute(query, (ticket_id, amount, mode))
    conn.commit()
    conn.close()


def create_pending_tickets(user_id, show_id, selected_show_seat_ids):
    """Create Ticket rows with status 'Pending' and reserve ShowSeat rows.
    Returns list of created ticket_ids.
    """
    if not selected_show_seat_ids:
        raise ValueError('No seats provided to create pending tickets.')
    conn = db_connect()
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        ticket_ids = []
        for ssid in selected_show_seat_ids:
            cursor.execute("SELECT seat_id FROM ShowSeat WHERE show_seat_id = %s FOR UPDATE", (ssid,))
            r = cursor.fetchone()
            seat_id = r[0] if r else None
            # Ensure seat is not already booked
            cursor.execute("SELECT status FROM ShowSeat WHERE show_seat_id = %s", (ssid,))
            status_row = cursor.fetchone()
            if status_row and status_row[0] == 'booked':
                conn.rollback()
                raise Exception('One or more seats already booked.')
            # Insert pending ticket
            cursor.execute("""
                INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
                VALUES (%s, %s, %s, 'Pending', NULL)
            """, (user_id, show_id, seat_id))
            ticket_ids.append(cursor.lastrowid)

        # Mark show seats as reserved
        format_strings = ','.join(['%s'] * len(selected_show_seat_ids))
        cursor.execute(f"UPDATE ShowSeat SET status='reserved' WHERE show_seat_id IN ({format_strings})", tuple(selected_show_seat_ids))

        conn.commit()
        return ticket_ids
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def cancel_tickets(ticket_ids):
    """Mark given tickets as 'Cancelled' and release reserved seats back to 'available'."""
    if not ticket_ids:
        return
    conn = db_connect()

    try:
        conn.start_transaction()
        cursor = conn.cursor()
        format_strings = ','.join(['%s'] * len(ticket_ids))
        # Get mapping of ticket -> show_id, seat_id
        cursor.execute(f"SELECT ticket_id, show_id, seat_id FROM Ticket WHERE ticket_id IN ({format_strings})", tuple(ticket_ids))
        rows = cursor.fetchall()
        # Update tickets to Cancelled
        cursor.execute(f"UPDATE Ticket SET status='Cancelled' WHERE ticket_id IN ({format_strings})", tuple(ticket_ids))
        # Release corresponding ShowSeat rows
        for tid, show_id, seat_id in rows:
            cursor.execute(
                "UPDATE ShowSeat SET status='available' WHERE show_id = %s AND seat_id = %s AND status = 'reserved'",
                (show_id, seat_id)
            )
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()



def finalize_payment_for_tickets(ticket_ids, amount, mode):
    """Finalize payment for a group of tickets. Inserts a single payment row associated with the first ticket_id,
    sets all tickets to 'Confirmed', and marks corresponding ShowSeat rows as 'booked'.
    Returns payment_id.
    """
    if not ticket_ids:
        raise ValueError('No ticket IDs provided for finalizing payment')
    conn = db_connect()
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        primary_ticket = ticket_ids[0]
        # Insert payment referencing first ticket
        cursor.execute("INSERT INTO payment (ticket_id, amount, mode, status) VALUES (%s, %s, %s, 'Success')", (primary_ticket, amount, mode))
        payment_id = cursor.lastrowid

        # Update tickets to Confirmed
        format_strings = ','.join(['%s'] * len(ticket_ids))
        cursor.execute(f"UPDATE Ticket SET status='Confirmed' WHERE ticket_id IN ({format_strings})", tuple(ticket_ids))

        # Mark corresponding ShowSeat rows as booked
        cursor.execute(f"SELECT show_id, seat_id FROM Ticket WHERE ticket_id IN ({format_strings})", tuple(ticket_ids))
        rows = cursor.fetchall()
        for show_id, seat_id in rows:
            cursor.execute("UPDATE ShowSeat SET status='booked' WHERE show_id = %s AND seat_id = %s AND status IN ('reserved','available')", (show_id, seat_id))

        conn.commit()
        return payment_id
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()

def get_user_loyalty(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT loyalty_points FROM User WHERE user_id = %s", (user_id,))
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 0

def redeem_loyalty_discount(user_id, ticket_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.callproc('redeem_loyalty_discount', [user_id, ticket_id])
    conn.commit()
    conn.close()

def get_user_discount(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT calc_user_discount(%s)", (user_id,))
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 0

def get_movies_with_rating():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, rating FROM Movie")
    results = cursor.fetchall()
    conn.close()
    return results

def get_my_bookings(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Ticket.ticket_id, ShowTable.show_id, Movie.title, Ticket.status
        FROM Ticket
        JOIN ShowTable ON Ticket.show_id = ShowTable.show_id
        JOIN Movie ON ShowTable.movie_id = Movie.movie_id
        WHERE Ticket.user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def admin_login(email, password):
    """Admin login backed by an Admin table.

    This function ensures the Admin table exists (and inserts a default
    admin row if the table is empty). It then checks credentials against
    the Admin table. Returns a tuple similar to other login functions
    ("admin", admin_name) on success, or None on failure.
    """
    # Ensure table exists and a default admin is present
    def ensure_admin_table_exists():
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Admin (
                admin_id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        conn.commit()
        # If no admin rows, insert a default admin (email: admin@bookmyshow.com, password: admin123)
        cursor.execute("SELECT COUNT(*) FROM Admin")
        cnt = cursor.fetchone()[0]
        if cnt == 0:
            cursor.execute(
                "INSERT INTO Admin (email, password, name) VALUES (%s, %s, %s)",
                ("admin@bookmyshow.com", "admin123", "BookMyShow Admin")
            )
            conn.commit()
        conn.close()

    ensure_admin_table_exists()

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, name FROM Admin WHERE email=%s AND password=%s", (email, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        # return (admin_id, admin_name) so controller can set admin context
        return (row[0], row[1])
    return None


def get_cities():
    """Get all unique cities from theatres"""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM Theatre ORDER BY city")
    cities = cursor.fetchall()
    conn.close()
    return [c[0] for c in cities]


def get_movies_by_city(city):
    """Get all movies showing in a city"""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT m.movie_id, m.title
        FROM Movie m
        JOIN ShowTable st ON m.movie_id = st.movie_id
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE t.city = %s
        ORDER BY m.title
    """, (city,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_shows_by_movie_city(movie_id, city):
    """Get all shows for a movie in a city"""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT st.show_id, t.name, st.show_date, st.start_time, s.screen_no
        FROM ShowTable st
        JOIN Screen s ON st.screen_id = s.screen_id
        JOIN Theatre t ON s.theatre_id = t.theatre_id
        WHERE st.movie_id = %s AND t.city = %s
        ORDER BY st.show_date, st.start_time
    """, (movie_id, city))
    results = cursor.fetchall()
    conn.close()
    return results


def get_total_earnings_for_show(show_id):
    """Get total earnings for a show"""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(p.amount),0) FROM payment p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.show_id = %s AND p.status = 'Success'
    """, (show_id,))
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 0


def get_earnings_by_user_for_show(show_id):
    """Get earnings breakdown by user for a show"""
    conn = db_connect()
    cursor = conn.cursor()
    # Count all confirmed tickets for the user for the show, and sum payments
    # made for that user's tickets (payments reference one ticket per booking).
    cursor.execute("""
        SELECT u.user_id, u.name, u.loyalty_points,
               COUNT(DISTINCT t.ticket_id) AS tickets,
               IFNULL(paid.total_paid, 0) AS total_paid
        FROM `User` u
        JOIN `Ticket` t ON u.user_id = t.user_id AND t.show_id = %s AND t.status = 'Confirmed'
        LEFT JOIN (
            SELECT t2.user_id, SUM(p2.amount) AS total_paid
            FROM `Ticket` t2
            JOIN `payment` p2 ON p2.ticket_id = t2.ticket_id AND p2.status = 'Success'
            WHERE t2.show_id = %s
            GROUP BY t2.user_id
        ) paid ON paid.user_id = u.user_id
        GROUP BY u.user_id, u.name, u.loyalty_points
        ORDER BY total_paid DESC
    """, (show_id, show_id))
    results = cursor.fetchall()
    conn.close()
    return results