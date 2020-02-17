import flask as fl
import app
import os
import pylift
import json
from app import app, db
from app.models import Entry
from app.forms import EntryForm, UploadForm
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
	entries = Entry.query.all()
	if fl.request.method == 'POST':
		if 'delete' in fl.request.form:
			clear_data()
		fl.render_template('index.html', title='Home', entries=entries)
	return fl.render_template('index.html', title='Home', entries=entries)


@app.route('/new/', methods=['GET', 'POST'])
def new_entry():
	form = EntryForm()
	if form.validate_on_submit():
		entry_id = Entry.query.count()+1
		this_entry = Entry(id=entry_id, headword=form.headword.data, gloss=form.gloss.data, pos=form.pos.data)
		db.session.add(this_entry)
		db.session.commit()
		fl.flash(f'Entry {form.headword.data} created.')
		return fl.redirect(fl.url_for('index'))
	return fl.render_template('create_entry.html', title='New Entry', form=form)

@app.route('/import-export/', methods=['GET', 'POST'])
def import_export():
	upload_form = UploadForm()
	if upload_form.validate_on_submit():
		print(fl.request.files)
		if 'file' not in fl.request.files:
			fl.flash('No file part')
			return fl.redirect(fl.request.url)
		file = fl.request.files['file']
		if not file.filename:
			fl.flash('No selected file')
			return fl.redirect(fl.request.url)
		if file and allowed_file(file.filename, extensions=['lift']):
			filename = secure_filename(file.filename)
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)
			# convert lift file to json
			json_file = file_path.replace('.lift', '.json')
			pylift.lift_to_json(file_path, json_file)

			fl.flash(f'File {filename} uploaded')

			add_from_json(json_file)

			return fl.redirect(fl.url_for('index'))
		else:
			fl.flash('Invalid file.')
			return fl.redirect(fl.request.url)
	return fl.render_template('export_import.html', upload_form=upload_form)

def add_from_json(filename):
	with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
		new_lexicon = json.load(f)
	for key, val in new_lexicon.items():
		entry_id = Entry.query.count()+1
		print(val)
		try:
			headword = str( val['lexical-unit'] )
		except KeyError:
			headword = key.split(sep='_')[0]
		try:
			gloss = str( val['sense'][0]['gloss'] )
		except KeyError:
			gloss = 'undef'
		try:
			pos = str( val['sense'][0]['grammatical-info'] )
		except KeyError:
			pos = 'undef'
		this_entry = Entry(id=entry_id, headword=headword, gloss=gloss, pos=pos)
		db.session.add(this_entry)
	db.session.commit()


def clear_data():
	db.session.query(Entry).delete()
	db.session.commit()

def allowed_file(filename, extensions=app.config['ALLOWED_EXTENSIONS']):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions