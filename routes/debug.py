from app import app, socketio
from flask_socketio import emit

def test_emit():
    """Test, ob emit funktioniert"""
    with app.test_request_context('/'):
        emit('test_event', {'data': 'Test'}, broadcast=True)
        return 'Emit sent'

if __name__ == '__main__':
    with app.app_context():
        print(test_emit())