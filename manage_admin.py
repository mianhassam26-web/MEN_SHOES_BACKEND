# ========================================
# manage_admin.py - Admin Account Manage Karne Ka Tool
# ========================================
# Is script se aap:
#   1) Naya admin bana sakte hain
#   2) Existing user ko admin bana sakte hain
#   3) Admin ka password change kar sakte hain
#   4) Email/password check kar sakte hain (login kaam karega ya nahi)
#
# Chalane ka tareeqa (backend folder ke andar se, jahan app/ folder hai):
#   python manage_admin.py
#
# Phir screen pe jo options aayenge unme se number choose karke enter dabayein.

from app.database.database import SessionLocal
from app.models.models import User
from app.core.security import hash_password, verify_password


def get_db():
    return SessionLocal()


def create_or_update_admin():
    email = input("Admin ka email dalen: ").strip()
    password = input("Admin ka naya password dalen: ").strip()
    name = input("Admin ka naam dalen (khali chor sakte hain): ").strip() or "Admin"

    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.role = "admin"
            user.password_hash = hash_password(password)
            db.commit()
            print(f"\n✅ '{email}' ka role 'admin' set kar diya gaya hai aur password bhi update ho gaya hai.")
        else:
            new_user = User(
                full_name=name,
                email=email,
                password_hash=hash_password(password),
                role="admin",
            )
            db.add(new_user)
            db.commit()
            print(f"\n✅ Naya admin account '{email}' successfully ban gaya hai.")

        print("Ab aap website ke normal /login page se isi email/password se login karein.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error aya: {e}")
    finally:
        db.close()


def test_login():
    email = input("Email dalen jo test karna hai: ").strip()
    password = input("Password dalen jo test karna hai: ").strip()

    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"\n❌ '{email}' naam ka koi user database mein maujood nahi hai.")
            print("   Pehle option 1 se admin account banayein.")
            return

        if verify_password(password, user.password_hash):
            print(f"\n✅ Password sahi hai! Yeh user login kar sakta hai.")
            print(f"   Role: {user.role}")
            if user.role != "admin":
                print("   ⚠️  Lekin is user ka role 'admin' nahi hai, isliye Admin Panel nahi dikhega.")
                print("   Option 1 use karke isko admin banayein.")
        else:
            print(f"\n❌ Password GALAT hai is email ke liye. (Role in DB: {user.role})")
            print("   Option 1 use karke password reset kar dein.")

    except Exception as e:
        print(f"\n❌ Error aya: {e}")
    finally:
        db.close()


def list_all_users():
    db = get_db()
    try:
        users = db.query(User).all()
        if not users:
            print("\nDatabase mein koi user nahi hai.")
            return
        print(f"\n{'ID':<5}{'Email':<35}{'Role':<10}{'Naam'}")
        print("-" * 70)
        for u in users:
            print(f"{u.id:<5}{u.email:<35}{u.role:<10}{u.full_name}")
    except Exception as e:
        print(f"\n❌ Error aya: {e}")
    finally:
        db.close()


def main():
    while True:
        print("\n" + "=" * 50)
        print("  ADMIN MANAGEMENT TOOL")
        print("=" * 50)
        print("1) Naya admin banao / password change karo")
        print("2) Email/password test karo (login kaam karega ya nahi)")
        print("3) Saare users dikhao")
        print("4) Exit")
        choice = input("\nApna option chunein (1-4): ").strip()

        if choice == "1":
            create_or_update_admin()
        elif choice == "2":
            test_login()
        elif choice == "3":
            list_all_users()
        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Galat option, dobara try karein.")


if __name__ == "__main__":
    main()
