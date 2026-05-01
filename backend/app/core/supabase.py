class MockTable:
    def insert(self, data): return self
    def select(self, *args, **kwargs): return self
    def update(self, data): return self
    def delete(self): return self
    def eq(self, *args, **kwargs): return self
    def execute(self):
        class Result:
            data = [{ "id": "mock-id", "tracking_number": "MOCK-123", "status": "pending", "full_name": "Mock User", "role": "admin", "email": "mock@dms.com" }]
            count = 1
        return Result()

class MockSupabase:
    def table(self, name): return MockTable()

supabase = MockSupabase()
def create_client(*args, **kwargs): return supabase
