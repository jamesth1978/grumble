# Factum Humanum - Work Registration & Certification System

A Django-based platform for registering creative works (music, writing, visual art, etc.) as "created by humans" and issuing PDF certificates of authenticity at factumhumanum.org.

## Features

- **User Registration**: Creators register their information (name, email)
- **Work Registration**: Register creative works with title, category, description, and creation date
- **PDF Certificates**: Automatically generate professional PDF certificates for each registered work
- **Work Gallery**: Display recently registered works on the homepage
- **Admin Dashboard**: Manage creators and works through Django admin

## Project Structure

```
factum_humanum/
├── core/
│   ├── models.py          # Creator and Work models
│   ├── views.py           # Registration and certificate views
│   ├── forms.py           # Registration forms
│   ├── pdf.py             # PDF generation logic
│   ├── admin.py           # Admin configuration
│   └── migrations/        # Database migrations
├── templates/
│   ├── index.html         # Homepage with work gallery
│   ├── register.html      # Work registration form
│   └── certificate.html   # Certificate display page
├── static/
│   └── main.css           # Styling
├── settings.py            # Django settings
├── urls.py                # URL routing
└── manage.py              # Django management script
```

## Installation & Setup

### 1. Install Dependencies
All dependencies are listed in `requirements.txt`:
- Django 5.2.2
- reportlab (PDF generation)
- django-browser-reload
- python-decouple
- gunicorn (production)
- whitenoise (static file serving)
- dj-database-url (database URL parsing)
- psycopg2-binary (PostgreSQL)

To install:
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Migrations have already been created and applied. If you need to recreate them:
```bash
python manage.py makemigrations core
python manage.py migrate
```

### 3. Create Admin User (Optional)
To access the admin dashboard:
```bash
python manage.py createsuperuser
```

Then visit: `http://localhost:8000/admin/`

### 4. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000/`

## Usage

### For Creators
1. **Register a Work**: Click "Register Work" button on the homepage
2. **Fill in Information**:
   - Your name and email
   - Work title and description
   - Category (Music, Written Word, Visual Art, Film/Video, Other)
   - Date the work was created
3. **Get Certificate**: Receive an instant PDF certificate with registration ID
4. **Download**: Download the PDF certificate anytime from the certificate page

### For Administrators
Access `/admin/` to:
- View all registered creators
- View all registered works
- Manage creator information
- Filter works by category or registration date
- Search works by title or creator name

## Database Models

### Creator Model
- `id` (UUID): Unique identifier
- `name` (CharField): Creator's full name
- `email` (EmailField): Creator's email address
- `created_at` (DateTimeField): Registration timestamp

### Work Model
- `id` (UUID): Unique identifier
- `creator` (ForeignKey): Reference to Creator
- `title` (CharField): Work title
- `description` (TextField): Work description
- `category` (CharField): Work category (choices: music, writing, visual, film, other)
- `creation_date` (DateField): Date the work was created
- `registered_at` (DateTimeField): Registration timestamp

## URLs

| URL | Purpose |
|-----|---------|
| `/` | Homepage with work gallery |
| `/register/` | Work registration form |
| `/certificate/<work_id>/` | View certificate details |
| `/certificate/<work_id>/download/` | Download PDF certificate |
| `/admin/` | Admin dashboard |

## PDF Certificate Features

The generated PDF certificate includes:
- Official "Certificate of Creation" header
- Creator's name and email
- Work title and category
- Creation date
- Registration ID (UUID for future reference)
- Registration timestamp
- Work description
- Professional formatting with styled table layout

## Customization

### Modify Certificate Design
Edit the `pdf_generation()` function in `factum_humanum/core/pdf.py`:
- Change colors (currently uses navy blue #1f4788)
- Adjust layout and spacing
- Add your organization's logo

### Add New Work Categories
Edit the `CATEGORY_CHOICES` in the `Work` model in `factum_humanum/core/models.py`

### Customize Templates
Edit the HTML templates in `factum_humanum/templates/` to match your branding

### Update Styling
Modify the inline CSS in templates or the `main.css` file

## Production Deployment

### Environment Variables (Required for production)
Set these in your hosting platform (Render, Fly.io, Heroku, etc.):
- `SECRET_KEY`: A strong, random secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of domains (e.g., `factumhumanum.org,www.factumhumanum.org`)
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@host:port/dbname`)

### Deployment to Render
1. Push code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repo
4. Set environment variables (SECRET_KEY, ALLOWED_HOSTS=factumhumanum.org,www.factumhumanum.org, DATABASE_URL)
5. Set build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
6. Set start command: Use `Procfile` (Render will auto-detect)
7. Create a managed PostgreSQL database on Render and link it
8. Deploy!

After deployment, create a superuser via Render's shell for /admin/ access.

## Technical Details

- **Framework**: Django 5.2
- **Database**: SQLite3 (development), PostgreSQL (production)
- **PDF Library**: ReportLab 4.0.9
- **Frontend**: Bootstrap 5.1.3
- **Python Version**: 3.12+
- **Web Server**: Gunicorn (production)
- **Static Files**: WhiteNoise (production)

## Error Handling

The application includes:
- Form validation for required fields
- Email format validation
- Duplicate creator prevention (by email)
- 404 handling for invalid work IDs
- Error messages displayed on registration form

## Future Enhancements

Consider adding:
- User authentication system
- Work search/filter functionality
- Email notifications upon registration
- Multiple file uploads (images, samples)
- Work modification/update functionality
- Certificate verification system
- Statistics dashboard
- Multi-language support

## License

This project is part of the factumhumanum.org initiative.
