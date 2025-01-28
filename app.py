import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Teacher database model
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    specialties = db.Column(db.String(200))
    experience = db.Column(db.Integer)
    languages = db.Column(db.String(100))
    availability = db.Column(db.String(50))
    rate = db.Column(db.Integer)
    rating = db.Column(db.Float)


# Create and initialize the database
def initialize_database():
    with app.app_context():
        db.create_all()

        # Add sample data if database is empty
        if not Teacher.query.first():
            sample_teachers = [
                Teacher(
                    name="John Math",
                    specialties="algebra, calculus, geometry",
                    experience=5,
                    languages="english, spanish",
                    availability="weekdays",
                    rate=40,
                    rating=4.9

                ),
                Teacher(
                    name="Sarah Physics",
                    specialties="mechanics, electromagnetism, calculus",
                    experience=8,
                    languages="english",
                    availability="both",
                    rate=60,
                    rating=4.8
                )
            ]
            db.session.bulk_save_objects(sample_teachers)
            db.session.commit()


# Welcome page
@app.route('/')
def welcome():
    return render_template('welcome.html')


# Student search page
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('match_teacher'))
    return render_template('index.html')


# Teacher matching results
@app.route('/match', methods=['POST'])
@app.route('/match', methods=['POST'])
def match_teacher():
    try:
        # Retrieve form data with fallback default values
        problem = request.form.get('problem', '').strip().lower()
        max_rate = request.form.get('max_rate', '50').strip()  # Default max_rate to 50
        min_experience = request.form.get('min_experience', '1').strip()  # Default to 1 year
        availability = request.form.get('availability', 'any').strip()
        language = request.form.get('language', '').strip().lower()

        # Convert numeric values safely
        max_rate = int(max_rate) if max_rate.isdigit() else 50
        min_experience = int(min_experience) if min_experience.isdigit() else 1

        # Query teacher database
        teachers = Teacher.query.all()
        matches = []

        for teacher in teachers:
            if (teacher.rate <= max_rate and
                    teacher.experience >= min_experience and
                    (availability == 'any' or teacher.availability == availability) and
                    language in teacher.languages.lower()):
                specialties = [s.strip().lower() for s in teacher.specialties.split(',')]
                match_score = len(set(problem.split()).intersection(specialties))

                if match_score > 0:
                    matches.append({
                        'teacher': teacher,
                        'score': match_score
                    })

        # Sort matches by score and rating
        matches.sort(key=lambda x: (-x['score'], -x['teacher'].rating))

        return render_template('results.html', matches=matches)
    except Exception as e:
        print(f"Error in match_teacher: {e}")
        return "An error occurred while matching teachers.", 500


# Add teacher page
@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        specialties = request.form['specialties']
        experience = int(request.form['experience'])
        languages = request.form['languages']
        availability = request.form['availability']
        rate = int(request.form['rate'])
        rating = float(request.form['rating'])

        new_teacher = Teacher(
            name=name,
            specialties=specialties,
            experience=experience,
            languages=languages,
            availability=availability,
            rate=rate,
            rating=rating
        )
        db.session.add(new_teacher)
        db.session.commit()

        return redirect(url_for('thanks', name=name))
    return render_template('add_teacher.html')


# Thank you page after adding a teacher
@app.route('/thanks')
def thanks():
    name = request.args.get('name', 'Teacher')
    return render_template('thanks.html', name=name)


# Initialize the database when the app starts
initialize_database()

if __name__ == '__main__':
    app.run(debug=True)
