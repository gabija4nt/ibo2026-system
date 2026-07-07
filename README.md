Readme

# IBO 2026 Wellbeing & Check-in System

## Overview

This project is a web application developed for the International Biology Olympiad (IBO) 2026 to manage participant check-ins and monitor student wellbeing throughout the event.

The system is built with:
- Python
- Flask
- SQLAlchemy
- SQLite (development)
- HTML/CSS
- Chart.js

The application supports multiple user roles and is designed to be migrated to PostgreSQL for production deployment.

---

# Main Features

## Participant Check-in

Participants identify themselves using barcode IDs.

Each check-in records:
- participant
- event
- timestamp

Events can be activated/deactivated by the administrator.

---

## Wellbeing Survey

Students can submit one wellbeing survey per day.

The survey is fully dynamic.

Administrators can:
- add new questions
- edit question text
- activate/deactivate questions

Responses are stored using a normalized database structure:

Wellbeing
↓
WellbeingAnswer
↓
WellbeingQuestion

This allows questions to be changed without modifying the database schema.

---

## User Roles

### Admin

- manage participants
- import participants from CSV
- create/edit wellbeing questions
- activate/deactivate questions
- create events
- activate/deactivate events

---

### Team Leader

Can view wellbeing information only for students from their own country.

Currently displays:
- student wellbeing charts
- one chart per active wellbeing question

---

### Organizer

Dashboard with:
- participant statistics
- event statistics
- recent wellbeing submissions

---

### Guide

Can perform participant check-ins.

---

# Database

Main models:

- Participant
- Country
- User
- Event
- CheckIn
- Wellbeing
- WellbeingQuestion
- WellbeingAnswer

---

# Current Status

Implemented:

✔ Login system

✔ Role-based access

✔ CSV participant import

✔ Event management

✔ Participant check-in

✔ Dynamic wellbeing questions

✔ Dynamic wellbeing answer storage

✔ Team Leader wellbeing dashboard

✔ Organizer dashboard

---

# Planned Improvements

The following features are partially implemented or still need improvement:

## Wellbeing Dashboard

- improve chart layout
- add global average line
- improve mobile responsiveness
- hide empty charts

---

## Event Selection

Current idea:

- administrators can activate multiple events
- active events appear as recommended choices during check-in
- all events remain available in the full event list

---

## Team Leader Dashboard

Possible improvements:

- display latest wellbeing score
- display student average
- better chart styling
- highlight students with low wellbeing

---

## Deployment

Current development database:

SQLite

Production target:

PostgreSQL + Render

---

# Notes

This repository contains the current working prototype.

The architecture has recently been refactored from fixed wellbeing questions (q1, q2, q3...) to a fully dynamic question/answer model.

The current structure should be maintained, as it allows administrators to modify survey questions without changing the database schema.


# Current Development Status

The project is functional, but several features requested by the IBO organizers are still incomplete.

The following tasks should be completed before production deployment.

---

# HIGH PRIORITY

## 1. Team Leader Dashboard

Current status:
- Charts are generated dynamically based on active wellbeing questions.
- Students are filtered by the Team Leader's country.

Still required:
- Add global average line to every chart.
- Use actual survey dates on the X-axis instead of response numbers.
- Improve chart appearance (compact layout, responsive design).
- Display students side-by-side as requested by organizers.
- Hide charts for students with no wellbeing responses.
- Show summary information (latest response, average score).

---

## 2. Organizer Dashboard

Current implementation still contains parts of the old wellbeing system.

Needs refactoring to use:

Wellbeing
→ WellbeingAnswer
→ WellbeingQuestion

instead of the old q1/q2/q3 structure.

All wellbeing statistics should be generated dynamically from WellbeingAnswer.

---

## 3. Event Selection

Current:
- Events can be activated/deactivated.

Still required:

Multiple active events should be allowed.

On the Check-in page:

- active events should appear as recommended buttons
- all events should still be available in the dropdown list

---

## 4. User Management

Currently users are created manually.

Recommended implementation:

CSV import for users including:

- username
- password
- role
- country

This automatically assigns Team Leaders and Guides to their countries.

---

## 5. PostgreSQL Migration

Development currently uses SQLite.

Production deployment should use PostgreSQL.

Migration and configuration are still required.

---

# MEDIUM PRIORITY

## Wellbeing Questions

Current implementation:

✔ add question

✔ edit question

✔ activate/deactivate question

Possible improvements:

- prevent deleting questions that already contain answers
- archive inactive questions

---

## Charts

Improve styling:

- smoother lines
- colors
- responsive layout
- better mobile support

---

## General UI

Improve consistency of:

- buttons
- spacing
- dashboard layout
- responsive behaviour

---

# Notes

The wellbeing system has already been refactored.

Do NOT return to fixed q1/q2/q3 columns.

The correct architecture is:

Wellbeing
↓
WellbeingAnswer
↓
WellbeingQuestion

All future wellbeing features should continue using this model.
