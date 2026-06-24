# RR CLAN PRO - Professional Flask MVP

A black-and-white professional home and property services platform.

## Features

- Customer registration and login
- Admin login
- Technician login
- CARE CLAN, TECH CLAN, FORCE CLAN services
- Customer booking flow
- Customer booking history
- Admin dashboard
- Technician assignment
- Technician job dashboard
- Accept job, reject job, complete job
- SQLite database using SQLAlchemy
- Responsive black-and-white UI

## Setup

```bash
cd RR_CLAN_PRO_PROFESSIONAL
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Default Logins

### Admin
Email: admin@rrclanpro.com  
Password: admin123

### Technicians
Email: cleaning@rrclanpro.com  
Password: tech123

Email: plumbing@rrclanpro.com  
Password: tech123

Email: electrical@rrclanpro.com  
Password: tech123

Email: ac@rrclanpro.com  
Password: tech123

## Important

This is an MVP. For production, add:
- Real email/WhatsApp notifications
- Payment gateway
- OTP login
- Deployment security
- Environment variables
- PostgreSQL or MySQL
