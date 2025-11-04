#!/usr/bin/env python3
"""
Generate secure secrets for production deployment
"""
import secrets
import string
import argparse
from pathlib import Path


def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_database_password(length=32):
    """Generate a secure database password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key(length=32):
    """Generate a secure API key"""
    return secrets.token_urlsafe(length)


def generate_jwt_secret():
    """Generate JWT secret key"""
    return secrets.token_urlsafe(64)


def main():
    parser = argparse.ArgumentParser(description="Generate secure secrets for Janasamparka")
    parser.add_argument("--env", choices=["production", "staging"], default="production",
                       help="Environment to generate secrets for")
    parser.add_argument("--output", default=None, 
                       help="Output file path (default: .env.{env})")
    
    args = parser.parse_args()
    
    env_file = args.output or f".env.{args.env}"
    
    # Generate all secrets
    secrets_dict = {
        "SECRET_KEY": generate_jwt_secret(),
        "DATABASE_PASSWORD": generate_database_password(),
        "REDIS_PASSWORD": generate_database_password(24),
        "SMS_PROVIDER_API_KEY": generate_api_key(),
        "BHOOMI_API_KEY": generate_api_key(),
        "KSNDMC_API_KEY": generate_api_key(),
        "APMC_API_KEY": generate_api_key(),
        "AWS_ACCESS_KEY_ID": f"AKIA{secrets.token_hex(8).upper()}",
        "AWS_SECRET_ACCESS_KEY": secrets.token_urlsafe(40),
        "SENTRY_DSN": "https://YOUR-SENTRY-PROJECT@sentry.io/PROJECT-ID",
    }
    
    # Read existing template if it exists
    template_file = Path(f".env.{args.env}.example")
    env_content = []
    
    if template_file.exists():
        with open(template_file, 'r') as f:
            env_content = f.readlines()
    
    # Replace secrets in template
    for i, line in enumerate(env_content):
        for key, value in secrets_dict.items():
            if line.startswith(f"{key}="):
                if "=" in line:
                    current_value = line.split("=", 1)[1].strip()
                    # Don't replace placeholder values
                    if not current_value.startswith("your-") and not current_value.startswith("staging-"):
                        continue
                env_content[i] = f"{key}={value}\n"
    
    # Add any missing secrets
    existing_keys = set()
    for line in env_content:
        if "=" in line:
            existing_keys.add(line.split("=", 1)[0])
    
    for key, value in secrets_dict.items():
        if key not in existing_keys:
            env_content.append(f"{key}={value}\n")
    
    # Write to file
    output_path = Path(env_file)
    with open(output_path, 'w') as f:
        f.writelines(env_content)
    
    print(f"✅ Generated secrets for {args.env} environment")
    print(f"📁 Saved to: {output_path.absolute()}")
    print(f"🔒 Generated {len(secrets_dict)} secure secrets")
    print("\n⚠️  IMPORTANT:")
    print("1. Store these secrets securely")
    print("2. Add the .env file to .gitignore")
    print("3. Update placeholder values (like SENTRY_DSN) with actual URLs")
    print("4. Share secrets only through secure channels")


if __name__ == "__main__":
    main()
