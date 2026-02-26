import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Category, Book, Chapter, Sheet, Section, Box, Task, Note, TaskProgress
import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'learnboard-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learnboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Markdown filter for Jinja2
@app.template_filter('markdown')
def markdown_filter(text):
    if text:
        return markdown.markdown(text, extensions=['fenced_code', 'tables'])
    return ''

# ==================== DASHBOARD ====================
@app.route('/')
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template('index.html', categories=categories)

# ==================== CATEGORY CRUD ====================
@app.route('/categories')
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if name:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('list_categories'))
        flash('El nombre es requerido', 'error')
    return render_template('category_form.html', category=None)

@app.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if name:
            category.name = name
            category.description = description
            db.session.commit()
            flash('Categoría actualizada', 'success')
            return redirect(url_for('list_categories'))
        flash('El nombre es requerido', 'error')
    return render_template('category_form.html', category=category)

@app.route('/category/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada', 'success')
    return redirect(url_for('list_categories'))

# ==================== BOOK CRUD ====================
@app.route('/book/new', methods=['GET', 'POST'])
def new_book():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        if name and category_id:
            book = Book(name=name, description=description, category_id=int(category_id))
            db.session.add(book)
            db.session.commit()
            flash('Libro creado exitosamente', 'success')
            return redirect(url_for('index'))
        flash('Nombre y categoría son requeridos', 'error')
    return render_template('book_form.html', book=None, categories=categories)

@app.route('/book/<int:id>')
def view_book(id):
    book = Book.query.get_or_404(id)
    chapters = Chapter.query.filter_by(book_id=id).order_by(Chapter.order).all()
    return render_template('book.html', book=book, chapters=chapters)

@app.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        if name and category_id:
            book.name = name
            book.description = description
            book.category_id = int(category_id)
            db.session.commit()
            flash('Libro actualizado', 'success')
            return redirect(url_for('view_book', id=id))
        flash('Nombre y categoría son requeridos', 'error')
    return render_template('book_form.html', book=book, categories=categories)

@app.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Libro eliminado', 'success')
    return redirect(url_for('index'))

# ==================== CHAPTER CRUD ====================
@app.route('/book/<int:book_id>/chapter/new', methods=['GET', 'POST'])
def new_chapter(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        order = request.form.get('order', 1, type=int)
        if name:
            chapter = Chapter(name=name, description=description, book_id=book_id, order=order)
            db.session.add(chapter)
            db.session.commit()
            flash('Capítulo creado exitosamente', 'success')
            return redirect(url_for('view_book', id=book_id))
        flash('El nombre es requerido', 'error')
    max_order = db.session.query(db.func.max(Chapter.order)).filter_by(book_id=book_id).scalar() or 0
    return render_template('chapter_form.html', chapter=None, book=book, next_order=max_order + 1)

@app.route('/chapter/<int:id>')
def view_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    sheets = Sheet.query.filter_by(chapter_id=id).order_by(Sheet.order).all()
    return render_template('chapter.html', chapter=chapter, sheets=sheets)

@app.route('/chapter/<int:id>/edit', methods=['GET', 'POST'])
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        order = request.form.get('order', chapter.order, type=int)
        if name:
            chapter.name = name
            chapter.description = description
            chapter.order = order
            db.session.commit()
            flash('Capítulo actualizado', 'success')
            return redirect(url_for('view_chapter', id=id))
        flash('El nombre es requerido', 'error')
    return render_template('chapter_form.html', chapter=chapter, book=chapter.book, next_order=chapter.order)

@app.route('/chapter/<int:id>/delete', methods=['POST'])
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    book_id = chapter.book_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Capítulo eliminado', 'success')
    return redirect(url_for('view_book', id=book_id))

# ==================== SHEET CRUD ====================
@app.route('/chapter/<int:chapter_id>/sheet/new', methods=['GET', 'POST'])
def new_sheet(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        order = request.form.get('order', 1, type=int)
        if name:
            sheet = Sheet(name=name, chapter_id=chapter_id, order=order)
            db.session.add(sheet)
            db.session.commit()
            flash('Hoja de práctica creada exitosamente', 'success')
            return redirect(url_for('view_chapter', id=chapter_id))
        flash('El nombre es requerido', 'error')
    max_order = db.session.query(db.func.max(Sheet.order)).filter_by(chapter_id=chapter_id).scalar() or 0
    return render_template('sheet_form.html', sheet=None, chapter=chapter, next_order=max_order + 1)

@app.route('/sheet/<int:id>')
def view_sheet(id):
    sheet = Sheet.query.get_or_404(id)
    sections = Section.query.filter_by(sheet_id=id).order_by(Section.section_order).all()
    
    # Calculate progress
    total_tasks = 0
    completed_tasks = 0
    section_progress = {}
    
    for section in sections:
        section_total = 0
        section_completed = 0
        for box in section.boxes:
            for task in box.tasks:
                section_total += 1
                total_tasks += 1
                if task.progress and task.progress.completed:
                    section_completed += 1
                    completed_tasks += 1
        section_progress[section.id] = {
            'total': section_total,
            'completed': section_completed,
            'percent': round((section_completed / section_total * 100) if section_total > 0 else 0)
        }
    
    global_percent = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    return render_template('sheet.html', sheet=sheet, sections=sections, 
                         section_progress=section_progress, 
                         global_progress={'total': total_tasks, 'completed': completed_tasks, 'percent': global_percent})

@app.route('/sheet/<int:id>/edit', methods=['GET', 'POST'])
def edit_sheet(id):
    sheet = Sheet.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        order = request.form.get('order', sheet.order, type=int)
        if name:
            sheet.name = name
            sheet.order = order
            db.session.commit()
            flash('Hoja actualizada', 'success')
            return redirect(url_for('view_sheet', id=id))
        flash('El nombre es requerido', 'error')
    return render_template('sheet_form.html', sheet=sheet, chapter=sheet.chapter, next_order=sheet.order)

@app.route('/sheet/<int:id>/delete', methods=['POST'])
def delete_sheet(id):
    sheet = Sheet.query.get_or_404(id)
    chapter_id = sheet.chapter_id
    db.session.delete(sheet)
    db.session.commit()
    flash('Hoja eliminada', 'success')
    return redirect(url_for('view_chapter', id=chapter_id))

# ==================== SECTION CRUD (Inline) ====================
@app.route('/sheet/<int:sheet_id>/section/new', methods=['POST'])
def new_section(sheet_id):
    sheet = Sheet.query.get_or_404(sheet_id)
    level_name = request.form.get('level_name', '').strip()
    if level_name:
        max_order = db.session.query(db.func.max(Section.section_order)).filter_by(sheet_id=sheet_id).scalar() or 0
        section = Section(level_name=level_name, section_order=max_order + 1, sheet_id=sheet_id)
        db.session.add(section)
        db.session.commit()
        flash('Sección creada', 'success')
    return redirect(url_for('view_sheet', id=sheet_id))

@app.route('/section/<int:id>/edit', methods=['POST'])
def edit_section(id):
    section = Section.query.get_or_404(id)
    level_name = request.form.get('level_name', '').strip()
    if level_name:
        section.level_name = level_name
        db.session.commit()
        flash('Sección actualizada', 'success')
    return redirect(url_for('view_sheet', id=section.sheet_id))

@app.route('/section/<int:id>/delete', methods=['POST'])
def delete_section(id):
    section = Section.query.get_or_404(id)
    sheet_id = section.sheet_id
    db.session.delete(section)
    db.session.commit()
    flash('Sección eliminada', 'success')
    return redirect(url_for('view_sheet', id=sheet_id))

# ==================== BOX CRUD (Inline) ====================
@app.route('/section/<int:section_id>/box/new', methods=['POST'])
def new_box(section_id):
    section = Section.query.get_or_404(section_id)
    box_title = request.form.get('box_title', '').strip()
    if box_title:
        max_num = db.session.query(db.func.max(Box.box_number)).filter_by(section_id=section_id).scalar() or 0
        if max_num < 25:  # Limit to 25 boxes per section
            box = Box(box_number=max_num + 1, box_title=box_title, section_id=section_id)
            db.session.add(box)
            db.session.commit()
            flash('Box creado', 'success')
        else:
            flash('Límite de 25 boxes alcanzado', 'error')
    return redirect(url_for('view_sheet', id=section.sheet_id))

@app.route('/box/<int:id>/edit', methods=['POST'])
def edit_box(id):
    box = Box.query.get_or_404(id)
    box_title = request.form.get('box_title', '').strip()
    if box_title:
        box.box_title = box_title
        db.session.commit()
        flash('Box actualizado', 'success')
    return redirect(url_for('view_sheet', id=box.section.sheet_id))

@app.route('/box/<int:id>/delete', methods=['POST'])
def delete_box(id):
    box = Box.query.get_or_404(id)
    sheet_id = box.section.sheet_id
    db.session.delete(box)
    db.session.commit()
    flash('Box eliminado', 'success')
    return redirect(url_for('view_sheet', id=sheet_id))

# ==================== TASK CRUD (Inline) ====================
@app.route('/box/<int:box_id>/task/new', methods=['POST'])
def new_task(box_id):
    box = Box.query.get_or_404(box_id)
    task_text = request.form.get('task_text', '').strip()
    if task_text:
        max_order = db.session.query(db.func.max(Task.task_order)).filter_by(box_id=box_id).scalar() or 0
        task = Task(task_order=max_order + 1, task_text=task_text, box_id=box_id)
        db.session.add(task)
        db.session.commit()
        # Create progress entry
        progress = TaskProgress(task_id=task.id, completed=False)
        db.session.add(progress)
        db.session.commit()
        flash('Tarea creada', 'success')
    return redirect(url_for('view_sheet', id=box.section.sheet_id))

@app.route('/task/<int:id>/edit', methods=['POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    task_text = request.form.get('task_text', '').strip()
    if task_text:
        task.task_text = task_text
        db.session.commit()
        flash('Tarea actualizada', 'success')
    return redirect(url_for('view_sheet', id=task.box.section.sheet_id))

@app.route('/task/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    sheet_id = task.box.section.sheet_id
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada', 'success')
    return redirect(url_for('view_sheet', id=sheet_id))

# ==================== TASK PROGRESS ====================
@app.route('/api/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if not task.progress:
        progress = TaskProgress(task_id=task_id, completed=True)
        db.session.add(progress)
    else:
        task.progress.completed = not task.progress.completed
    db.session.commit()
    
    # Recalculate progress for the sheet
    sheet = task.box.section.sheet
    total_tasks = 0
    completed_tasks = 0
    section_progress = {}
    
    for section in sheet.sections:
        section_total = 0
        section_completed = 0
        for box in section.boxes:
            for t in box.tasks:
                section_total += 1
                total_tasks += 1
                if t.progress and t.progress.completed:
                    section_completed += 1
                    completed_tasks += 1
        section_progress[section.id] = {
            'total': section_total,
            'completed': section_completed,
            'percent': round((section_completed / section_total * 100) if section_total > 0 else 0)
        }
    
    global_percent = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    return jsonify({
        'success': True,
        'completed': task.progress.completed,
        'section_id': task.box.section.id,
        'section_progress': section_progress,
        'global_progress': {'total': total_tasks, 'completed': completed_tasks, 'percent': global_percent}
    })

# ==================== NOTES CRUD ====================
@app.route('/section/<int:section_id>/note/new', methods=['POST'])
def new_note(section_id):
    section = Section.query.get_or_404(section_id)
    content = request.form.get('content_markdown', '').strip()
    note = Note(content_markdown=content, section_id=section_id)
    db.session.add(note)
    db.session.commit()
    flash('Nota creada', 'success')
    return redirect(url_for('view_sheet', id=section.sheet_id))

@app.route('/note/<int:id>/edit', methods=['POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    content = request.form.get('content_markdown', '').strip()
    note.content_markdown = content
    db.session.commit()
    flash('Nota actualizada', 'success')
    return redirect(url_for('view_sheet', id=note.section.sheet_id))

@app.route('/note/<int:id>/delete', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    sheet_id = note.section.sheet_id
    db.session.delete(note)
    db.session.commit()
    flash('Nota eliminada', 'success')
    return redirect(url_for('view_sheet', id=sheet_id))

# ==================== CSV IMPORT ====================
@app.route('/sheet/<int:sheet_id>/import', methods=['GET', 'POST'])
def import_csv(sheet_id):
    sheet = Sheet.query.get_or_404(sheet_id)
    if request.method == 'POST':
        csv_file = request.files.get('csv_file')
        csv_text = request.form.get('csv_text', '')
        
        if csv_file and csv_file.filename:
            content = csv_file.read().decode('utf-8')
        elif csv_text:
            content = csv_text
        else:
            flash('Por favor proporcione un archivo CSV o texto CSV', 'error')
            return redirect(url_for('import_csv', sheet_id=sheet_id))
        
        try:
            reader = csv.DictReader(io.StringIO(content))
            sections_data = {}
            
            for row in reader:
                level = row.get('level', '').strip()
                section_order = int(row.get('section_order', 1))
                box_number = int(row.get('box_number', 1))
                box_title = row.get('box_title', '').strip()
                task_order = int(row.get('task_order', 1))
                task_text = row.get('task_text', '').strip()
                
                if not level or not task_text:
                    continue
                
                key = (level, section_order)
                if key not in sections_data:
                    sections_data[key] = {'level': level, 'order': section_order, 'boxes': {}}
                
                if box_number not in sections_data[key]['boxes']:
                    sections_data[key]['boxes'][box_number] = {'title': box_title, 'tasks': []}
                
                sections_data[key]['boxes'][box_number]['tasks'].append({
                    'order': task_order,
                    'text': task_text
                })
            
            # Create sections, boxes, and tasks
            for key, section_data in sections_data.items():
                # Check if section exists
                section = Section.query.filter_by(
                    sheet_id=sheet_id, 
                    level_name=section_data['level'],
                    section_order=section_data['order']
                ).first()
                
                if not section:
                    section = Section(
                        level_name=section_data['level'],
                        section_order=section_data['order'],
                        sheet_id=sheet_id
                    )
                    db.session.add(section)
                    db.session.flush()
                
                for box_num, box_data in section_data['boxes'].items():
                    if box_num > 25:
                        continue
                    
                    # Check if box exists
                    box = Box.query.filter_by(
                        section_id=section.id,
                        box_number=box_num
                    ).first()
                    
                    if not box:
                        box = Box(
                            box_number=box_num,
                            box_title=box_data['title'],
                            section_id=section.id
                        )
                        db.session.add(box)
                        db.session.flush()
                    else:
                        box.box_title = box_data['title']
                    
                    for task_data in box_data['tasks']:
                        # Check if task exists
                        task = Task.query.filter_by(
                            box_id=box.id,
                            task_order=task_data['order']
                        ).first()
                        
                        if not task:
                            task = Task(
                                task_order=task_data['order'],
                                task_text=task_data['text'],
                                box_id=box.id
                            )
                            db.session.add(task)
                            db.session.flush()
                            
                            progress = TaskProgress(task_id=task.id, completed=False)
                            db.session.add(progress)
                        else:
                            task.task_text = task_data['text']
            
            db.session.commit()
            flash('CSV importado exitosamente', 'success')
            return redirect(url_for('view_sheet', id=sheet_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al importar CSV: {str(e)}', 'error')
    
    return render_template('import_csv.html', sheet=sheet)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
