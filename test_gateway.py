import httpx
import asyncio

API_GATEWAY_URL = "http://localhost:8080"

async def test_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_GATEWAY_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(response.json())

async def test_user_registration():
    async with httpx.AsyncClient() as client:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = await client.post(
            f"{API_GATEWAY_URL}/api/auth/register",
            json=user_data
        )
        print(f"\nUser Registration: {response.status_code}")
        print(response.json())

async def test_paths_search():
    async with httpx.AsyncClient() as client:
        params = {
            "originLat": 45.4642,
            "originLon": 9.1900,
            "destLat": 45.4654,
            "destLon": 9.1859
        }
        response = await client.get(f"{API_GATEWAY_URL}/api/paths/search", params=params)
        print(f"\nPaths Search: {response.status_code}")
        print(response.json())

async def test_rate_limiting():
    async with httpx.AsyncClient() as client:
        print(f"\nTesting Rate Limiting (sending 65 requests)...")
        for i in range(65):
            response = await client.get(f"{API_GATEWAY_URL}/health")
            if response.status_code == 429:
                print(f"Rate limit hit at request {i+1}")
                break
            if i % 10 == 0:
                print(f"Request {i+1}: OK")

async def main():
    print("Testing API Gateway")
    print("=" * 50)

    try:
        await test_health()
        await test_user_registration()
        await test_paths_search()
        await test_rate_limiting()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
