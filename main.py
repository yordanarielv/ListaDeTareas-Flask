from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Tarea(db.Model):          #modelo para descripcion
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
with app.app_context():         #base de datos
    db.create_all()

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect('/login')
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect('/')
    return render_template('login.html')
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@app.route('/') 
@login_required              
def inicio():
    tareas = Tarea.query.filter_by(usuario_id=current_user.id).all()
    return render_template('index.html', tareas=tareas)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    contenido = request.form['tarea']
    descripcion = request.form['descripcion']
    nueva_tarea = Tarea(contenido=contenido, descripcion=descripcion, usuario_id=current_user.id)
    db.session.add(nueva_tarea)
    db.session.commit()
    return redirect('/')

@app.route('/eliminar/<int:tarea_id>')
@login_required
def eliminar(tarea_id):
    tarea = Tarea.query.get(tarea_id)
    db.session.delete(tarea)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)