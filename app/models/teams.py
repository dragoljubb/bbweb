from app import db


class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'schema': 'dwh'}


team_id = db.Column(db.Integer, primary_key=True)
code = db.Column(db.String(16), nullable=True)
name = db.Column(db.String(128), nullable=False)
city = db.Column(db.String(128), nullable=True)
created_at = db.Column(db.DateTime, server_default=db.func.now())


def to_dict(self):
    return {
    "team_id": self.team_id,
    "code": self.code,
    "name": self.name,
    "city": self.city
    }