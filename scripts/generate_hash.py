from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if len(sys.argv) > 1:
    password = sys.argv[1]
else:
    password = input("Enter password to hash: ")

print(pwd_context.hash(password))
