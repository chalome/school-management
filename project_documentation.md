# Petit Enfant Grand Cœur — School Management System

This Django project supports the crèche and maternelle at Petit Enfant Grand
Cœur in Burundi. It follows the workflows and visual direction in
`stitch_preschool_management_portal/`, with working Django forms, database-backed
lists, details, authentication, and validation in place of static mock data.

## School requirements

- One Crèche class and Petite, Moyenne, and Grande Section classrooms.
- Child registration, family and pickup contacts, health history, and medical
  alerts.
- Teacher records, qualifications, classroom assignments, and emergency
  readiness information.
- Monthly fees, partial payments, late penalties, payment methods, receipts,
  and transaction references in Burundian francs (Fbu).
- Staff sign-in, profile details, password changes, and password recovery.

## Application structure

| App | Owns |
| --- | --- |
| `main/` | Project settings and root URL configuration |
| `accounts/` | Django authentication routes, staff profile, and notification preferences |
| `core/` | School years, yearly enrollments, classrooms, and the school dashboard |
| `teachers/` | Teacher records and classroom staff registry |
| `children/` | Child identity, registration, health, and related contacts |
| `payments/` | Monthly fee entries, receipt details, and payment tracking |

Authentication uses Django's built-in `User`, groups, and permissions. A
`StaffProfile` stores the staff unit, title, contact details, language, and
notification preferences. A teacher record can optionally be linked to a user
account. Accounts are created by an administrator; there is no public signup.
Operational pages require an authenticated user. Fine-grained restrictions by
staff unit or Django group have not been added yet, so any signed-in staff user
can currently access the management pages.

The navigation year selector defaults to the active school year and remembers
each user's selection for the session. The dashboard, child directory,
classroom enrollment counts, and payment register use that selected year.
Manage year date ranges and the active year in Django admin. Existing child
classroom assignments migrate to the active year; existing payments are
associated with a year based on their recorded month when possible.

## Data model

- **ClassRoom** — section, room name, assigned teacher, capacity, and active
  status. Room names are unique within a section. The initial data migration
  creates Crèche, Petite Section, Moyenne Section, and Grande Section.
- **SchoolYear** — configurable start and end dates, with one active year at a
  time. The default calendar is September 1 through June 30; new years default
  to the active year's dates shifted forward by one year.
- **ChildEnrollment** — one child/classroom/attendance-formula assignment per
  school year. The child's identity, family contacts, and health record remain
  on the permanent child record.
- **Teacher** — generated staff number, role, contact information, qualification,
  specialty, teaching languages, hire date, photo, emergency contact, and
  emergency-safety training flags.
- **Child** — generated student number, identity, birth details, family details,
  photo, vaccination and medical history,
  blood group, pediatrician, hospital, and registration date.
- **ChildContact** — one or more guardian, emergency, or authorized-pickup
  contacts per child, including relationship, phone, e-mail, and notes.
- **MonthlyFeePayment** — one fee category for a child and month, associated
  school year, amount due, amount received, late penalty, status, payment date
  and method, transaction reference, proof upload, note, and generated receipt
  number. The same child/month/category combination cannot be entered twice,
  payment amounts cannot be negative, and the received amount cannot exceed
  the due amount plus penalties. New records use a `YYYY-MM` month value with a
  dynamically populated French month/year selector; older recorded month
  values remain selectable for editing and filtering.
- **StaffProfile** — staff unit (direction, education, or accounting), title,
  phone, interface language, and alert preferences.

## Ported Stitch screens

| Screen / workflow | URL |
| --- | --- |
| Administrative sign-in | `/accounts/login/` |
| School dashboard and classroom summary | `/` |
| Child directory, search, class filter, medical alerts | `/children/` |
| New child admission | `/children/add/` |
| Child electronic record | `/children/<id>/` |
| Edit child record | `/children/<id>/edit/` |
| Fee and payment register | `/payments/` |
| Record a fee payment | `/payments/add/` |
| Payment receipt details and print view | `/payments/<id>/` |
| Classroom list and teacher assignments | `/classrooms/` |
| Add or edit a classroom | `/classrooms/add/`, `/classrooms/<id>/edit/` |
| Teacher register, add, view, and edit | `/teachers/`, `/teachers/add/`, `/teachers/<id>/`, `/teachers/<id>/edit/` |
| Staff profile and alert preferences | `/accounts/profile/` |
| Password change and recovery | `/accounts/password_change/`, `/accounts/password_reset/` |

Templates use a shared responsive portal layout and the Stitch palette. Child
and teacher pages expose the registration, detail, and edit workflows;
classroom and payment screens use live database data. Browser print is available
for child records and payment receipts.

The Stitch exports also show capabilities such as PDF/Excel exports, two-factor
authentication, a connection audit log, and live notification delivery. Those
are visual references only at this stage and are not represented as active
features. Alert preferences are stored for future notification delivery.

## Local setup

From the project directory:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `/accounts/login/` to sign in. The development default sends password-reset
messages to the console. Configure `EMAIL_BACKEND` and the normal Django e-mail
settings before using password recovery in a deployed environment. Uploaded
child and teacher photos and payment proof files are stored under `media/`.

Run the model and page checks with:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test accounts core children teachers payments
```
