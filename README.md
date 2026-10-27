
# Retrieve — Lost & Found Platform

<p align="center">
  <strong>Lost something? Find your way back.</strong>
  <br />
  A smart, community-driven platform that helps people report, discover, and recover lost belongings.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-Backend-black?logo=flask" alt="Flask" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/HTML5-Frontend-E34F26?logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-Responsive-1572B6?logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/Status-Development-orange" alt="Project status" />
</p>

---

## Overview

Retrieve is a web-based lost-and-found management platform built with Python, Flask, and MySQL.

It provides a centralized place where users can report lost belongings, publish found-item listings, discover potentially matching items, communicate with other users, and submit ownership claims.

Instead of relying entirely on scattered social media posts or physical notice boards, Retrieve organizes reports and recovery workflows in one platform.

The project combines a responsive user interface with a relational database, account management, item discovery, claim handling, and administrative moderation.

## Problem Statement

Losing personal belongings can be stressful. Finding them often depends on whether the right person sees a social media post or a notice at the right time.

Common problems include:

- Lost and found reports being scattered across different platforms.
- Difficulty identifying matching items.
- No centralized claim-verification workflow.
- Limited communication between the person who found an item and its owner.
- Lack of visibility into reports and recovery activity.

Retrieve addresses these problems by bringing the reporting, discovery, communication, and recovery process together.

## Key Features

### 1. User Authentication
- User registration and login.
- Secure password hashing.
- Session-based access to authenticated features.
- Role-based access for administrative functions.

### 2. Lost and Found Reports
- Create lost-item and found-item reports.
- Add item names, descriptions, categories, dates, and locations.
- Upload item photographs.
- View item details and listing status.
- Manage personal listings.

### 3. Item Search and Discovery
- Browse available reports.
- Search for items using relevant keywords.
- Filter listings by categories and item type.
- View detailed information about reported belongings.

### 4. Smart Item Matching
- Compare lost and found reports.
- Evaluate similarities using item categories, descriptions, locations, and dates.
- Rank potential matches using a matching score.
- Help users discover reports that may relate to their missing belongings.

> The current matching approach is rule-based. It does not guarantee that two reports refer to the same physical item.

### 5. Ownership Claims
- Submit a claim for a found item.
- Provide an explanation to support ownership.
- Allow the listing reporter to review claims.
- Approve or reject claims.
- Track claim status and item recovery progress.

### 6. Private Messaging
- Enable communication between eligible users involved in a claim.
- Discuss item details and arrange recovery.
- Restrict conversations according to the application's claim-access rules.

### 7. Notifications
- Notify users about relevant item matches.
- Provide claim-related updates.
- Display notifications about new messages and other supported activities.

### 8. User Dashboard
- View personal listings.
- Track submitted claims.
- Review incoming claim requests.
- Access matching results and notifications.
- Manage item recovery workflows.

### 9. Admin Dashboard
- View platform activity and basic statistics.
- Review item listings and claims.
- Moderate inappropriate listings.
- Hide or restore listings when necessary.

### 10. Responsive User Interface
- Mobile-friendly layouts.
- Consistent navigation and reusable components.
- Loading indicators and form feedback.
- Custom error pages.
- Optimized image handling for supported uploads.
- Custom favicon and `robots.txt`.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend web framework |
| MySQL | Relational database |
| SQLAlchemy | Database interaction and ORM, if configured in the current version |
| HTML5 | Page structure |
| CSS3 | Styling, layouts, animations, and responsiveness |
| JavaScript | Client-side interactions |
| Werkzeug | Password hashing and web utilities |
| Pillow | Image processing, if included in the current requirements |

**Architecture:** Flask handles application routes, authentication, business logic, and database operations. MySQL stores application records, while HTML, CSS, and JavaScript provide the user interface.

## Project Structure

The exact files may vary by version. A typical structure is:

```text
Retrieve/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── item_detail.html
│   ├── report_item.html
│   ├── notifications.html
│   ├── messages.html
│   ├── admin.html
│   └── errors/
│       ├── 400.html
│       ├── 403.html
│       ├── 404.html
│       ├── 405.html
│       ├── 413.html
│       └── 500.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   ├── images/
│   ├── uploads/
│   └── favicon.ico
│
└── tests/
```

Refer to the actual repository for the authoritative directory structure.

---

## Getting Started

### Prerequisites

Install the following software:

- Python 3.10 or newer.
- MySQL Server.
- MySQL Workbench (recommended).
- Git.
- Visual Studio Code or another Python editor.

### 1. Clone the Repository

Replace the example URL with your GitHub repository URL.

```bash
git clone https://github.com/YOUR_USERNAME/Retrieve.git
cd Retrieve
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python executable directly or adjust the execution policy for the current terminal session.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure MySQL

Start MySQL Server and open MySQL Workbench.

Create the database and a dedicated application user:

```sql
CREATE DATABASE retrieve_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'retrieve_user'@'localhost'
IDENTIFIED BY 'CHANGE_THIS_TO_A_STRONG_PASSWORD';

GRANT ALL PRIVILEGES ON retrieve_db.*
TO 'retrieve_user'@'localhost';

FLUSH PRIVILEGES;
```

If the database or user already exists, reuse the existing resources and update permissions or credentials as required. Do not drop an existing database merely to install the application.

### 5. Configure Environment Variables

Copy the example environment file:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Update `.env` with the values required by your application.

For example:

```dotenv
SECRET_KEY=replace_with_a_long_random_secret
DATABASE_URL=mysql+pymysql://retrieve_user:YOUR_PASSWORD@localhost/retrieve_db
```

Replace the sample credentials with your own values.

If your database password contains URL-special characters, encode them correctly in the connection URL.

Never commit `.env` or real credentials to GitHub.

### 6. Initialize the Database

If the application provides the Flask CLI command shown below, run:

```bash
flask --app app init-db
```

This should create the required database tables when implemented using the application's database initialization logic.

If your version uses a different initialization command or database migration system, follow the commands defined in its source code and documentation.

### 7. Run the Application

```bash
flask --app app run --debug
```

Open the following address in your browser:

http://127.0.0.1:5000

The development server must remain running while you use the application.

Press `Ctrl + C` in the terminal to stop it.

---

## Database Overview

The database supports the main entities required for a lost-and-found workflow.

| Entity | Purpose |
|---|---|
| Users | Account details, authentication information, and roles |
| Items | Lost and found reports |
| Claims | Ownership claim requests and their statuses |
| Item Matches | Potential matches between lost and found reports |
| Notifications | User-facing activity alerts |
| Messages | Conversations associated with eligible claims |

The actual table names, columns, relationships, and constraints depend on the current database models.

### Typical Workflow

1. A user registers or logs in.
2. The user submits a lost-item report or a found-item report.
3. Retrieve stores the report in MySQL.
4. The matching logic identifies potentially related reports.
5. Users review relevant listings and submit ownership claims.
6. The listing reporter reviews the claim.
7. Eligible users communicate through the messaging system.
8. The item is marked as recovered when the workflow is completed.

---

## Security and Privacy

Retrieve should be configured to follow these security practices:

- Store passwords using secure password hashing.
- Keep secrets and database credentials in environment variables.
- Enforce authorization checks on protected routes.
- Validate and sanitize user-submitted data.
- Restrict uploaded file types and sizes.
- Protect state-changing forms against cross-site request forgery (CSRF).
- Use secure session-cookie settings in production.
- Avoid exposing private user information in public listings.
- Apply rate limiting to authentication and other abuse-prone endpoints.
- Use HTTPS for public deployments.
- Back up the database regularly.

Uploaded item photographs may contain sensitive information. Image processing should remove embedded metadata where appropriate.

**Production readiness:** The presence of security-related features does not by itself establish that the application has undergone a security audit. Verify the implemented controls before deploying publicly.

## Error Handling

The application includes custom error pages for supported HTTP errors, such as:

- `400` — Bad Request
- `403` — Forbidden
- `404` — Page Not Found
- `405` — Method Not Allowed
- `413` — Uploaded File Too Large
- `500` — Internal Server Error

Production error pages should display helpful messages without exposing stack traces, database credentials, or internal implementation details.

## Search Engine Configuration

Retrieve includes a `robots.txt` file to communicate crawler preferences.

Example:

```text
User-agent: *
Disallow: /dashboard
Disallow: /admin
Disallow: /messages
Disallow: /notifications

Sitemap: https://YOUR_DOMAIN/sitemap.xml
```

Replace `YOUR_DOMAIN` with the deployed domain and publish a sitemap only if the application actually provides one.

`robots.txt` is not an access-control mechanism. Private pages must remain protected by server-side authentication and authorization.

## Testing Checklist

Before deploying a new version, verify the following:

- [ ] User registration, login, and logout.
- [ ] Passwords are hashed correctly.
- [ ] Lost and found reports can be created and viewed.
- [ ] Search and category filters work.
- [ ] Image uploads validate file type and size.
- [ ] Matching results are generated correctly.
- [ ] Claims can be submitted and reviewed.
- [ ] Unauthorized users cannot access private messages.
- [ ] Notifications display the correct events.
- [ ] Admin-only routes reject ordinary users.
- [ ] Error pages render correctly.
- [ ] The interface works on mobile and desktop.
- [ ] Horizontal overflow is absent on supported screen sizes.
- [ ] Database records persist after restarting the application.

## Current Limitations

The following capabilities may require additional work depending on the current implementation:

- Matching is rule-based rather than a trained machine-learning model.
- Email and push notifications require external delivery services.
- Real-time messaging may require WebSockets or periodic polling.
- Maps and location-based distance calculations require appropriate location data and mapping services.
- Production deployment requires hosted infrastructure, HTTPS, backups, monitoring, and security hardening.

Only advertise a feature as fully implemented after testing it in the running application.

## Future Improvements

Potential improvements include:

- Image similarity matching.
- More advanced location-based discovery.
- Email notifications and notification preferences.
- Real-time messaging.
- Stronger claim-verification workflows.
- Automated tests and continuous integration.
- Accessibility improvements.
- Analytics for item recovery and platform usage.
- Cloud deployment and production monitoring.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the affected functionality.
5. Submit a pull request describing the changes.

Please avoid committing credentials, personal information, uploaded user photographs, or local database files.

## License

Choose a license before publishing the project for reuse. If you intend to use the MIT License, add a `LICENSE` file containing the appropriate license text.

---

## Author

**Preet Dutta**

GitHub: https://github.com/preetdutta0409-cell

Project: Retrieve — Lost & Found Platform

Built to make reporting, discovering, and recovering lost belongings easier through a centralized digital platform.
