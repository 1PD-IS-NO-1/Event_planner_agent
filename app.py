from flask import Flask, render_template, request, jsonify
from markupsafe import Markup
from werkzeug.utils import secure_filename
import os
from event_planner import run_event_planning_workflow
import markdown
app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def index():
    return render_template('index.html')

@app.template_filter('markdown')
def markdown_filter(text):
    if text is None:
        return ""
    # Convert markdown to HTML with extension for tables
    md = markdown.Markdown(extensions=['tables'])
    return Markup(md.convert(text))

@app.route('/plan_event', methods=['POST'])
def plan_event():
    try:
        event_details = {
            'event_topic': request.form['event_topic'],
            'event_description': request.form['event_description'],
            'event_city': request.form['event_city'],
            'tentative_date': request.form['tentative_date'],
            'expected_participants': int(request.form['expected_participants']),
            'budget': float(request.form['budget']),
            'venue_type': request.form['venue_type']
        }
        
        results = run_event_planning_workflow(event_details)
        return render_template('results.html', results=results, event_details=event_details)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)