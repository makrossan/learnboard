Create an import-ready CSV for my Elite Dashboard Exam system.

STRICT REQUIREMENTS:

1. The CSV structure MUST be exactly:

level,section_order,box_number,box_title,task_order,task_text

2. Structure rules:
- 5 sections total:
  - Nivel Básico
  - Nivel Intermedio
  - Nivel Avanzado
  - Nivel Experto
  - Reto Final
- section_order must be:
  1 = Nivel Básico
  2 = Nivel Intermedio
  3 = Nivel Avanzado
  4 = Nivel Experto
  5 = Reto Final
- Each level MUST contain EXACTLY 2 boxes (box_number 1 and 2).
- Each box must contain between 5–12 tasks.
- task_order must start at 1 inside each box.
- Do not skip numbers.
- No empty rows.
- No explanation text.
- Only output valid CSV.
- Do not wrap in markdown.
- Do not add commentary.
- The output language must match the topic of the exam. 

3. Task rules:
- Tasks must be practical.
- Tasks must require real command execution.
- Must include realistic repetition like a real RHCSA exam.
- Must be based ONLY on the topic I provide.
- Use clear command-style phrasing (e.g., "Configure...", "Create...", "Verify...", "Modify...").

4. Box rules:
- Box titles must reflect the difficulty of the level.
- Maintain increasing complexity per level.

Topic of the exam:
[TELL THE AI YOUR NEW TOPIC HERE]
