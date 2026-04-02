from app.utils.security import get_password_hash, verify_password

plain = "123456"
hashed = get_password_hash(plain)

print(hashed)
print(verify_password("123456", hashed))