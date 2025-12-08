from app import db


class News(db.Model):
    __tablename__ = 'news'
    __table_args__ = {'schema': 'dwh'}


id = db.Column(db.Integer, primary_key=True)
title = db.Column(db.String(512), nullable=False)
summary = db.Column(db.Text, nullable=True)
content = db.Column(db.Text, nullable=True)
published_at = db.Column(db.DateTime, nullable=False)
source = db.Column(db.String(256), nullable=True)
created_at = db.Column(db.DateTime, server_default=db.func.now())


def to_dict(self):
    return {
    "id": self.id,
    "title": self.title,
    "summary": self.summary,
    "published": self.published_at.isoformat() if self.published_at else None,
    "source": self.source
    }