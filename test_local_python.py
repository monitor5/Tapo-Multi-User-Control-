#!/usr/bin/env python3
"""
Local test script to verify Python environment and dependencies
Run this outside of Docker to test the Python setup
"""

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Python imports...")
    
    try:
        import sys
        print(f"✅ Python version: {sys.version}")
        
        import sqlite3
        print("✅ sqlite3 imported successfully")
        
        import sqlalchemy
        print(f"✅ SQLAlchemy imported successfully (version: {sqlalchemy.__version__})")
        
        from passlib.context import CryptContext
        print("✅ passlib imported successfully")
        
        # Test app imports
        from app.models import Base, User
        print("✅ app.models imported successfully")
        
        from app.db import engine
        print("✅ app.db imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_connection():
    """Test database connection and table creation"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from app.models import Base, User
        from app.db import engine
        from sqlalchemy.orm import Session
        
        # Test engine connection
        with engine.connect() as conn:
            print("✅ Database engine connection successful")
        
        # Test table creation
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test session
        with Session(engine) as session:
            user_count = session.query(User).count()
            print(f"✅ Database session works - Found {user_count} existing users")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("\n🔐 Testing password hashing...")
    
    try:
        from passlib.context import CryptContext
        
        ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_password = "testpass123"
        hashed = ctx.hash(test_password)
        
        print("✅ Password hashing successful")
        print(f"✅ Hash verification: {ctx.verify(test_password, hashed)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 TAPO CONTROL - LOCAL PYTHON ENVIRONMENT TEST")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database_connection),
        ("Password Hashing Test", test_password_hashing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Python environment is ready!")
        print("\n📝 Next steps:")
        print("1. Start Docker Desktop")
        print("2. Run: start_containers.bat")
        print("3. Run: test_user_creation.bat")
    else:
        print("\n⚠️ Some tests failed. Please check dependencies:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main() 