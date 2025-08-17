#!/usr/bin/env python3
"""
Test script to create sample binary protobuf files for testing the decoder.
"""

import subprocess
import tempfile
import os
from pathlib import Path

def create_test_data():
    """Create test binary protobuf files using the example proto."""
    
    # First, compile the proto file
    print("Compiling example.proto...")
    try:
        result = subprocess.run([
            'protoc',
            '--python_out=.',
            'example.proto'
        ], capture_output=True, text=True, check=True)
        print("✓ Proto file compiled successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to compile proto file: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ protoc not found. Please install Protocol Buffers compiler.")
        return False
    
    # Now create test data
    try:
        # Import the generated module
        import example_pb2
        
        # Create a Person message
        person = example_pb2.Person()
        person.name = "John Doe"
        person.age = 30
        person.email = "john.doe@example.com"
        person.hobbies.extend(["reading", "hiking", "coding"])
        person.gender = example_pb2.Person.Gender.MALE
        
        # Create an AddressBook message
        address_book = example_pb2.AddressBook()
        address_book.title = "My Contacts"
        address_book.created_date = "2024-01-15"
        address_book.people.append(person)
        
        # Add another person
        person2 = example_pb2.Person()
        person2.name = "Jane Smith"
        person2.age = 25
        person2.email = "jane.smith@example.com"
        person2.hobbies.extend(["painting", "yoga"])
        person2.gender = example_pb2.Person.Gender.FEMALE
        address_book.people.append(person2)
        
        # Create a SimpleMessage
        simple_msg = example_pb2.SimpleMessage()
        simple_msg.content = "Hello, this is a test message!"
        simple_msg.timestamp = 1705315200  # 2024-01-15 00:00:00 UTC
        simple_msg.is_important = True
        
        # Write binary files
        with open('test_person.binpb', 'wb') as f:
            f.write(person.SerializeToString())
        print("✓ Created test_person.binpb")
        
        with open('test_addressbook.binpb', 'wb') as f:
            f.write(address_book.SerializeToString())
        print("✓ Created test_addressbook.binpb")
        
        with open('test_simple.binpb', 'wb') as f:
            f.write(simple_msg.SerializeToString())
        print("✓ Created test_simple.binpb")
        
        # Clean up generated Python files
        os.remove('example_pb2.py')
        print("✓ Cleaned up generated Python files")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import generated module: {e}")
        return False
    except Exception as e:
        print(f"✗ Error creating test data: {e}")
        return False

if __name__ == '__main__':
    print("Creating test binary protobuf files...")
    if create_test_data():
        print("\n✓ Test data created successfully!")
        print("\nYou can now test the decoder with:")
        print("  python binpb_decoder_advanced.py . test_person.binpb")
        print("  python binpb_decoder_advanced.py . test_addressbook.binpb")
        print("  python binpb_decoder_advanced.py . test_simple.binpb")
        print("\nOr list available message types:")
        print("  python binpb_decoder_advanced.py . test_person.binpb -l")
    else:
        print("\n✗ Failed to create test data.")
        sys.exit(1)
