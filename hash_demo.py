from werkzeug.security import generate_password_hash, check_password_hash

password = "correcthorsebatterystaple"

# Create a hash of the password
password_hash = generate_password_hash(password)
print("Stored hash:")
print(password_hash)
print()

# Try verifying with the correct password
is_correct = check_password_hash(password_hash, "correcthorsebatterystaple")
print("Check with CORRECT password:", is_correct)

# Try verifying with a wrong password
is_wrong = check_password_hash(password_hash, "wrongpassword")
print("Check with WRONG password:", is_wrong)