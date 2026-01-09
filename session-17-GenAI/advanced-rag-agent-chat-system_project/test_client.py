#!/usr/bin/env python3
"""
WebSocket Test Client for Advanced RAG Agent Chat System
"""

import asyncio
import websockets
import json
import sys


async def chat_session():
    """Start an interactive chat session via WebSocket"""
    
    # Configuration
    ws_url = "ws://localhost:8080/ws/chat/test_conversation_1"
    
    print("=" * 60)
    print("Advanced RAG Agent Chat System - Test Client")
    print("=" * 60)
    print(f"Connecting to {ws_url}...")
    print()
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✓ Connected successfully!")
            print("Type your questions below. Type 'exit' to quit.\n")
            
            while True:
                # Get user input
                query = input("You: ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Send query
                await websocket.send(json.dumps({
                    "query": query,
                    "user_id": "test_user"
                }))
                
                print("\nAssistant: ", end="", flush=True)
                
                # Receive streaming response
                response_complete = False
                sources = []
                
                while not response_complete:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        msg_type = data.get("type")
                        
                        if msg_type == "status":
                            # Show status updates in gray
                            print(f"\n[{data.get('message')}]", end="", flush=True)
                        
                        elif msg_type == "workflow":
                            # Show workflow plan
                            plan = data.get("plan", {})
                            print(f"\n[Workflow: {plan.get('explanation', 'N/A')}]", end="", flush=True)
                        
                        elif msg_type == "retrieval":
                            # Show retrieval info
                            num_docs = data.get("num_docs", 0)
                            print(f"\n[Retrieved {num_docs} documents]", end="", flush=True)
                        
                        elif msg_type == "content":
                            # Print content as it streams
                            print(data.get("content", ""), end="", flush=True)
                        
                        elif msg_type == "complete":
                            # Response is complete
                            sources = data.get("sources", [])
                            response_complete = True
                        
                        elif msg_type == "error":
                            print(f"\n\nError: {data.get('message')}")
                            response_complete = True
                    
                    except websockets.exceptions.ConnectionClosed:
                        print("\n\nConnection closed by server")
                        return
                
                # Show sources if available
                if sources:
                    print("\n\n📚 Sources:")
                    for source in sources[:3]:  # Show top 3 sources
                        print(f"  • {source.get('source', 'Unknown')}", end="")
                        if source.get('page'):
                            print(f" (Page {source['page']})", end="")
                        if source.get('relevance_score'):
                            print(f" - Relevance: {source['relevance_score']:.2f}", end="")
                        print()
                
                print("\n")
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {str(e)}")
        print("\nMake sure the server is running:")
        print("  docker-compose up")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


async def test_rest_api():
    """Test the REST API endpoints"""
    import aiohttp
    
    base_url = "http://localhost:8080"
    
    print("=" * 60)
    print("Testing REST API Endpoints")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        async with session.get(f"{base_url}/health") as resp:
            print(f"   Status: {resp.status}")
            print(f"   Response: {await resp.json()}")
        
        # Test registration
        print("\n2. Testing user registration...")
        user_data = {
            "username": "testuser123",
            "email": "test123@example.com",
            "password": "testpass123"
        }
        async with session.post(f"{base_url}/api/auth/register", json=user_data) as resp:
            if resp.status == 200:
                print(f"   ✓ Registration successful")
                user_info = await resp.json()
                print(f"   User ID: {user_info['id']}")
            else:
                print(f"   Status: {resp.status}")
                print(f"   Response: {await resp.text()}")
        
        # Test login
        print("\n3. Testing login...")
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        async with session.post(
            f"{base_url}/api/auth/token",
            data=login_data
        ) as resp:
            if resp.status == 200:
                token_data = await resp.json()
                token = token_data["access_token"]
                print(f"   ✓ Login successful")
                print(f"   Token: {token[:20]}...")
                
                # Test authenticated endpoint
                print("\n4. Testing authenticated endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{base_url}/api/auth/me", headers=headers) as resp:
                    if resp.status == 200:
                        user = await resp.json()
                        print(f"   ✓ Authentication working")
                        print(f"   User: {user['username']}")
            else:
                print(f"   Status: {resp.status}")
                print(f"   Response: {await resp.text()}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test REST API
        asyncio.run(test_rest_api())
    else:
        # Start chat session
        asyncio.run(chat_session())


if __name__ == "__main__":
    main()