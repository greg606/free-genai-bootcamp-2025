import pytest
from app import create_app
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    # Set up test database
    with app.app_context():
        cursor = app.db.cursor()
        
        # Create required tables
        cursor.executescript('''
            DROP TABLE IF EXISTS session_words;
            DROP TABLE IF EXISTS study_sessions;
            DROP TABLE IF EXISTS words;
            
            CREATE TABLE words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kanji TEXT NOT NULL,
                romaji TEXT NOT NULL,
                english TEXT NOT NULL
            );

            CREATE TABLE study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE session_words (
                session_id INTEGER,
                word_id INTEGER,
                PRIMARY KEY (session_id, word_id),
                FOREIGN KEY (session_id) REFERENCES study_sessions(id),
                FOREIGN KEY (word_id) REFERENCES words(id)
            );
            
            -- Insert test data for words
            INSERT INTO words (id, kanji, romaji, english) VALUES 
                (1, '犬', 'inu', 'dog'),
                (2, '猫', 'neko', 'cat'),
                (3, '鳥', 'tori', 'bird');
        ''')
        app.db.commit()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup after tests
    with app.app_context():
        cursor = app.db.cursor()
        cursor.executescript('''
            DROP TABLE IF EXISTS session_words;
            DROP TABLE IF EXISTS study_sessions;
            DROP TABLE IF EXISTS words;
        ''')
        app.db.commit()

def test_create_study_session_success(client):
    data = {
        "user_id": 1,
        "word_ids": [1, 2, 3],
        "session_type": "review"
    }
    response = client.post('/study_sessions',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 201
    assert 'session_id' in response.json
    assert 'message' in response.json
    assert response.json['message'] == "Study session created successfully"

def test_create_study_session_invalid_data(client):
    data = {
        "user_id": 1,
        "session_type": "review"
        # Missing word_ids
    }
    response = client.post('/study_sessions',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'] == "Missing required fields"

def test_create_study_session_invalid_word_ids(client):
    data = {
        "user_id": 1,
        "word_ids": "not an array",
        "session_type": "review"
    }
    response = client.post('/study_sessions',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'] == "word_ids must be an array"

def test_create_study_session_non_json(client):
    response = client.post('/study_sessions',
                          data="not json",
                          content_type='text/plain')
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'] == "Request must be JSON" 