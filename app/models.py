from app import db
from datetime import datetime

class Entry(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	headword = db.Column(db.String(24))
	gloss = db.Column(db.String(24))
	pos = db.Column(db.String(12))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

	def __repr__(self):
		return f'<Entry {self.headword}>'