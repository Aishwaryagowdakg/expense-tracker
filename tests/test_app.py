import pytest
from app import app
from database import db
from models import User, Expense, Budget

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            user = User(username="test", email="test@example.com")
            db.session.add(user)
            db.session.commit()
        yield client

def test_add_expense(client):
    """Test adding expense"""
    response = client.post('/api/expenses', json={
        'amount': 25.50,
        'category': 'Food',
        'description': 'Lunch'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'Expense added' in data['message']

def test_set_budget(client):
    """Test setting budget"""
    response = client.post('/api/budgets', json={
        'category': 'Food',
        'amount': 500,
        'month': 12,
        'year': 2024
    })
    assert response.status_code == 200
    assert 'Budget set' in response.get_json()['message']

def test_monthly_report(client):
    """Test monthly report"""
   
    client.post('/api/expenses', json={
        'amount': 100,
        'category': 'Food',
        'description': 'Test'
    })
    
    response = client.get('/api/reports/monthly')
    assert response.status_code == 200
    data = response.get_json()
    assert 'categories' in data

def test_budget_report(client):
    """Test budget report"""
    
    client.post('/api/budgets', json={
        'category': 'Food',
        'amount': 500,
        'month': 12,
        'year': 2024
    })
    
    response = client.get('/api/reports/budget')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)