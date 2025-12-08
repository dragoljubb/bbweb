from app import db

def bulk_insert(model, rows):
    if not rows:
        return 0
        objs = [model(**r) for r in rows]
        db.session.bulk_save_objects(objs)
        db.session.commit()
        return len(objs)