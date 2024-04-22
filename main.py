from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

app = Flask(__name__)
engine = create_engine('sqlite:///contacts.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contact'

    id = Column(Integer, primary_key=True)
    phoneNumber = Column(String)
    email = Column(String)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(Enum("secondary", "primary", name="link_precedence"))
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deletedAt = Column(DateTime, nullable=True)

Base.metadata.create_all(engine)

@app.route('/identify', methods=['POST'])
def identify_contact():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    session = Session()

    # Check for existing contacts
    existing_contacts = session.query(Contact).filter(
        (Contact.email == email) | (Contact.phoneNumber == phone_number)
    ).order_by(Contact.createdAt).all()

    if existing_contacts:
        # Link existing contacts
        primary_contact = existing_contacts[0]
        primary_contact_id = primary_contact.id
        emails = [c.email for c in existing_contacts]
        phone_numbers = [c.phoneNumber for c in existing_contacts]
        secondary_contact_ids = [c.id for c in existing_contacts[1:]]
    else:
        # Create a new primary contact
        primary_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkPrecedence="primary"
        )
        session.add(primary_contact)
        session.commit()
        primary_contact_id = primary_contact.id
        emails = [email]
        phone_numbers = [phone_number]
        secondary_contact_ids = []

    response = {
        "contact": {
            "primaryContatctId": primary_contact_id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_contact_ids
        }
    }

    session.close()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
