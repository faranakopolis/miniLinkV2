from db import models
from db.session import SessionLocal


def store_guest_url_info(visitor_info, hashed_url):
    """This function is used for parsing the visitor request, separate its different data
        in order to store them in the tables below:
        - visitor
        - url_visitor
    """
    db = SessionLocal()
    db_url = db.query(models.Url).filter(models.Url.hashed == hashed_url).one_or_none()
    if not db_url:
        return None
    # Check if the visitor exists in the table or not
    db_visitor = db.query(models.Visitor).filter(models.Visitor.ip == visitor_info['ip'],
                                                 models.Visitor.os == visitor_info['os'],
                                                 models.Visitor.device == visitor_info['device'],
                                                 models.Visitor.browser == visitor_info['browser']).one_or_none()

    if db_visitor:
        # Store data just in the visitor_url table
        url_visitor = models.UrlVisitor(url=db_url,
                                        visitor=db_visitor)
        db.add(url_visitor)
        db.commit()
    else:
        # This visitor is new, store it in its table first
        new_visitor = models.Visitor(ip=visitor_info['ip'],
                                     device=visitor_info['device'],
                                     os=visitor_info['os'],
                                     browser=visitor_info['browser'])
        db.add(new_visitor)
        db.commit()
        url_visitor = models.UrlVisitor(url=db_url,
                                        visitor=db_visitor)
        db.add(url_visitor)
        db.commit()
