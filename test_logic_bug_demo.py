#!/usr/bin/env python3
"""Demo program with logic bugs (not runtime errors) for testing enhanced analysis"""

import os

def create_empty_file():
    """Logic bug: Creates file but doesn't write any data"""
    filename = "output.txt"
    
    # Bug 1: Opens file but never writes anything
    with open(filename, 'w') as f:
        pass  # Should write data here but doesn't
    
    print(f"File {filename} created successfully")
    return filename

def process_numbers():
    """Logic bug: Wrong calculation logic"""
    numbers = [1, 2, 3, 4, 5]
    
    # Bug 2: Wrong formula - should sum, but does average calculation wrong
    total = sum(numbers)
    average = total / (len(numbers) + 1)  # Bug: should be len(numbers), not +1
    
    print(f"Numbers: {numbers}")
    print(f"Total: {total}")
    print(f"Average: {average}")  # Will show wrong average
    
    return average

def check_file_exists():
    """Logic bug: Checks wrong file"""
    # Bug 3: Looking for wrong filename
    filename = "data.txt"  # Should be "output.txt"
    
    if os.path.exists(filename):
        print(f"✅ Found {filename}")
        return True
    else:
        print(f"❌ File {filename} not found")
        return False

def main():
    """Main function that runs without errors but produces wrong results"""
    print("🚀 Starting program...")
    
    # This will run successfully but create empty file
    output_file = create_empty_file()
    
    # This will run successfully but calculate wrong average
    avg = process_numbers()
    
    # This will run successfully but look for wrong file
    file_found = check_file_exists()
    
    print(f"\n📊 Program completed:")
    print(f"   - Created file: {output_file}")
    print(f"   - Calculated average: {avg}")
    print(f"   - File check result: {file_found}")
    
    # Program exits successfully (exit code 0) but has logical bugs
    print("✅ Program finished successfully (but results are wrong!)")

if __name__ == "__main__":
    main()