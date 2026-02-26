Esta app sirve para organizar y practicar lo que uno estudia.
Usted crea “libros” como CCNA, RHCSA, Linux+, SQL, dentro de cada libro crea capítulos, y dentro de cada capítulo tiene hojas de práctica con tareas, checklists y notas.
Además puede importar prácticas desde CSV, marcar progreso, guardar notas y tener todo su avance centralizado en un solo lugar.

# Despliegue con Docker

```
cd ~/learnboard
docker build -t learnboard .
docker run -p 5000:5000 -v learnboard_data:/app/instance learnboard
```

Para generar un archivo CSV que sirva para importar las prácticas en este app, utilice el siguiente prompt de IA, disponible en el archivo `aicsvprompt.md`. 
