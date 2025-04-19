# AI-CV: Smart Resume Analysis & Job Matching Platform

AI-CV is a comprehensive platform for resume analysis, skills extraction, and job matching. The system leverages AI to analyze resumes, extract skills, and suggest matching job opportunities based on candidates' profiles.

## Overview

The AI-CV platform provides powerful tools for both job seekers and recruiters:

- **Automated Resume Analysis**: Extract key information, skills, and experience from uploaded resumes
- **Skill Matching**: Identify and categorize technical, soft, and language skills from resume content
- **Job Listing Management**: Create, search, and manage job listings
- **Smart Matching**: Connect candidates with relevant job opportunities based on skill alignment
- **User Management**: Different roles for job seekers, recruiters, and administrators

## Architecture

The platform is built using a modern microservices architecture:

![Docker Containers](/AI-CV/frontend/src/assets/docker.png)

- **Web Backend**: Django REST Framework serving the API
- **Databases**:
  - MySQL: Primary relational database for user data, job listings, etc.
  - MongoDB: Document store for analyzed resume content
  - PostgreSQL: Supporting database for specific features
- **Redis**: Caching and real-time features
- **Celery**: Background task processing for resume analysis
- **Celery Beat**: Scheduled tasks and periodic operations

## API Documentation

The platform provides a comprehensive API for integration with frontend applications or third-party services:

![API Overview](/AI-CV/frontend/src/assets/1-part-swagger.png)
![API Overview](/AI-CV/frontend/src/assets/2-part-swagger.png)
![API Overview](/AI-CV/frontend/src/assets/3-part-swagger.png)


## Admin Interface

The platform includes a powerful administrative interface for managing users, resumes, and job listings:

![Admin Interface](/AI-CV/frontend/src/assets/django-admin.png)

## Key Features

- **Resume Parsing**: Extract text and structure from PDF, DOCX, and DOC files
- **Skills Identification**: Automatically identify technical skills, soft skills, and languages
- **Resume Scoring**: Evaluate resumes based on completeness, formatting, and content
- **Job Matching Algorithm**: Match candidates to jobs based on skills, experience, and other factors
- **Company Profiles**: Allow companies to create profiles and post job listings
- **User Roles**: Different permissions for job seekers, recruiters, and administrators

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Databases**: MySQL, MongoDB, PostgreSQL
- **Task Processing**: Celery, Redis
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Text Analysis**: NLTK, custom NLP algorithms
- **Container Orchestration**: Docker, Docker Compose

## Getting Started

1. Clone the repository
2. Run `docker-compose up -d` to start all services
3. Access the API documentation at http://localhost:8000/api/docs/
4. Access the admin interface at http://localhost:8000/admin/

## License

This project is licensed under the MIT License - see the LICENSE file for details.
