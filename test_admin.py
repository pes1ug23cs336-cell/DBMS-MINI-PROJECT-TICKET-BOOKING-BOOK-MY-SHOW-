#!/usr/bin/env python3
"""Quick test script for admin functionality"""
import db

print("=" * 80)
print("Testing Admin Functions")
print("=" * 80)

# Test 1: Admin login
print("\n1. Testing admin_login:")
result = db.admin_login("admin@bookmyshow.com", "admin123")
print(f"   Login result: {result}")

# Test 2: Get cities
print("\n2. Testing get_cities:")
cities = db.get_cities()
print(f"   Cities: {cities}")

if cities:
    city = cities[0]
    print(f"\n3. Testing get_movies_by_city ({city}):")
    movies = db.get_movies_by_city(city)
    print(f"   Movies: {movies[:3]}")  # Show first 3
    
    if movies:
        movie_id = movies[0][0]
        print(f"\n4. Testing get_shows_by_movie_city (movie={movie_id}, city={city}):")
        shows = db.get_shows_by_movie_city(movie_id, city)
        print(f"   Shows: {shows[:3]}")  # Show first 3
        
        if shows:
            show_id = shows[0][0]
            print(f"\n5. Testing get_total_earnings_for_show (show={show_id}):")
            total = db.get_total_earnings_for_show(show_id)
            print(f"   Total earnings: ₹{total}")
            
            print(f"\n6. Testing get_earnings_by_user_for_show (show={show_id}):")
            user_earnings = db.get_earnings_by_user_for_show(show_id)
            print(f"   User earnings count: {len(user_earnings)}")
            if user_earnings:
                for user in user_earnings[:3]:  # Show first 3
                    print(f"     - {user[1]}: ₹{user[4]} ({user[2]} loyalty points, {user[3]} tickets)")

print("\n" + "=" * 80)
print("All tests completed!")
print("=" * 80)
