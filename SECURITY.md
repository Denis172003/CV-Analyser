# Security Policy

## Supported Versions

We actively support the following versions of AI Resume Analyzer with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of AI Resume Analyzer seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [your-email@domain.com]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Process

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.

2. **Investigation**: We will investigate the issue and determine its severity and impact.

3. **Resolution**: We will work on a fix and coordinate the release timeline with you.

4. **Disclosure**: We will publicly disclose the vulnerability after a fix is available, giving you credit for the discovery (if desired).

## Security Best Practices

### For Users

- **API Keys**: Never share your API keys publicly or commit them to version control
- **Environment Variables**: Use `.env` files and keep them secure
- **Updates**: Keep the application updated to the latest version
- **Access Control**: Limit access to the application in production environments

### For Developers

- **Input Validation**: Always validate and sanitize user inputs
- **API Security**: Implement rate limiting and proper authentication
- **Dependencies**: Regularly update dependencies and scan for vulnerabilities
- **Secrets Management**: Use proper secret management systems in production

## Known Security Considerations

### API Key Management
- OpenAI API keys should be kept secure and rotated regularly
- Supabase keys should use row-level security policies
- Environment variables should never be logged or exposed

### File Upload Security
- File type validation is implemented for uploads
- File size limits are enforced
- Temporary files are cleaned up after processing

### Data Privacy
- Resume data is processed securely
- Personal information is handled according to privacy policies
- Data retention policies are implemented

## Security Updates

Security updates will be released as patch versions and announced through:
- GitHub Security Advisories
- Release notes
- Email notifications (if subscribed)

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

- [List will be updated as reports are received]

## Contact

For any security-related questions or concerns, please contact:
- Email: [your-email@domain.com]
- GitHub: Create a private security advisory

Thank you for helping keep AI Resume Analyzer and our users safe!