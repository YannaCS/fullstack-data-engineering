import httpx
import os

class AIClient():
    
    def __init__(self, api_key: str, base_url: str = 'https://api.openai.com/v1') -> None:
        self.api_key = api_key
        self.base_url = base_url
        
    async def summarize_content(self, content: str):
        print('content', content)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.base_url}/responses",
                timeout=30,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-5-nano",
                    "input": f"summarize the following content in 10 words: {content}",
                    "store": True,
                }
            )
            
            result = response.json()
            print('result', result)
            return result['output'][1]['content'][0]['text']
        
ai_client = AIClient(api_key=os.getenv('OPENAI_SECRECT_KEY') or '')

"""
result:
{
...,
    "output": [
        {
            "id": "rs_0ec579abf9a55d5000692a392e0b8c819083d5e1999c3b80d1",
            "type": "reasoning",
            "summary": []
        },
        {
            "id": "msg_0ec579abf9a55d5000692a392fda148190bb00e9a83d5c7bc7",
            "type": "message",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "annotations": [],
                    "logprobs": [],
                    "text": "Hello! How can I help you today?"
                }
            ],
            "role": "assistant"
        }
    ],
...
}
"""