# BookMyShow Mini Project - Quick Start Guide

## 🚀 30-Second Setup

### 1. Install Requirements
```bash
pip install mysql-connector-python pillow
```

### 2. Start the App
```bash
python gui.py
```

### 3. First Time Usage

#### **As a Regular User**
1. Click "User Login" tab
2. Click "New user? Register"
3. Fill in: Name, Email, Phone, Password
4. Click "Register"
5. Go back to login and enter your credentials
6. Select city → browse movies → select show
7. Click on movie poster or "Book" button
8. Select seats (max 6) → click "Pay & Confirm"
9. Choose payment mode → confirm payment
10. See booking confirmation with ticket details

#### **As Admin**
1. Click "Admin Login" tab
2. Enter:
   - Email: `admin@bookmyshow.com`
   - Password: `admin123`
3. Click "Login"
4. You'll see the Admin Dashboard
5. Select **City** → **Movie** → **Show**
6. View total earnings and user-wise breakdown

---

## 🎯 Main Features to Try

### Feature 1: Book Tickets
- Select seats visually
- 2-minute payment window with countdown
- Real-time seat availability (refreshes every 5 seconds)

### Feature 2: Double-Booking Prevention
- Open two browsers/windows with different users
- Have User A start booking seat X
- Switch to User B's window
- Seat X shows as "Booked/Reserved" (gray, unclickable)

### Feature 3: Payment Timeout
- Start payment for seats
- Don't click "Confirm & Pay"
- Wait 120 seconds
- See auto-timeout message
- Seats released back to other users

### Feature 4: Loyalty Points
- Book with amount ≥500 rupees
- Check your profile → loyalty points increased by 10 × (amount/50)
- With 500+ points, get automatic discount at checkout

### Feature 5: Admin Analytics
- Login as admin
- Filter by City → Movie → Show
- See total earnings in big numbers
- View breakdown by user with spending & loyalty points

---

## 🧪 Testing Checklist

After starting the app, verify these:

- [ ] Can register new user
- [ ] Can login as user
- [ ] Movies appear by city
- [ ] Seat grid displays with colors
- [ ] Can select 1-6 seats
- [ ] Payment modal shows 2-minute countdown
- [ ] Payment modes available (UPI, Wallet, Credit Card, Net Banking)
- [ ] Can confirm payment
- [ ] Booking confirmation appears
- [ ] Loyalty points increase after booking
- [ ] Can login as admin
- [ ] Admin dashboard loads
- [ ] Admin can filter city → movie → show
- [ ] Earnings table shows users & amounts

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database connection error" | Ensure MySQL is running and credentials in db.py are correct |
| App won't start | Check Python version (3.7+) and install requirements |
| Admin login fails | Use exact credentials: admin@bookmyshow.com / admin123 |
| No cities appear | Check if Theatre table has data in DB |
| Seats don't update | Refresh might take 5 seconds; wait and check again |
| Payment timeout | Normal behavior; seats auto-release after 120s |

---

## 📱 UI Navigation

```
Landing Page (Home)
├── Search Movies by Title
├── Filter by City & Theatre
├── View Trending Movies
└── View All Movies

Movie Detail Page
├── Movie Info (Rating, Genre, Duration)
└── Show Times by Theatre

Booking Window
├── Seat Selection Grid
├── Price Display
└── Pay & Confirm Button

Payment Modal
├── Movie & Theatre Details
├── Selected Seats List
├── 2-Minute Countdown Timer
├── Loyalty Discount (if eligible)
├── Payment Mode Selection
├── Confirm & Cancel Buttons

Confirmation Page
├── Ticket ID
├── Booking Details
└── Back to Home Button

User Dashboard
├── My Bookings
├── My Profile
├── Loyalty Points
└── Claim Loyalty Discount

Admin Dashboard
├── City Filter
├── Movie Filter
├── Show Filter
├── Total Earnings Display
└── User Earnings Table
```

---

## 🔐 Test Accounts

### Existing Test Users (may vary based on your DB)
- Any registered user account

### Admin Account
- **Email**: admin@bookmyshow.com
- **Password**: admin123

---

## 🎨 Color Code Reference

| Color | Meaning |
|-------|---------|
| **Green (#90EE90)** | Seat available |
| **Gold (#FFD700)** | Seat selected by you |
| **Gray (#D3D3D3)** | Seat booked or reserved |
| **Cyan (#47C9AF)** | Active/highlight (buttons) |
| **Red (#D43F52)** | Important/error |
| **Yellow (#ECC94B)** | Labels/headers |

---

## 💡 Tips & Tricks

1. **Real-time seat updates**: If you have two browser windows open, seat reservations appear in real-time
2. **Quick booking**: Select seats, confirm payment before 2-minute timer runs out
3. **Loyalty tracking**: Check "My Profile" to see current loyalty points
4. **Admin insights**: View earnings by show to understand booking patterns
5. **Payment modes**: Choose your preferred payment method at confirmation

---

## 📊 Example Data Flow

```
User Selects Seats (UI)
        ↓
Creates Pending Tickets (DB)
        ↓
Marks ShowSeat as 'reserved' (DB)
        ↓
Opens Payment Modal with 2-min countdown (UI)
        ↓
User Clicks "Confirm & Pay" (UI)
        ↓
Calls finalize_payment_for_tickets() (DB)
        ↓
Inserts Payment Record (DB)
        ↓
Updates Tickets to 'Confirmed' (DB)
        ↓
Marks ShowSeat as 'booked' (DB)
        ↓
Shows Confirmation Page (UI)
        ↓
BOOKING COMPLETE ✓
```

---

## 🚨 If Timer Expires

```
2-Minute Timer Runs Out
        ↓
Auto-calls cancel_tickets() (DB)
        ↓
Marks Tickets as 'Cancelled' (DB)
        ↓
Releases ShowSeat to 'available' (DB)
        ↓
Shows "Payment Timed Out" Message (UI)
        ↓
Seats available for other users after refresh
        ↓
BOOKING CANCELLED
```

---

**Ready to book? Start the app and enjoy! 🎉**
