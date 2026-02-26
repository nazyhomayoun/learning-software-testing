def test_check_metadata():
    """Check if models are registered in metadata"""
    from ticketer.db.base import Base
    import ticketer.models  # import all models
    
    print("\n" + "="*50)
    print("Registered tables in Base.metadata:")
    print("="*50)
    
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    print("="*50)
    print(f"Total tables: {len(Base.metadata.tables)}")
    
    assert "users" in Base.metadata.tables, "users table not found!"
    assert len(Base.metadata.tables) > 0, "No tables registered!"
