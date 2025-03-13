# Nirapod Tika - Vaccine Management Web App

Nirapod Tika is a web-based vaccine management system built using Django REST Framework (DRF). It provides an API-based architecture to manage vaccination campaigns, patient records, doctor profiles, and vaccination schedules. The application also includes JWT authentication using Djoser and API documentation via DRF YASG.

## Features

- **User Authentication:** JWT authentication with Djoser.
- **Doctor Profiles:** Manage doctor details and credentials.
- **Patient Profiles:** Store patient information and vaccination history.
- **Vaccination Schedules:** Schedule vaccinations for registered patients.
- **Vaccine Campaigns:** Manage and track large-scale vaccination campaigns.
- **Vaccine Management:** Keep records of available vaccines.
- **API Documentation:** Interactive Swagger UI using DRF YASG.

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Authentication:** JWT via Djoser
- **Database:** SQLite/PostgreSQL
- **Documentation:** DRF YASG (Swagger UI)
- **Python Version:** 3.8+

## Installation Guide

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/nirapod-tika.git
   cd nirapod-tika
   ```
2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```
5. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   The API will be accessible at `http://127.0.0.1:8000/`.

6. **Access API Documentation**
   Visit Swagger UI at:
   ```
   http://127.0.0.1:8000/swagger/
   ```

## API Endpoints

### Authentication
- **POST** `/auth/jwt/create/` - Obtain JWT token (Login)
- **POST** `/auth/jwt/refresh/` - Refresh JWT token
- **POST** `/auth/jwt/verify/` - Verify JWT token

### Doctor Profiles
- **GET** `/doctor-profile/` - Retrieve doctor profiles
- **POST** `/doctor-profile/` - Create a new doctor profile
- **PUT** `/doctor-profile/{id}/` - Update doctor profile

### Patient Profiles
- **GET** `/patient-profile/` - Retrieve patient profiles
- **POST** `/patient-profile/` - Create a new patient profile
- **PUT** `/patient-profile/{id}/` - Update patient profile

### Vaccination Schedules
- **GET** `/vaccination-schedules/` - Get schedules
- **POST** `/vaccination-schedules/` - Create a schedule
- **PUT** `/vaccination-schedules/{id}/` - Update schedule

### Vaccine Campaigns
- **GET** `/vaccine-campaign/` - Retrieve campaigns
- **POST** `/vaccine-campaign/` - Create a new campaign
- **PUT** `/vaccine-campaign/{id}/` - Update campaign

### Vaccines
- **GET** `/vaccines/` - Get vaccine details
- **POST** `/vaccines/` - Add a new vaccine
- **PUT** `/vaccines/{id}/` - Update vaccine info

## Running Tests
To run tests, use:
```bash
python manage.py test
```

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

