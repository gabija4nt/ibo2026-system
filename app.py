from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import csv
import io

app = Flask(__name__)
app.secret_key = 'ibo2026secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ibo.db'
db = SQLAlchemy(app)

# --- MODELS (database tables) ---

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nfc_id = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, guide, leader, organizer
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country', backref='participants')

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref='checkins')
    event_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Wellbeing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    participant = db.relationship('Participant', backref='wellbeing')
    q1 = db.Column(db.Integer)  # 1-5
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=False)

# --- PAGES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    message = None
    participant = None

    active_event = Event.query.filter_by(active=True).first()

    if request.method == 'POST':
        nfc_id = request.form.get('nfc_id')
        event = active_event.name if active_event else "No Active Event"
        participant = Participant.query.filter_by(nfc_id=nfc_id).first()
        if participant:
            entry = CheckIn(participant_id=participant.id, event_name=event)
            db.session.add(entry)
            db.session.commit()
            message = f'✅ {participant.name} successfully checked in!'
        else:
            message = '❌ Participant not found'
    return render_template('checkin.html', message=message, participant=participant, active_event=active_event)

@app.route('/wellbeing', methods=['GET', 'POST'])
def wellbeing():
    message = None
    if request.method == 'POST':
        nfc_id = request.form.get('nfc_id')
        participant = Participant.query.filter_by(nfc_id=nfc_id).first()
        if participant:
            today = date.today()

            existing_entry = Wellbeing.query.filter_by(
                participant_id=participant.id
            ).all()

            already_submitted = False

            for entry in existing_entry:
                if entry.timestamp.date() == today:
                    already_submitted = True
                    break

            if already_submitted:
                message = "⚠️ Wellbeing survey already submitted today."
            
            else:
                entry = Wellbeing(
                    participant_id=participant.id,
                    q1=request.form.get('q1'),
                    q2=request.form.get('q2'),
                    q3=request.form.get('q3')
                )

                db.session.add(entry)
                db.session.commit()
            
                message = f'✅ {participant.name} wellbeing recorded!'

        else:
            message = '❌ Participant not found'
    return render_template('wellbeing.html', message=message)

@app.route('/dashboard')
def dashboard():
    checkins = CheckIn.query.order_by(CheckIn.timestamp.desc()).limit(20).all()
    total_participants = Participant.query.count()
    total_checkins = CheckIn.query.count()
    active_event = Event.query.filter_by(active=True).first()

    events = Event.query.all()

    event_stats = []

    for event in events:
        count = CheckIn.query.filter_by(
            event_name=event.name
        ).count()

        event_stats.append({
            'name': event.name,
            'count': count,
            'active': event.active
        })

    wellbeing_entries = Wellbeing.query.all()

    valid_q1 = [int(w.q1) for w in wellbeing_entries if w.q1 is not None]

    if valid_q1:
        avg_wellbeing = round(
            sum(valid_q1) / len(valid_q1),
            2
        )
    else:
        avg_wellbeing = 0

    avg_q1 = 0
    avg_q2 = 0
    avg_q3 = 0

    if wellbeing_entries:
        avg_q1 = round(
            sum(int(w.q1) for w in wellbeing_entries if w.q1 is not None),
            2
        )

        avg_q2 = round(
            sum(int(w.q2) for w in wellbeing_entries if w.q2 is not None),
            2
        )

        avg_q3 = round(
            sum(int(w.q3) for w in wellbeing_entries if w.q3 is not None),
            2
        )
    return render_template(
        'dashboard.html',
        checkins=checkins,
        total=total_participants, total_checkins=total_checkins,
        avg_q1=avg_q1,
        avg_q2=avg_q2,
        avg_q3=avg_q3,
        wellbeing_count=len(wellbeing_entries),
        active_event=active_event,
        event_stats=event_stats,
        avg_wellbeing=avg_wellbeing,
    )

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        if request.form.get('activate_event'):

            event_id = request.form.get('activate_event')

            Event.query.update({'active': False})

            event = Event.query.get(event_id)

            if event:
                event.active = True
                db.session.commit()

            return redirect(url_for('admin'))

        if request.form.get('create_event'):

            event_name = request.form.get('event_name')

            if event_name:
                event = Event(name=event_name)
                db.session.add(event)
                db.session.commit()

            return redirect(url_for('admin'))

        if request.form.get('import_csv'):

            file = request.files.get('csv_file')

            if file:
                stream = io.StringIO(file.stream.read().decode("UTF8"))
                reader = csv.DictReader(stream)

                imported_count = 0
                skipped_count = 0

                for row in reader:
                    existing = Participant.query.filter_by(
                        nfc_id=row['nfc_id']
                    ).first()

                    if existing:
                        skipped_count += 1
                        continue

                    country_name = row['country']

                    country = Country.query.filter_by(name=country_name).first()

                    if not country:
                        country = Country(name=country_name)
                        db.session.add(country)
                        db.session.commit()

                    participant = Participant(
                        name=row['name'],
                        nfc_id=row['nfc_id'],
                        role=row['role'],
                        country_id=country.id
                    )

                    db.session.add(participant)
                    imported_count += 1

                db.session.commit()
                flash(
                    f"Import completed. Imported: {imported_count}, Skipped duplicates: {skipped_count}",
                    "success"
                )

            return redirect(url_for('admin'))

        name = request.form.get('name')
        nfc_id = request.form.get('nfc_id')
        role = request.form.get('role')
        country_name = request.form.get('country')

        country = Country.query.filter_by(name=country_name).first()

        if not country:
            country = Country(name=country_name)
            db.session.add(country)
            db.session.commit()

        p = Participant(
            name=name,
            nfc_id=nfc_id,
            role=role,
            country_id=country.id
        )

        db.session.add(p)
        db.session.commit()

    participants = Participant.query.all()
    events = Event.query.all()

    return render_template(
        'admin.html',
        participants=participants,
        events=events
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
