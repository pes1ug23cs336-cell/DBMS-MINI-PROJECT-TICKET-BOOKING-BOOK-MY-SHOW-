import mysql.connector
from datetime import datetime, timedelta

def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sathwik",
        database="bookmyshow"
    )

def test_list_all_triggers():
    """List all triggers in the database"""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SHOW TRIGGERS;")
    triggers = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*80)
    print("ALL TRIGGERS IN DATABASE:")
    print("="*80)
    if not triggers:
        print("❌ NO TRIGGERS FOUND!")
        return
    
    for trigger in triggers:
        print(f"Trigger: {trigger[0]}")
        print(f"  Event: {trigger[1]} | Timing: {trigger[2]} | Table: {trigger[3]}")
        print()

def test_trigger_1_duplicate_booking():
    """
    Trigger 1a: Prevent Booking More Than Once for Same Seat-Show
    Test: Try to book same seat twice in same show
    """
    print("\n" + "="*80)
    print("TEST 1: Prevent Booking More Than Once for Same Seat-Show")
    print("="*80)
    
    conn = db_connect()
    cursor = conn.cursor()
    
    # Setup: Get a show and seat
    cursor.execute("""
        SELECT s.show_id, ss.show_seat_id, ss.seat_id 
        FROM ShowTable s
        JOIN ShowSeat ss ON s.show_id = ss.show_id
        WHERE ss.status = 'available'
        LIMIT 1
    """)
    result = cursor.fetchone()
    
    if not result:
        print("❌ No available seats found for testing")
        conn.close()
        return
    
    show_id, show_seat_id, seat_id = result
    user_id = 1  # Assuming user_id 1 exists
    
    print(f"Setup: show_id={show_id}, seat_id={seat_id}, user_id={user_id}")
    
    try:
        # First booking should succeed
        cursor.execute("""
            INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
            VALUES (%s, %s, %s, 'Confirmed', NULL)
        """, (user_id, show_id, seat_id))
        conn.commit()
        print("✅ First booking SUCCEEDED")
        
        # Second booking same seat should fail (trigger should prevent)
        try:
            cursor.execute("""
                INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
                VALUES (%s, %s, %s, 'Confirmed', NULL)
            """, (user_id, show_id, seat_id))
            conn.commit()
            print("❌ Second booking SUCCEEDED (TRIGGER FAILED - should have been blocked)")
        except mysql.connector.Error as e:
            if "duplicate" in str(e).lower() or "already" in str(e).lower():
                print("✅ Second booking BLOCKED by trigger (correct)")
            else:
                print(f"⚠️  Second booking error: {e}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        conn.close()

def test_trigger_1b_loyalty_points():
    """
    Trigger 1b: Auto-Update Loyalty Points on Payment Success (50 rupees = 1 point)
    Test: Create a payment and check if loyalty points increased
    """
    print("\n" + "="*80)
    print("TEST 1b: Auto-Update Loyalty Points on Payment Success")
    print("="*80)
    
    conn = db_connect()
    cursor = conn.cursor()
    
    # Setup: Get user and their current loyalty points
    cursor.execute("SELECT user_id, loyalty_points FROM User WHERE user_id = 1")
    result = cursor.fetchone()
    
    if not result:
        print("❌ User not found")
        conn.close()
        return
    
    user_id, initial_points = result
    print(f"Setup: user_id={user_id}, initial_loyalty_points={initial_points}")
    
    # Get or create a ticket
    cursor.execute("""
        SELECT ticket_id FROM Ticket WHERE user_id = %s LIMIT 1
    """, (user_id,))
    ticket_result = cursor.fetchone()
    
    if ticket_result:
        ticket_id = ticket_result[0]
        print(f"Using existing ticket_id={ticket_id}")
    else:
        # Create a test ticket
        cursor.execute("""
            SELECT show_id, seat_id FROM Ticket LIMIT 1
        """)
        show_result = cursor.fetchone()
        if show_result:
            show_id, seat_id = show_result
        else:
            print("❌ No show/seat data found")
            conn.close()
            return
        
        cursor.execute("""
            INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
            VALUES (%s, %s, %s, 'Confirmed', NULL)
        """, (user_id, show_id, seat_id))
        ticket_id = cursor.lastrowid
        conn.commit()
    
    try:
        # Create a payment with amount that should add points (e.g., 500 = 10 points)
        amount = 500
        expected_points = amount // 50  # 500/50 = 10 points
        
        cursor.execute("""
            INSERT INTO Payment (ticket_id, amount, mode, status)
            VALUES (%s, %s, 'UPI', 'Success')
        """, (ticket_id, amount))
        conn.commit()
        print(f"✅ Payment created: amount={amount}, expected_points={expected_points}")
        
        # Check updated loyalty points
        cursor.execute("SELECT loyalty_points FROM User WHERE user_id = %s", (user_id,))
        updated_result = cursor.fetchone()
        updated_points = updated_result[0]
        
        if updated_points > initial_points:
            points_added = updated_points - initial_points
            print(f"✅ Loyalty points updated: {initial_points} → {updated_points} (+{points_added})")
            if points_added == expected_points:
                print("✅ Points calculation CORRECT")
            else:
                print(f"⚠️  Points mismatch: expected +{expected_points}, got +{points_added}")
        else:
            print(f"❌ Loyalty points NOT updated: {initial_points} → {updated_points}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        conn.close()

def test_trigger_1d_ticket_status():
    """
    Trigger 1d: Update Ticket Status to Confirmed on Payment Success
    Test: Check if ticket status changes when payment succeeds
    """
    print("\n" + "="*80)
    print("TEST 1d: Update Ticket Status to Confirmed on Payment Success")
    print("="*80)
    
    conn = db_connect()
    cursor = conn.cursor()
    
    try:
        # Create a test ticket with Pending status
        cursor.execute("""
            SELECT show_id FROM ShowTable LIMIT 1
        """)
        show_result = cursor.fetchone()
        if not show_result:
            print("❌ No show found")
            conn.close()
            return
        
        show_id = show_result[0]
        
        cursor.execute("""
            INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
            VALUES (1, %s, 1, 'Pending', NULL)
        """, (show_id,))
        ticket_id = cursor.lastrowid
        conn.commit()
        
        print(f"Created ticket_id={ticket_id} with status='Pending'")
        
        # Create payment for this ticket
        cursor.execute("""
            INSERT INTO Payment (ticket_id, amount, mode, status)
            VALUES (%s, 500, 'UPI', 'Success')
        """, (ticket_id,))
        conn.commit()
        
        # Check ticket status after payment
        cursor.execute("SELECT status FROM Ticket WHERE ticket_id = %s", (ticket_id,))
        status_result = cursor.fetchone()
        final_status = status_result[0]
        
        if final_status == 'Confirmed':
            print(f"✅ Ticket status updated to 'Confirmed' on payment success")
        else:
            print(f"❌ Ticket status NOT updated: still '{final_status}'")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        conn.close()

def test_trigger_1e_cancelled_payment():
    """
    Trigger 1e: Prevent Payment for Cancelled Tickets
    Test: Try to create payment for cancelled ticket
    """
    print("\n" + "="*80)
    print("TEST 1e: Prevent Payment for Cancelled Tickets")
    print("="*80)
    
    conn = db_connect()
    cursor = conn.cursor()
    
    try:
        # Get or create a cancelled ticket
        cursor.execute("""
            SELECT ticket_id FROM Ticket WHERE status = 'Cancelled' LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            ticket_id = result[0]
            print(f"Using existing cancelled ticket_id={ticket_id}")
        else:
            # Create a cancelled ticket
            cursor.execute("""
                SELECT show_id FROM ShowTable LIMIT 1
            """)
            show_result = cursor.fetchone()
            if not show_result:
                print("❌ No show found")
                conn.close()
                return
            
            show_id = show_result[0]
            cursor.execute("""
                INSERT INTO Ticket (user_id, show_id, seat_id, status, qr_code)
                VALUES (1, %s, 1, 'Cancelled', NULL)
            """, (show_id,))
            ticket_id = cursor.lastrowid
            conn.commit()
            print(f"Created cancelled ticket_id={ticket_id}")
        
        # Try to create payment for cancelled ticket (should fail)
        try:
            cursor.execute("""
                INSERT INTO Payment (ticket_id, amount, mode, status)
                VALUES (%s, 500, 'UPI', 'Success')
            """, (ticket_id,))
            conn.commit()
            print("❌ Payment for CANCELLED ticket SUCCEEDED (TRIGGER FAILED)")
        except mysql.connector.Error as e:
            print(f"✅ Payment for cancelled ticket BLOCKED by trigger: {e}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        conn.close()

def main():
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "TRIGGER VERIFICATION TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # First, list all triggers
    test_list_all_triggers()
    
    # Run individual tests
    test_trigger_1_duplicate_booking()
    test_trigger_1b_loyalty_points()
    test_trigger_1d_ticket_status()
    test_trigger_1e_cancelled_payment()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
