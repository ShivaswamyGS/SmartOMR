import urllib.request
import json

def test_api():
    login_data = json.dumps({'email': 'teacher@smartomr.com', 'password': 'teacher123'}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/login', 
        data=login_data, 
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        token = res['access_token']
        print('[OK] LOGIN SUCCESS: Token received ->', token[:20], '...')

    req2 = urllib.request.Request(
        'http://127.0.0.1:8000/api/exams', 
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req2) as resp2:
        exams = json.loads(resp2.read().decode())
        print(f'[OK] EXAMS RETRIEVED: Found {len(exams)} exam(s)')
        for ex in exams:
            print(f"    - ID {ex['id']}: '{ex['title']}' | Submissions: {ex['total_submissions']} | Avg: {ex['average_score']}/{ex['max_marks']}")

    if exams:
        exam_id = exams[0]['id']
        req3 = urllib.request.Request(
            f'http://127.0.0.1:8000/api/exams/{exam_id}/results', 
            headers={'Authorization': f'Bearer {token}'}
        )
        with urllib.request.urlopen(req3) as resp3:
            results = json.loads(resp3.read().decode())
            print(f"[OK] RESULTS RETRIEVED: Found {results['total']} evaluated student(s)")
            for r in results['items']:
                print(f"    - Rank #{r['rank']} | ID: {r['student_id']} | Name: {r['student_name']} | Score: {r['raw_score']}/{exams[0]['max_marks']} ({r['percentage']}%) | Status: {r['review_status']}")

if __name__ == '__main__':
    test_api()
