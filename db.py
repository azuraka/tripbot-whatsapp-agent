from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///trip_agent.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    group_id = Column(String)
    amount = Column(Integer)
    description = Column(String)
    paid_by = Column(String)


Base.metadata.create_all(engine)


def save_expense(group_id, expense):
    session = Session()
    row = Expense(
        group_id=group_id,
        amount=expense["amount"],
        description=expense["description"],
        paid_by=expense["paid_by"],
    )
    session.add(row)
    session.commit()
    session.close()


def get_group_total(group_id):
    session = Session()
    total = sum(x.amount for x in session.query(Expense).filter_by(group_id=group_id).all())
    session.close()
    return total
