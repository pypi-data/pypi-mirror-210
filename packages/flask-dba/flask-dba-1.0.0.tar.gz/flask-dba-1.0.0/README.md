# Flask DBA
## Flask DBA is a Flask extension that provides a simple interface for interacting with databases.
### Installation
```bash
pip install flask-dba
```
### Basic Usage
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_dba import FlaskDBA

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
dba = FlaskDBA(app, db)
dba.init_usuario()
dba.init_permissions(
    with_usuario=True
)
```
