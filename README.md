# Bruno Health Tracker

A Django web application for tracking canine lymphoma treatment quality-of-life metrics. Designed for mobile-first use by family members caring for a dog undergoing cancer treatment.

## Features

- **Daily Health Tracking** - Record quality-of-life metrics including mood, appetite, energy, and comfort levels
- **Medication Management** - Track medications and record doses given
- **Lymph Node Measurements** - Monitor node sizes over time
- **History & Trends** - View weekly summaries and track progress
- **Multi-User Support** - Multiple family members can log in and track simultaneously

## Tech Stack

- Django 6.0
- PostgreSQL (Docker) / SQLite (development)
- Mobile-first responsive design
- Docker & Docker Compose

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nestorwheelock/bruno.git
cd bruno

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Docker Deployment

```bash
docker-compose up -d
```

The app will be available at `http://localhost:8000`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=health --cov-report=term-missing
```

Current test coverage: **99%**

## Project Structure

```
bruno/
├── brunosite/          # Django project settings
├── health/             # Main health tracking app
│   ├── models.py       # DailyEntry, Medication, MedicationDose, LymphNodeMeasurement
│   ├── views.py        # All views (tracker, medications, nodes, history)
│   ├── urls.py         # URL routing
│   └── tests.py        # Comprehensive test suite (60 tests)
├── fundraiser/         # Public fundraising page
├── templates/          # HTML templates
├── static/             # Static assets
└── docker-compose.yml  # Docker configuration
```

## Health Metrics Tracked

### Daily Quality of Life
- Tail/body language (0-5)
- Interest in people (0-5)
- Interest in environment (0-5)
- Enjoyment of favorites (0-5)
- Overall spark/joy (0-5)

### Appetite & Eating
- Appetite level (0-5)
- Food enjoyment (0-5)
- Nausea signs (0-5)
- Weight/body condition (0-5)
- Meals eaten (breakfast, lunch, dinner, treats)

### Energy & Mobility
- Energy level (0-5)
- Willingness to move (0-5)
- Walking comfort (0-5)
- Resting comfort (0-5)

### Comfort & Pain
- Breathing comfort (0-5)
- Pain signs (0-5)
- Sleep quality (0-5)
- Response to touch (0-5)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
