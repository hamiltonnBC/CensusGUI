
# CensusConnect: Secure Census Data Access Platform

## Project Status
**⚠️ Work in Progress** - This project is currently under active development and represents an ongoing exploration of full-stack web development, security implementation, and user experience design. As of now, it is an initial exercise created to demonstrate more accessible data analysis. I have always loved the Census, but I know that working with their data is a major barrier of entry. Both frontend and backend designs were limited by being apart of school projects. I will create the full version of this application with Django and React in the future. 

## Description/Motivation

CensusConnect is a dual-purpose project that combines two primary objectives:

1. **Robust Authentication System Development**: Building a production-grade user authentication system with advanced security features
2. **Frontend Design & User Experience**: Creating an intuitive interface for accessing complex Census data

This project serves as both a technical demonstration of secure backend development and a design exploration of how to make government data more accessible through thoughtful user interface design.

### Design Process Documentation
For a detailed look at the design process, user research, and iterative development approach, visit the complete project portfolio: 
**[View Design Process & Development Blog](https://sites.google.com/view/nicholas-hamilton/project-portfolio-blog-post?authuser=1)**

CensusConnect is a secure web application designed to democratize access to American Community Survey (ACS) data while implementing robust security measures to protect user information and data access patterns. The platform features a comprehensive user authentication system that not only secures access but also enhances the user experience through personalized data management.

### Core Components:

#### Advanced Authentication System
- Multi-factor authentication
- Secure session management
- Rate limiting and brute force protection
- Admin dashboard for security monitoring
- Email verification system
- Password reset functionality with secure tokens

#### Data Access Platform
- Simplified ACS data retrieval
- Automatic variable code mapping across years
- Geographic customization options
- Interactive visualization tools
- Data export capabilities
- Collaborative features

### Project Objectives:

#### 1. Advanced Authentication System Implementation
- Multi-layered security architecture with rate limiting and brute force protection
- Session management with IP tracking and user agent validation
- Comprehensive audit logging and security monitoring
- Email verification workflows and secure password reset functionality

#### 2. User-Centered Design & Accessibility
- Intuitive interface design for complex data interactions
- Responsive design patterns and accessibility compliance
- User research-driven feature development
- Progressive enhancement for various technical skill levels

The dual nature of this project allows for exploration of both backend security architecture and frontend user experience design, making it a comprehensive full-stack development showcase.

For detailed information about the backend structure and implementation, see our [Backend Documentation](codebase/backend/backend_documentation/BACKEND_STRUCTURE.md).

### Prerequisites
This is a web application. For detailed setup instructions and requirements working with the repo, please refer to our [Setup Guide](Documentation/setupInstructions.md).

#### Quick Start Requirements:
- Python 3.10+
- PostgreSQL 12+
- Node.js 16+
- Redis (for caching)
- SendGrid API key (for email verification)

### Built With
- **Flask**: Python web framework for backend development
- **PostgreSQL**: Database for user management and data caching
- **bcrypt**: Password hashing
- **Redis**: Session management and caching
- **SendGrid**: Email service for user verification
- **D3.js**: Data visualization
- **Tailwind**: Frontend styling
- **VSCode** with Python and PostgreSQL extensions

### Author
- Nicholas Hamilton: [GitHub Profile](https://github.com/hamiltonnBC)

## Security Considerations and Acknowledgments
For a comprehensive overview of security implementations and acknowledgments, please refer to our [Security Documentation](securityConsiderations.md).

### Key Security Features:
- OWASP compliant authentication system
- Rate limiting and request throttling
- Secure session management
- SQL injection prevention
- XSS protection
- CSRF protection
- Comprehensive security logging

This project embraces security best practices while making Census data more accessible to users of all technical backgrounds. The robust authentication system ensures that data access is both secure and user-friendly.


## About the Author
Nicholas Hamilton is a software developer with a passion for data security and accessibility. With a background in computer science and cybersecurity, Nicholas has a keen interest in developing secure web applications that make complex data more accessible to users of all technical backgrounds.

