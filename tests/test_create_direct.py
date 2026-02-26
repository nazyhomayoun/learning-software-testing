def test_create_table_directly():
    """Direct test for table creation"""
    from sqlalchemy import create_engine, text
    from ticketer.db.base import Base
    import ticketer.models
    
    # Direct connection
    engine = create_engine("postgresql://postgres:postgres@localhost:5433/ticketing_test")
    
    print("\n--- Tables before create_all ---")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        for row in result:
            print(f"  {row[0]}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    print("\n--- Tables after create_all ---")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = [row[0] for row in result]
        for t in tables:
            print(f"  {t}")
    
    assert "users" in tables, "users table was not created!"
