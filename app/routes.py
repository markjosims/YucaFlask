import flask as fl
from app import app, db
from app.models import Entry
from app.forms import EntryForm

@app.route('/')
@app.route('/index')
def index():
	entries = Entry.query.all()
	return fl.render_template('index.html', title='Home', entries=entries)


@app.route('/new', methods=['GET', 'POST'])
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