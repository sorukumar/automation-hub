# Automation Hub

Collection of automated tasks for personal use.

## Automations

### 1. Team Elite
- Automated scheduling system
- Runs every Wednesday at 7 AM CST
- Schedules for Saturday morning

## Setup
1. Fork this repository
2. Set up GitHub Secrets:
 - ELITE_USERNAME
 - ELITE_PASSWORD
3. Enable GitHub Actions

## Security
- All sensitive data is managed via GitHub Secrets
- No credentials are stored in code
- Workflow logs are sanitized

## Local Development
1. Clone the repository
2. Create .env file with required credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `python -m pytest`

## Contributing
Feel free to submit issues and enhancement requests!
