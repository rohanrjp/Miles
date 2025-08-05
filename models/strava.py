from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class StravaToken(Base):
    __tablename__ = 'strava_tokens'

    id = Column(Integer, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<StravaToken(access_token='{self.access_token}', refresh_token='{self.refresh_token}', expires_at='{self.expires_at}')>"