from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Training(Base):
    """Training Dataset"""

    __tablename__ = "training"
    id = Column(Integer(), primary_key=True)
    text = Column(String(500), nullable=False)
    label = Column(Integer(), nullable=False)

    def __repr__(self):
        return f"text: {self.text}, label: {self.label}"


class StopWords(Base):
    """stop words"""

    __tablename__ = "stop_words"
    id = Column(Integer(), primary_key=True)
    content = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"text: {self.content}"


class Prior(Base):
    """Logprior"""

    __tablename__ = "prior"
    id = Column(Integer(), primary_key=True)
    logprior = Column(Float(), nullable=False)

    def _repr_(self):
        return f"logprior: {self.logprior}"


class Likelihood(Base):
    """Loglikelihood"""

    __tablename__ = "likelihoods"
    id = Column(Integer(), primary_key=True)
    text = Column(String(500), nullable=False)
    loglikelihood = Column(Float(), nullable=False)

    def __repr__(self):
        return f"text: {self.text}, likelihood: {self.loglikelihood}"
