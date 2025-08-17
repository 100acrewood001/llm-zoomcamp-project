#!/usr/bin/env python3

import requests
import json

def test_api_query():
    """Test the API query endpoint"""
    
    # Test the query endpoint
    print("Testing API query endpoint...")
    
    response = requests.post(
        'http://localhost:8000/documents/query',
        headers={'Content-Type': 'application/json'},
        json={
            'question': 'what is the financial performance', 
            'top_k': 3
        }
    )
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('SUCCESS! Query completed successfully')
        print(f'Status: {result["status"]}')
        print(f'Answer length: {len(result["answer"])} characters')
        print(f'Citations: {len(result["citations"])} citations')
        print(f'Confidence: {result["confidence"]}')
        print('\nAnswer preview:')
        print(result["answer"][:300] + "..." if len(result["answer"]) > 300 else result["answer"])
        
        print('\nCitations:')
        for i, citation in enumerate(result["citations"][:2]):
            print(f'  Citation {i+1}: Page {citation["page_numbers"]}, Score: {citation["relevance_score"]:.3f}')
            print(f'    Preview: {citation["text_preview"][:100]}...')
    else:
        print(f'FAILED: {response.text}')

if __name__ == "__main__":
    test_api_query()
