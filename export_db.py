import csv
from app import db
from app.models import Entry

def main():
	with open('yuca_export.csv', 'w') as outfile:
		outcsv = csv.writer(outfile)
		records = db.session.query(Entry).all()
		outcsv.writerow([column.name for column in Entry.__mapper__.columns])
		for curr in records:
			outcsv.writerow([getattr(curr, column.name) for column in Entry.__mapper__.columns])

if __name__ == '__main__':
	main()