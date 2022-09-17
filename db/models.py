import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship

from session import Base


class Url(Base):
    __tablename__ = "url"

    id = Column(BigInteger, primary_key=True, index=True)
    original = Column(String, nullable=False)
    hashed = Column(String, unique=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now())
    is_active = Column(Boolean, default=True)

    url_visitors = relationship("UrlVisitor", back_populates="url")


class Visitor(Base):
    __tablename__ = "visitor"

    id = Column(BigInteger, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    device = Column(String)
    browser = Column(String)
    os = Column(String)
    created_at = Column(TIMESTAMP)

    url_visitors = relationship("Item", back_populates="visitor")


class UrlVisitor(Base):
    __tablename__ = "url_visitor"

    id = Column(BigInteger, primary_key=True, index=True)
    url_id = Column(BigInteger, ForeignKey("url.id"))
    visitor_id = Column(BigInteger, ForeignKey("visitor.id"))
    created_at = Column(TIMESTAMP)

    url = relationship("Url", back_populates="url_visitors")
    visitor = relationship("Visitor", back_populates="url_visitors")
