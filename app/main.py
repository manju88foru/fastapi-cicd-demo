from fastapi import FastAPI, Depends, Form
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.responses import HTMLResponse
import time

DATABASE_URL = "postgresql://postgres:postgres@db:5432/appdb"

# wait for database to be ready
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        break
    except:
        print("Waiting for database...")
        time.sleep(3)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    users = db.query(User).all()

    html = """
    <h1>My DevOps Demo Application</h1>
    <form method="post" action="/add">
        <input name="name" placeholder="Enter name"/>
        <button>Add</button>
    </form>
    <h2>Saved Users</h2>
    <ul>
    """

    for u in users:
        html += f"<li>{u.name}</li>"

    html += "</ul>"
    return html

@app.post("/add")
def add_user(name: str = Form(...), db: Session = Depends(get_db)):
    user = User(name=name)
    db.add(user)
    db.commit()
    return {"status": "added"}