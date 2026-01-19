import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test cases for authentication endpoints"""
    
    async def test_signup_success(self, client: AsyncClient, test_user_data, cleanup_test_user):
        """Test successful user signup with strong password"""
        response = await client.post(
            "/auth/signup",
            json=test_user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["is_paid"] == False
        assert "id" in user
        assert "created_at" in user
    
    
    async def test_signup_duplicate_email(self, client: AsyncClient, test_user_data, cleanup_test_user):
        """Test signup with already registered email"""
        # First signup
        await client.post("/auth/signup", json=test_user_data)
        
        # Try to signup again with same email
        response = await client.post("/auth/signup", json=test_user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    
    async def test_signup_weak_password(self, client: AsyncClient):
        """Test signup with weak password (missing requirements)"""
        weak_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigits!",  # No digits
            "NoSpecial123",  # No special character
        ]
        
        for weak_password in weak_passwords:
            response = await client.post(
                "/auth/signup",
                json={
                    "email": "test@example.com",
                    "password": weak_password
                }
            )
            
            assert response.status_code == 400
            assert "Password" in response.json()["detail"]
    
    
    async def test_login_success(self, client: AsyncClient, test_user_data, cleanup_test_user):
        """Test successful login"""
        # First create user
        await client.post("/auth/signup", json=test_user_data)
        
        # Then login
        response = await client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user_data, cleanup_test_user):
        """Test login with invalid credentials"""
        # Create user
        await client.post("/auth/signup", json=test_user_data)
        
        # Try login with wrong password
        response = await client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    
    async def test_get_me_authenticated(self, client: AsyncClient, test_user_data, cleanup_test_user):
        """Test /me endpoint with valid token"""
        # Signup and get token
        signup_response = await client.post("/auth/signup", json=test_user_data)
        token = signup_response.json()["access_token"]
        
        # Call /me endpoint
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == test_user_data["email"]
        assert data["is_paid"] == False
        assert "id" in data
        assert "created_at" in data
    
    
    async def test_get_me_no_token(self, client: AsyncClient):
        """Test /me endpoint without authentication token"""
        response = await client.get("/auth/me")
        
        assert response.status_code == 403
    
    
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test /me endpoint with invalid token"""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
