# Uso:
## Docker
Si tienes Docker instalado, basta con ejecutar el siguiente comando:
```
docker compose up -d
```
Luego, ejecuta el siguiente comando para ingresar al contenedor:
```
docker compose exec -it app bash
```
Una vez dentro del contenedor, ejecuta el siguiente comando para iniciar el código:
```
python main.py
```
## Sin Docker
Instalar las librerías necesarias:
    pip install -r requirements.txt

Ejecutar el código:
    python main.py


# Input

Hay un archivo llamado "input.txt" que contiene la información del nonograma.

La primera línea indica que la matriz tiene una longitud y una altura de 10 celdas cada una. Las siguientes 10 líneas representan las pistas para las filas de la matriz, mientras que las últimas 10 líneas representan las pistas para las columnas.

Cada número en las pistas indica la cantidad de celdas que deben ser coloreadas consecutivamente en esa fila o columna, mientras que los espacios entre los números indican grupos separados de celdas coloreadas. Por ejemplo, la primera pista de la fila es "■,4", lo que significa que debe haber al menos una celda coloreada, seguida de un grupo de cuatro celdas consecutivas coloreadas. La tercera pista de la fila es "■,10", lo que indica que toda la fila debe estar coloreada. La segunda pista de la columna es "■,8", lo que indica que debe haber al menos una celda coloreada, seguida de un grupo de ocho celdas consecutivas coloreadas.

# Output

El programa imprimirá la matriz resuelta en la consola, siempre y cuando se haya puesto "yes" en la pregunta "Print results?".
Ejemplo de output:
□ □ □ ■ ■ ■ ■ □ □ □
□ ■ ■ ■ ■ ■ ■ ■ ■ □
■ ■ ■ ■ ■ ■ ■ ■ ■ ■
■ □ ■ □ ■ ■ □ ■ □ ■
■ □ ■ □ ■ ■ □ ■ □ ■
■ □ ■ ■ ■ ■ ■ ■ □ ■
□ □ ■ ■ ■ ■ ■ ■ □ □
□ □ ■ ■ □ □ ■ ■ □ □
□ □ □ ■ ■ ■ ■ □ □ □
□ □ □ □ ■ ■ □ □ □ □