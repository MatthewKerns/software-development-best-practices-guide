# Security Hardening Guide

## Overview

Security hardening transforms systems from default configurations into production-ready, defense-in-depth architectures that protect against real-world threats. This guide provides actionable security measures across all complexity tiers.

**Security Principles:**

1. **Defense in Depth:** Multiple layers of security controls
2. **Least Privilege:** Grant minimum necessary permissions
3. **Fail Securely:** Failures should deny access, not grant it
4. **Security by Design:** Build security in from the start
5. **Continuous Monitoring:** Detect and respond to threats

**Complexity Tiers:**

- **Small-Scale:** HTTPS, security headers, basic auth, input validation
- **Medium-Scale:** OAuth/JWT, secrets vault, rate limiting, security scanning
- **Large-Scale:** Zero-trust architecture, mTLS, SOC2 compliance, pen testing

---

## 1. Network Security

### 1.1 HTTPS/TLS Configuration (All Scales)

**Why:** Encrypt data in transit, prevent man-in-the-middle attacks

**TLS Certificate Setup (Let's Encrypt):**
```bash
#!/bin/bash
# setup-https.sh - Automated HTTPS setup with Let's Encrypt

# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d example.com -d www.example.com \
  --non-interactive \
  --agree-tos \
  --email admin@example.com \
  --redirect

# Verify certificate
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -dates

# Setup automatic renewal
sudo certbot renew --dry-run

# Add renewal to crontab
echo "0 0,12 * * * certbot renew --quiet" | sudo crontab -
```

**Nginx TLS Configuration (Hardened):**
```nginx
# /etc/nginx/sites-available/example.com
server {
    listen 80;
    server_name example.com www.example.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    # TLS certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS protocol versions (TLS 1.2+ only)
    ssl_protocols TLSv1.2 TLSv1.3;

    # Strong cipher suites (forward secrecy)
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # SSL session caching (performance)
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # OCSP stapling (performance + privacy)
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.example.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;

    # Application
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Test TLS Configuration:**
```bash
# Test with SSL Labs
# https://www.ssllabs.com/ssltest/analyze.html?d=example.com

# Test with testssl.sh
docker run --rm -ti drwetter/testssl.sh example.com

# Verify HSTS
curl -I https://example.com | grep Strict-Transport-Security

# Verify TLS 1.3 support
openssl s_client -connect example.com:443 -tls1_3
```

**Checklist:**
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] TLS 1.2+ only (no TLS 1.0/1.1, no SSLv3)
- [ ] Strong cipher suites (ECDHE for forward secrecy)
- [ ] HSTS header configured (max-age 1+ year)
- [ ] Certificate auto-renewal configured
- [ ] SSL Labs grade A+ achieved

### 1.2 Firewall & Network Segmentation (Medium/Large Scale)

**Why:** Limit attack surface, restrict unnecessary network access

**UFW Firewall (Ubuntu):**
```bash
#!/bin/bash
# firewall-setup.sh - Configure UFW firewall

# Enable UFW
sudo ufw --force enable

# Default policies (deny all incoming, allow all outgoing)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (limit to specific IPs in production)
sudo ufw allow from 203.0.113.0/24 to any port 22 proto tcp comment 'SSH from office'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Allow PostgreSQL (only from app servers)
sudo ufw allow from 10.0.1.0/24 to any port 5432 proto tcp comment 'PostgreSQL from app servers'

# Rate limiting on SSH (prevent brute force)
sudo ufw limit 22/tcp comment 'SSH rate limit'

# Show status
sudo ufw status verbose
```

**AWS Security Groups:**
```python
# security_groups.py - Terraform AWS security groups
resource "aws_security_group" "web" {
  name        = "web-servers"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  # Allow HTTPS from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  # Allow HTTP (redirect to HTTPS)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from internet"
  }

  # Allow SSH from bastion only
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion"
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-servers"
  }
}

resource "aws_security_group" "database" {
  name        = "database"
  description = "Security group for database servers"
  vpc_id      = aws_vpc.main.id

  # Allow PostgreSQL from app servers only
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "PostgreSQL from app servers"
  }

  # No outbound internet access (defense in depth)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]  # VPC only
  }

  tags = {
    Name = "database"
  }
}
```

**Checklist:**
- [ ] Firewall configured (UFW, Security Groups, iptables)
- [ ] Default deny all incoming traffic
- [ ] Only necessary ports open
- [ ] SSH restricted to specific IPs/bastion
- [ ] Database ports not exposed to internet
- [ ] Network segmentation (web/app/db tiers)

---

## 2. Authentication & Authorization

### 2.1 Password Security (All Scales)

**Why:** Weak passwords are the #1 cause of account breaches

**Password Hashing (bcrypt):**
```python
# password_security.py
import bcrypt
import re

class PasswordManager:
    """Secure password hashing and validation."""

    # Password policy
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True

    @classmethod
    def hash_password(cls, password):
        """Hash password with bcrypt (cost factor 12)."""
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @classmethod
    def verify_password(cls, password, hashed):
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    @classmethod
    def validate_password_strength(cls, password):
        """Validate password meets security requirements."""
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f'Password must be at least {cls.MIN_LENGTH} characters')

        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append('Password must contain uppercase letter')

        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append('Password must contain lowercase letter')

        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append('Password must contain digit')

        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain special character')

        # Check against common passwords
        if password.lower() in cls.get_common_passwords():
            errors.append('Password is too common')

        return errors

    @staticmethod
    def get_common_passwords():
        """Top 10,000 most common passwords (load from file)."""
        return {
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'monkey', '1234567', 'letmein', 'trustno1', 'dragon'
            # ... load from common-passwords.txt
        }

# Usage
@app.route('/register', methods=['POST'])
def register():
    password = request.json['password']

    # Validate password strength
    errors = PasswordManager.validate_password_strength(password)
    if errors:
        return jsonify({'errors': errors}), 400

    # Hash password
    password_hash = PasswordManager.hash_password(password)

    # Store user
    user = User(
        email=request.json['email'],
        password_hash=password_hash
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created'}), 201

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.json['email']).first()

    if not user or not PasswordManager.verify_password(
        request.json['password'],
        user.password_hash
    ):
        # Generic error (don't reveal if email exists)
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate JWT token
    token = generate_jwt(user.id)
    return jsonify({'access_token': token})
```

**Checklist:**
- [ ] Passwords hashed with bcrypt/Argon2 (never plaintext)
- [ ] Password policy enforced (12+ chars, complexity)
- [ ] Common passwords rejected
- [ ] Account lockout after N failed attempts (5-10)
- [ ] Password reset via secure token (time-limited)

### 2.2 Multi-Factor Authentication (Medium/Large Scale)

**Why:** Passwords alone are insufficient, MFA adds critical second layer

**TOTP Implementation (Time-Based One-Time Passwords):**
```python
# mfa.py
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAManager:
    """Multi-factor authentication with TOTP."""

    @staticmethod
    def generate_secret():
        """Generate new TOTP secret for user."""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(user, secret):
        """Generate QR code URI for authenticator app."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user.email,
            issuer_name='YourApp'
        )

    @staticmethod
    def generate_qr_code(provisioning_uri):
        """Generate QR code image for provisioning."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for API response
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_token(secret, token):
        """Verify TOTP token (with 30s window for clock drift)."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

# MFA enrollment endpoint
@app.route('/api/mfa/enroll', methods=['POST'])
@require_auth
def enroll_mfa():
    """Enroll user in MFA."""
    # Generate secret
    secret = MFAManager.generate_secret()

    # Store secret (encrypted)
    request.user.mfa_secret = encrypt(secret)
    request.user.mfa_enabled = False  # Not enabled until verified
    db.session.commit()

    # Generate QR code
    provisioning_uri = MFAManager.get_provisioning_uri(request.user, secret)
    qr_code = MFAManager.generate_qr_code(provisioning_uri)

    return jsonify({
        'secret': secret,  # Show once for manual entry
        'qr_code': qr_code
    })

@app.route('/api/mfa/verify-enrollment', methods=['POST'])
@require_auth
def verify_mfa_enrollment():
    """Verify MFA enrollment with first token."""
    token = request.json['token']
    secret = decrypt(request.user.mfa_secret)

    if MFAManager.verify_token(secret, token):
        request.user.mfa_enabled = True
        db.session.commit()
        return jsonify({'message': 'MFA enabled'})
    else:
        return jsonify({'error': 'Invalid token'}), 400

# MFA login flow
@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.json['email']).first()

    # Verify password
    if not user or not PasswordManager.verify_password(
        request.json['password'],
        user.password_hash
    ):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Check if MFA enabled
    if user.mfa_enabled:
        # Return temporary token requiring MFA
        temp_token = generate_mfa_challenge_token(user.id)
        return jsonify({
            'mfa_required': True,
            'challenge_token': temp_token
        }), 200

    # No MFA, return access token
    token = generate_jwt(user.id)
    return jsonify({'access_token': token})

@app.route('/login/mfa', methods=['POST'])
def login_mfa():
    """Complete login with MFA token."""
    challenge_token = request.json['challenge_token']
    mfa_token = request.json['mfa_token']

    # Verify challenge token
    user_id = verify_mfa_challenge_token(challenge_token)
    if not user_id:
        return jsonify({'error': 'Invalid challenge token'}), 401

    user = User.query.get(user_id)
    secret = decrypt(user.mfa_secret)

    # Verify MFA token
    if not MFAManager.verify_token(secret, mfa_token):
        return jsonify({'error': 'Invalid MFA token'}), 401

    # Generate access token
    token = generate_jwt(user.id)
    return jsonify({'access_token': token})
```

**Backup Codes:**
```python
# Generate backup codes for MFA recovery
import secrets

def generate_backup_codes(count=10):
    """Generate one-time use backup codes."""
    codes = []
    for _ in range(count):
        code = '-'.join([
            secrets.token_hex(2).upper()
            for _ in range(4)
        ])
        codes.append(code)
    return codes

# Store backup codes (hashed)
@app.route('/api/mfa/backup-codes', methods=['POST'])
@require_auth
def generate_backup_codes_endpoint():
    codes = generate_backup_codes()

    # Hash and store
    hashed_codes = [
        PasswordManager.hash_password(code)
        for code in codes
    ]
    request.user.backup_codes = json.dumps(hashed_codes)
    db.session.commit()

    # Return codes once (user must save them)
    return jsonify({'backup_codes': codes})
```

**Checklist:**
- [ ] MFA enforced for admin accounts
- [ ] TOTP implementation (Google Authenticator compatible)
- [ ] Backup codes generated for recovery
- [ ] MFA enrollment flow tested
- [ ] SMS/email 2FA considered (less secure than TOTP)

### 2.3 JWT Token Security (Medium/Large Scale)

**Why:** Stateless authentication, but tokens must be secure

**Secure JWT Implementation:**
```python
# jwt_security.py
import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # 256-bit random key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE = 7  # 7 days

def generate_jwt(user_id, token_type='access'):
    """Generate JWT token with short expiration."""
    if token_type == 'access':
        expire_minutes = ACCESS_TOKEN_EXPIRE
    elif token_type == 'refresh':
        expire_minutes = REFRESH_TOKEN_EXPIRE * 24 * 60
    else:
        raise ValueError('Invalid token type')

    payload = {
        'user_id': user_id,
        'type': token_type,
        'exp': datetime.utcnow() + timedelta(minutes=expire_minutes),
        'iat': datetime.utcnow(),
        'jti': secrets.token_hex(16)  # Token ID (for revocation)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt(token, token_type='access'):
    """Verify JWT token and extract payload."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Verify token type
        if payload.get('type') != token_type:
            raise jwt.InvalidTokenError('Invalid token type')

        # Check if token is revoked (check blacklist)
        if is_token_revoked(payload['jti']):
            raise jwt.InvalidTokenError('Token has been revoked')

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError as e:
        raise ValueError(f'Invalid token: {str(e)}')

# Token refresh flow
@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Exchange refresh token for new access token."""
    refresh_token = request.json.get('refresh_token')

    try:
        payload = verify_jwt(refresh_token, token_type='refresh')
        user_id = payload['user_id']

        # Generate new access token
        new_access_token = generate_jwt(user_id, token_type='access')

        return jsonify({
            'access_token': new_access_token
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 401

# Token revocation (logout)
@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Revoke all user tokens."""
    # Extract token ID
    token = request.headers.get('Authorization').replace('Bearer ', '')
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload['jti']

    # Add to blacklist (Redis with TTL)
    redis_client.setex(
        f'revoked_token:{jti}',
        ACCESS_TOKEN_EXPIRE * 60,
        '1'
    )

    return jsonify({'message': 'Logged out successfully'})

def is_token_revoked(jti):
    """Check if token is in blacklist."""
    return redis_client.exists(f'revoked_token:{jti}')
```

**Checklist:**
- [ ] JWT secret key strong (256-bit random)
- [ ] Access tokens short-lived (<15 minutes)
- [ ] Refresh tokens used for renewal
- [ ] Token revocation implemented (logout)
- [ ] Tokens validated on every request

---

## 3. Input Validation & Injection Prevention

### 3.1 SQL Injection Prevention (All Scales)

**Why:** SQL injection is OWASP #1 vulnerability

**Safe Database Queries:**
```python
# sql_injection_prevention.py

# ❌ BAD: String concatenation (vulnerable to SQL injection)
def get_user_bad(email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    result = db.execute(query)
    # Attacker can inject: ' OR '1'='1

# ✅ GOOD: Parameterized queries
def get_user_good(email):
    query = "SELECT * FROM users WHERE email = %s"
    result = db.execute(query, (email,))

# ✅ GOOD: ORM (SQLAlchemy)
def get_user_orm(email):
    return User.query.filter_by(email=email).first()

# ❌ BAD: Dynamic table names (still vulnerable)
def get_records_bad(table_name):
    query = f"SELECT * FROM {table_name}"
    result = db.execute(query)
    # Attacker can inject: users; DROP TABLE users;--

# ✅ GOOD: Whitelist table names
ALLOWED_TABLES = {'users', 'posts', 'comments'}

def get_records_good(table_name):
    if table_name not in ALLOWED_TABLES:
        raise ValueError('Invalid table name')

    # Use identifier escaping
    query = sql.SQL("SELECT * FROM {}").format(
        sql.Identifier(table_name)
    )
    result = db.execute(query)
```

**Checklist:**
- [ ] All queries use parameterized statements
- [ ] ORM used where possible (SQLAlchemy, Django ORM)
- [ ] No string concatenation in SQL queries
- [ ] Dynamic table/column names whitelisted
- [ ] Stored procedures use bind variables

### 3.2 XSS Prevention (All Scales)

**Why:** Cross-Site Scripting allows attackers to execute JavaScript in users' browsers

**Output Encoding:**
```python
# xss_prevention.py
from markupsafe import escape
import bleach

# ✅ Template auto-escaping (Jinja2)
# {{ user_input }} automatically escapes HTML

# ✅ Manual escaping
def safe_render(user_input):
    return escape(user_input)

# ❌ BAD: Marking as safe without sanitization
def unsafe_render(user_input):
    return Markup(user_input)  # Don't do this!

# ✅ GOOD: Sanitize HTML (allow safe tags only)
def sanitize_html(user_html):
    allowed_tags = ['p', 'br', 'strong', 'em', 'a', 'ul', 'li']
    allowed_attrs = {'a': ['href', 'title']}

    clean_html = bleach.clean(
        user_html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

    return clean_html

# Content Security Policy headers
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none';"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

**Frontend XSS Prevention:**
```javascript
// xss_prevention.js

// ❌ BAD: innerHTML with user input
element.innerHTML = userInput;

// ✅ GOOD: textContent (auto-escapes)
element.textContent = userInput;

// ✅ GOOD: DOMPurify for HTML sanitization
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);

// ❌ BAD: eval() with user input
eval(userCode);  // Never do this!

// ❌ BAD: Inline event handlers
element.setAttribute('onclick', userInput);

// ✅ GOOD: addEventListener
element.addEventListener('click', () => {
    // Safe event handling
});
```

**Checklist:**
- [ ] All user input HTML-escaped by default
- [ ] CSP headers configured
- [ ] HTML sanitization for rich text (Bleach, DOMPurify)
- [ ] No eval() or innerHTML with user input
- [ ] X-XSS-Protection header enabled

### 3.3 CSRF Protection (All Scales)

**Why:** Prevent attackers from forging requests on behalf of authenticated users

**CSRF Token Implementation:**
```python
# csrf_protection.py
from flask_wtf.csrf import CSRFProtect
import secrets

csrf = CSRFProtect(app)

# Generate CSRF token
def generate_csrf_token():
    """Generate CSRF token for form."""
    token = secrets.token_hex(32)
    session['csrf_token'] = token
    return token

# Validate CSRF token
def validate_csrf_token(token):
    """Validate CSRF token from request."""
    session_token = session.get('csrf_token')
    return session_token and secrets.compare_digest(session_token, token)

# CSRF protection decorator
def csrf_protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Exempt safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)

        # Validate CSRF token
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')

        if not token or not validate_csrf_token(token):
            return jsonify({'error': 'CSRF token invalid'}), 403

        return f(*args, **kwargs)

    return decorated_function

# Usage
@app.route('/api/transfer', methods=['POST'])
@require_auth
@csrf_protected
def transfer_money():
    # Process transfer
    pass
```

**Frontend CSRF Token:**
```javascript
// Include CSRF token in requests
fetch('/api/transfer', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify({ amount: 100 })
});
```

**Checklist:**
- [ ] CSRF tokens required for state-changing operations
- [ ] Tokens validated on server side
- [ ] Tokens bound to user session
- [ ] SameSite cookie attribute set

---

## 4. Secrets Management (Medium/Large Scale)

### 4.1 Environment Variables & Secrets Vault

**Why:** Hardcoded credentials = instant compromise

**AWS Secrets Manager:**
```python
# secrets_manager.py
import boto3
import json
from functools import lru_cache

class SecretsManager:
    """Fetch secrets from AWS Secrets Manager."""

    def __init__(self, region='us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region)

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name):
        """Fetch secret (with caching)."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Failed to fetch secret {secret_name}: {e}")
            raise

    def get_database_credentials(self, environment='production'):
        """Get database credentials."""
        secret_name = f'{environment}/database/credentials'
        credentials = self.get_secret(secret_name)
        return credentials

# Initialize app with secrets
secrets_manager = SecretsManager()
db_creds = secrets_manager.get_database_credentials('production')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{db_creds['username']}:{db_creds['password']}"
    f"@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
)
```

**Secrets Rotation:**
```python
# rotate_secrets.py
import boto3
import psycopg2
import secrets

def rotate_database_password(secret_name):
    """Rotate database password."""
    secrets_client = boto3.client('secretsmanager')

    # Get current secret
    response = secrets_client.get_secret_value(SecretId=secret_name)
    current_secret = json.loads(response['SecretString'])

    # Generate new password
    new_password = secrets.token_urlsafe(32)

    # Update database user password
    conn = psycopg2.connect(
        host=current_secret['host'],
        user=current_secret['username'],
        password=current_secret['password'],
        database=current_secret['database']
    )
    cursor = conn.cursor()
    cursor.execute(
        f"ALTER USER {current_secret['username']} WITH PASSWORD %s;",
        (new_password,)
    )
    conn.commit()
    conn.close()

    # Update secret in vault
    current_secret['password'] = new_password
    secrets_client.put_secret_value(
        SecretId=secret_name,
        SecretString=json.dumps(current_secret)
    )

    logger.info(f"Rotated password for {secret_name}")

# Run quarterly
rotate_database_password('production/database/credentials')
```

**Checklist:**
- [ ] No secrets in version control (git-secrets scan)
- [ ] Secrets stored in vault (AWS Secrets Manager, Vault)
- [ ] Secrets rotated every 90 days (automated)
- [ ] Environment-specific secrets (dev/staging/prod isolated)
- [ ] Audit logging for secret access

---

## 5. API Security (Medium/Large Scale)

### 5.1 Rate Limiting

**Why:** Prevent abuse, brute force, DDoS

**Implementation:**
```python
# rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Redis-backed rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per hour", "50 per minute"]
)

# Per-endpoint rate limiting
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def login():
    pass

@app.route('/api/expensive-operation', methods=['POST'])
@limiter.limit("10 per hour", key_func=lambda: request.user_id)  # Per-user
def expensive_operation():
    pass

# Custom rate limiting (per user + per IP)
from functools import wraps

def rate_limit_user_and_ip(limit, period):
    """Rate limit by both user and IP."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_key = f"rate_limit:user:{request.user_id}:{f.__name__}"
            ip_key = f"rate_limit:ip:{request.remote_addr}:{f.__name__}"

            # Check both limits
            user_count = redis_client.incr(user_key)
            ip_count = redis_client.incr(ip_key)

            # Set TTL on first request
            if user_count == 1:
                redis_client.expire(user_key, period)
            if ip_count == 1:
                redis_client.expire(ip_key, period)

            if user_count > limit or ip_count > limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': redis_client.ttl(user_key)
                }), 429

            return f(*args, **kwargs)

        return decorated_function
    return decorator
```

**Checklist:**
- [ ] Global rate limits (200/hour, 50/minute)
- [ ] Auth endpoint rate limits (5-10/minute)
- [ ] Per-user rate limits (prevents single user abuse)
- [ ] Per-IP rate limits (prevents distributed attacks)
- [ ] 429 status code returned with Retry-After header

### 5.2 API Authentication

**Implementation covered in Section 2.3 (JWT)**

**Checklist:**
- [ ] API keys for service-to-service (not user auth)
- [ ] JWT tokens for user authentication
- [ ] OAuth 2.0 for third-party integrations
- [ ] mTLS for microservice communication (large scale)

---

## 6. Vulnerability Management (All Scales)

### 6.1 Dependency Scanning

**Why:** 80% of vulnerabilities come from dependencies

**Automated Scanning:**
```bash
# Python dependency scanning
pip install safety
safety check --json

# Node.js dependency scanning
npm audit --audit-level=high

# Scan Docker images
trivy image myapp:latest --severity CRITICAL,HIGH

# Continuous scanning in CI/CD
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Run Bandit (SAST)
        run: |
          pip install bandit
          bandit -r app/ -ll -f json -o bandit-report.json
```

**Checklist:**
- [ ] Dependency scanning automated (Snyk, Dependabot)
- [ ] Scan on every commit (CI/CD integration)
- [ ] Critical/high vulnerabilities block deployment
- [ ] Patch within 7 days of disclosure
- [ ] SBOM (Software Bill of Materials) maintained

### 6.2 Security Headers

**Comprehensive Security Headers:**
```python
# security_headers.py
@app.after_request
def add_security_headers(response):
    """Add comprehensive security headers."""

    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # XSS protection (legacy but still useful)
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # HTTPS enforcement (1 year)
    response.headers['Strict-Transport-Security'] = (
        'max-age=31536000; includeSubDomains; preload'
    )

    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "upgrade-insecure-requests;"
    )

    # Permissions policy (formerly Feature-Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=()"
    )

    return response
```

**Test Security Headers:**
```bash
# Test with securityheaders.com
curl -I https://example.com

# Or use online tool
# https://securityheaders.com/?q=example.com&followRedirects=on
```

**Checklist:**
- [ ] All security headers configured
- [ ] CSP policy defined (no 'unsafe-eval', minimal 'unsafe-inline')
- [ ] HSTS with preload (1+ year max-age)
- [ ] SecurityHeaders.com grade A+

---

## 7. Security Monitoring (Medium/Large Scale)

### 7.1 Audit Logging

**Implementation:**
```python
# audit_logging.py
class AuditLog(db.Model):
    """Audit log for security events."""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(255))
    action = db.Column(db.String(50))
    result = db.Column(db.String(20))  # success, failure
    details = db.Column(db.JSON)

def log_security_event(event_type, resource_type=None, resource_id=None,
                       action=None, result='success', details=None):
    """Log security-relevant event."""
    audit_log = AuditLog(
        event_type=event_type,
        user_id=getattr(request, 'user_id', None),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        result=result,
        details=details
    )
    db.session.add(audit_log)
    db.session.commit()

# Log authentication events
@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.json['email']).first()

    if not user or not verify_password(request.json['password'], user.password_hash):
        log_security_event('login', result='failure',
                          details={'email': request.json['email']})
        return jsonify({'error': 'Invalid credentials'}), 401

    log_security_event('login', result='success',
                      details={'user_id': user.id})
    return jsonify({'access_token': generate_jwt(user.id)})

# Log privileged actions
@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@require_role('admin')
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    old_role = user.role
    new_role = request.json['role']

    user.role = new_role
    db.session.commit()

    log_security_event(
        'role_change',
        resource_type='user',
        resource_id=user_id,
        action='update',
        details={'old_role': old_role, 'new_role': new_role}
    )

    return jsonify({'message': 'Role updated'})
```

**Checklist:**
- [ ] Authentication events logged (login, logout, failures)
- [ ] Authorization failures logged
- [ ] Privileged actions logged (role changes, admin actions)
- [ ] Audit logs tamper-proof (append-only, separate storage)
- [ ] Retention 1+ year (compliance dependent)

### 7.2 Intrusion Detection

**Detect Suspicious Patterns:**
```python
# intrusion_detection.py
from collections import defaultdict
from datetime import datetime, timedelta

class IntrusionDetector:
    """Detect suspicious security patterns."""

    def __init__(self):
        self.failed_logins = defaultdict(list)
        self.privilege_escalations = defaultdict(list)

    def detect_brute_force(self, ip_address):
        """Detect brute force login attempts."""
        # Get failed logins from last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        failed_attempts = AuditLog.query.filter(
            AuditLog.event_type == 'login',
            AuditLog.result == 'failure',
            AuditLog.ip_address == ip_address,
            AuditLog.timestamp > one_hour_ago
        ).count()

        if failed_attempts >= 10:
            self.alert_security_team(
                severity='high',
                event='brute_force_detected',
                details={
                    'ip_address': ip_address,
                    'failed_attempts': failed_attempts,
                    'timeframe': '1 hour'
                }
            )

            # Block IP temporarily
            self.block_ip(ip_address, duration=3600)  # 1 hour

    def detect_privilege_escalation(self, user_id):
        """Detect suspicious privilege escalation."""
        # Check for rapid role changes
        recent_changes = AuditLog.query.filter(
            AuditLog.event_type == 'role_change',
            AuditLog.resource_id == str(user_id),
            AuditLog.timestamp > datetime.utcnow() - timedelta(hours=24)
        ).count()

        if recent_changes >= 3:
            self.alert_security_team(
                severity='critical',
                event='privilege_escalation_detected',
                details={
                    'user_id': user_id,
                    'role_changes': recent_changes,
                    'timeframe': '24 hours'
                }
            )

    def alert_security_team(self, severity, event, details):
        """Send alert to security team."""
        # Send to PagerDuty, Slack, email
        send_slack_notification(
            channel='#security-alerts',
            message=f"🚨 {severity.upper()}: {event}",
            details=json.dumps(details, indent=2)
        )

        if severity == 'critical':
            trigger_pagerduty_incident(
                title=f"Security Alert: {event}",
                description=json.dumps(details)
            )
```

**Checklist:**
- [ ] Brute force detection (failed logins)
- [ ] Privilege escalation detection
- [ ] Anomalous access patterns detected
- [ ] Security alerts automated (Slack, PagerDuty)
- [ ] IP blocking for attacks

---

## Summary: Security Checklist by Scale

**Small-Scale (Essential Security):**
- [ ] HTTPS with strong TLS configuration
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] Password hashing (bcrypt)
- [ ] Input validation (SQL injection, XSS prevention)
- [ ] Rate limiting on auth endpoints
- [ ] Dependency scanning

**Medium-Scale (Production Security):**
- [ ] Multi-factor authentication
- [ ] JWT token security (short expiration, refresh tokens)
- [ ] Secrets vault (AWS Secrets Manager)
- [ ] CSRF protection
- [ ] Audit logging for security events
- [ ] Automated vulnerability scanning in CI/CD
- [ ] Firewall configuration

**Large-Scale (Enterprise Security):**
- [ ] Zero-trust architecture (mTLS between services)
- [ ] SOC2/ISO 27001 compliance
- [ ] Penetration testing (annual or quarterly)
- [ ] Security Information and Event Management (SIEM)
- [ ] Intrusion detection system (IDS)
- [ ] Incident response playbooks
- [ ] Bug bounty program

**Universal Best Practices:**
- [ ] Principle of least privilege
- [ ] Defense in depth (multiple layers)
- [ ] Security training for developers
- [ ] Regular security audits
- [ ] Incident response plan

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-27
**Related:** [PRODUCTION_READINESS_FRAMEWORK.md](PRODUCTION_READINESS_FRAMEWORK.md#2-security-posture), [MEDIUM_SCALE_READINESS.md](MEDIUM_SCALE_READINESS.md#2-security-hardening-5-7-days), [LARGE_SCALE_READINESS.md](LARGE_SCALE_READINESS.md#2-enterprise-security--compliance-4-6-weeks)
