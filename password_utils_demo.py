from password_utils import hash_password, verify_password

# Simulate a user choosing a password during registration
plain_password = "correcthorsebatterystaple"

# What we would store in users.password_hash:
stored_hash = hash_password(plain_password)
print("Simulated stored password_hash value:")
print(stored_hash)
print()

# Now simulate login: user types a password

print("Check with CORRECT password:",
      verify_password(stored_hash, "correcthorsebatterystaple"))

print("Check with WRONG password:",
      verify_password(stored_hash, "wrongpassword"))