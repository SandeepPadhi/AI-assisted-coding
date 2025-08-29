"""
Flask Web Application for Chat Application
Provides a modern web interface for the chat system
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
import os
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional, Dict, List

# Import our existing chat application
from main import ChatApplication

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chat-app-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize Flask-Session
Session(app)

# Global chat application instance
chat_app = ChatApplication()

# Helper functions
def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        try:
            user_id = UUID(session['user_id'])
            return chat_app.get_user_by_id(user_id)
        except (ValueError, TypeError):
            return None
    return None

def require_login(f):
    """Decorator to require user login"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def get_recent_messages(user_id, limit=50):
    """Get recent messages for a user (across all conversations)"""
    try:
        users = chat_app.get_all_users()
        user_dict = {str(u.user_id): u.username for u in users}  # Create lookup dict
        all_messages = []

        for user in users:
            if user.user_id != user_id:
                messages = chat_app.get_message_history(user_id, user.user_id)
                for msg in messages:
                    sender_name = user_dict.get(str(msg.sender_id), "Unknown")
                    receiver_name = user_dict.get(str(msg.receiver_id), "Unknown")

                    # Only show sender name if it's not the current user
                    if msg.sender_id == user_id:
                        sender_name = None  # Current user sent it
                    if msg.receiver_id == user_id:
                        receiver_name = None  # Current user received it

                    all_messages.append({
                        'message_id': str(msg.message_id),
                        'sender_id': str(msg.sender_id),
                        'receiver_id': str(msg.receiver_id),
                        'content': msg.content,
                        'status': msg.status.value,
                        'created_at': msg.created_at.isoformat(),
                        'updated_at': msg.updated_at.isoformat(),
                        'sender_name': sender_name,
                        'receiver_name': receiver_name
                    })

        # Sort by creation time and limit
        all_messages.sort(key=lambda x: x['created_at'], reverse=True)
        return all_messages[:limit]
    except Exception as e:
        print(f"Error getting recent messages: {e}")
        return []

# Routes
@app.route('/')
def index():
    """Home page - redirects to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()

        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('login'))

        # Try to get existing user
        user = chat_app.get_user_by_username(username)

        if not user:
            # Create new user
            try:
                user = chat_app.create_user(username)
                flash(f'Account created successfully! Welcome, {username}!', 'success')
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('login'))

        # Set session
        session['user_id'] = str(user.user_id)
        session['username'] = user.username
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard"""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))

    # Get recent messages
    recent_messages = get_recent_messages(current_user.user_id, 10)

    # Get all users for contacts
    all_users = chat_app.get_all_users()
    contacts = [u for u in all_users if u.user_id != current_user.user_id]

    return render_template('dashboard.html',
                         user=current_user,
                         recent_messages=recent_messages,
                         contacts=contacts)

@app.route('/users')
@require_login
def users():
    """View all users"""
    current_user = get_current_user()
    all_users = chat_app.get_all_users()

    # Calculate user statistics
    from datetime import datetime, timedelta
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(days=1)

    stats = {
        'total_users': len(all_users),
        'new_this_week': len([u for u in all_users if u.created_at > week_ago]),
        'new_today': len([u for u in all_users if u.created_at > day_ago]),
        'can_chat_with': len(all_users) - 1  # Excluding current user
    }

    return render_template('users.html', user=current_user, all_users=all_users, stats=stats)

@app.route('/chat/<user_id>')
@require_login
def chat_with_user(user_id):
    """Chat with a specific user"""
    current_user = get_current_user()

    try:
        # Convert string user_id to UUID
        target_user_id = UUID(user_id)
        target_user = chat_app.get_user_by_id(target_user_id)
        if not target_user:
            flash('User not found.', 'error')
            return redirect(url_for('dashboard'))

        if target_user.user_id == current_user.user_id:
            flash('You cannot chat with yourself.', 'error')
            return redirect(url_for('dashboard'))

        # Get message history
        messages = chat_app.get_message_history(current_user.user_id, target_user.user_id)

        # Format messages for template
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'message_id': str(msg.message_id),
                'content': msg.content,
                'status': msg.status.value,
                'created_at': msg.created_at,
                'is_sender': msg.sender_id == current_user.user_id,
                'sender_name': 'You' if msg.sender_id == current_user.user_id else target_user.username
            })

        return render_template('chat.html',
                             user=current_user,
                             target_user=target_user,
                             messages=formatted_messages)

    except Exception as e:
        flash(f'Error loading chat: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/send_message', methods=['POST'])
@require_login
def send_message():
    """Send a message via AJAX"""
    current_user = get_current_user()

    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()

        if not receiver_id or not content:
            return jsonify({'success': False, 'error': 'Missing required fields'})

        # Validate receiver exists
        receiver_id_uuid = UUID(receiver_id)
        receiver = chat_app.get_user_by_id(receiver_id_uuid)
        if not receiver:
            return jsonify({'success': False, 'error': 'User not found'})

        # Send message
        message = chat_app.send_message(current_user.user_id, receiver.user_id, content)

        return jsonify({
            'success': True,
            'message': {
                'message_id': str(message.message_id),
                'content': message.content,
                'status': message.status.value,
                'created_at': message.created_at.isoformat(),
                'is_sender': True,
                'sender_name': 'You'
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/edit_message', methods=['POST'])
@require_login
def edit_message():
    """Edit a message via AJAX"""
    current_user = get_current_user()

    try:
        data = request.get_json()
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()

        if not message_id or not new_content:
            return jsonify({'success': False, 'error': 'Missing required fields'})

        message_id_uuid = UUID(message_id)
        chat_app.edit_message(message_id_uuid, new_content, current_user.user_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_message', methods=['POST'])
@require_login
def delete_message():
    """Delete a message via AJAX"""
    current_user = get_current_user()

    try:
        data = request.get_json()
        message_id = data.get('message_id')

        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID required'})

        message_id_uuid = UUID(message_id)
        chat_app.delete_message(message_id_uuid, current_user.user_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/groups')
@require_login
def groups():
    """Groups page"""
    current_user = get_current_user()
    return render_template('groups.html', user=current_user)

@app.route('/create_group', methods=['POST'])
@require_login
def create_group():
    """Create a new group"""
    current_user = get_current_user()

    try:
        group_name = request.form.get('group_name', '').strip()

        if not group_name:
            flash('Group name is required.', 'error')
            return redirect(url_for('groups'))

        group = chat_app.create_group(group_name, current_user.user_id)
        flash(f'Group "{group_name}" created successfully!', 'success')

    except Exception as e:
        flash(f'Error creating group: {str(e)}', 'error')

    return redirect(url_for('groups'))

@app.route('/group/<group_id>')
@require_login
def group_chat(group_id):
    """Group chat page"""
    current_user = get_current_user()

    try:
        # For now, we'll just show a placeholder
        # In a real implementation, you'd fetch group details and messages
        return render_template('group_chat.html',
                             user=current_user,
                             group_id=group_id)

    except Exception as e:
        flash(f'Error loading group: {str(e)}', 'error')
        return redirect(url_for('groups'))

@app.route('/api/messages/<user_id>')
@require_login
def get_messages_api(user_id):
    """API endpoint to get messages with a user"""
    current_user = get_current_user()

    try:
        target_user_id = UUID(user_id)
        target_user = chat_app.get_user_by_id(target_user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404

        messages = chat_app.get_message_history(current_user.user_id, target_user.user_id)

        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'message_id': str(msg.message_id),
                'content': msg.content,
                'status': msg.status.value,
                'created_at': msg.created_at.isoformat(),
                'is_sender': msg.sender_id == current_user.user_id,
                'sender_name': 'You' if msg.sender_id == current_user.user_id else target_user.username
            })

        return jsonify({'messages': formatted_messages})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
@require_login
def get_stats():
    """API endpoint for user statistics"""
    try:
        users = chat_app.get_all_users()
        stats = {
            'total_users': len(users),
            'total_messages': 'Coming soon',
            'total_groups': 'Coming soon',
            'active_users': len([u for u in users if (datetime.now() - u.created_at).days < 7])
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_messages')
@require_login
def api_get_recent_messages():
    """API endpoint to get recent messages for current user"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        limit = int(request.args.get('limit', 10))
        # Call the local helper function
        recent_messages = get_recent_messages(current_user.user_id, limit)

        # Format for JSON response
        messages_data = []
        for message in recent_messages:
            messages_data.append({
                'message_id': str(message['message_id']),
                'sender_id': str(message['sender_id']),
                'receiver_id': str(message['receiver_id']),
                'content': message['content'],
                'status': message['status'],
                'created_at': message['created_at'],
                'updated_at': message['updated_at'],
                'sender_name': message['sender_name'],
                'receiver_name': message['receiver_name']
            })

        return jsonify({'messages': messages_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new_messages')
@require_login
def get_new_messages():
    """API endpoint to get messages newer than a specific timestamp"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        since_timestamp = request.args.get('since')
        if not since_timestamp:
            return jsonify({'error': 'Missing since parameter'}), 400

        # Parse timestamp - handle different formats
        try:
            # Try ISO format first
            since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try alternative format
                since_dt = datetime.fromisoformat(since_timestamp)
            except ValueError:
                # Fallback to current time minus 1 minute
                since_dt = datetime.now() - timedelta(minutes=1)

        # Get all recent messages
        recent_messages = get_recent_messages(current_user.user_id, 50)

        # Filter messages newer than the timestamp
        new_messages = []
        for message in recent_messages:
            message_dt = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
            if message_dt > since_dt:
                new_messages.append({
                    'message_id': str(message['message_id']),
                    'sender_id': str(message['sender_id']),
                    'receiver_id': str(message['receiver_id']),
                    'content': message['content'],
                    'status': message['status'],
                    'created_at': message['created_at'],
                    'updated_at': message['updated_at'],
                    'sender_name': message['sender_name'],
                    'receiver_name': message['receiver_name']
                })

        return jsonify({'messages': new_messages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Template filters
@app.template_filter('datetime')
def format_datetime(value, format='%H:%M'):
    """Format datetime for display"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.strftime(format)

@app.template_filter('date')
def format_date(value, format='%Y-%m-%d'):
    """Format date for display"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.strftime(format)

if __name__ == '__main__':
    import sys
    port = 5001  # Use port 5001 as default to avoid conflicts
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    app.run(debug=True, host='0.0.0.0', port=port)
