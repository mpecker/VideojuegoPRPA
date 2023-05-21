# VideojuegoPRPA

Instrucciones del juego:

Al comienzo, los 2 personajes(Mario y Luigi) aparecen en pantalla y constan de 5 vidas cada uno, que están representadas en la parte superior izquierda(Mario) y derecha(Luigi) de la pantalla. 

Las vidas se pierden cuando los “Bill Bala” que caen de la parte superior del mapa impactan contra los avatares y se pueden ganar recogiendo “Ups” que también precipitan de la parte superior de la pantalla.

Para esquivar los “Bill Bala” y acercarse a los “Ups” los jugadores podrán moverse únicamente de manera horizontal utilizando las flechas de dirección.

El objetivo del juego es no quedarte sin vidas. 

Para jugar(entre 2 personas),una de ellas ha de abrir en el terminal el fichero Mapa.py y, en otra ventana del terminal, el fichero Jugador.py. La otra persona abrirá en el terminal el fichero Jugador.py.

Nota1: Para que ambos jugadores puedan jugar tienen que encontrarse en el mismo directorio los 2 ficheros de python y las imágenes necesarias para el juego(el fondo, los avatares…).

Nota2: Para que puedan jugar en línea hay que cambiar la variable ip_address que aparece en ambos ficheros a la dirección IP del ordenador de la persona que ejecuta el fichero Mapa.py.

Sobre los ficheros y las clases y funciones:

Mapa.py: Servidor.
   -class Player: En ella se definen los movimientos horizontales del jugador
   -class billbala/class up: En ella se define la caída de los billbalas/ups.
   -class Game: Define qué puede hacer cada objeto dentro del juego. También mediante semáforos(Lock) se asegura de la independencia de los objetos. 
   -player(numero,conn,game): Controla que puedan jugar en red a la vez los 2 jugadores y las interacciones entre los objetos y personajes.
   -main(ip_adress): Sirve para esperar y aceptar las conexiones(Listener), y aquí se pone a dirección IP.

Jugador.py: Recibe información del servidor y la expresa en pantalla y aquí están programados los movimientos.
   -class Game: Se encarga de que cada elemento se vea en pantalla.
   -class billbalaSprite(pygame.sprite.Sprite) / class upSprite(pygame.sprite.Sprite): expresa las imágenes del billbala y el up.
   -class Display: Junta todos los elementos del juego visualmente y crea la imagen
   -main(ip_adress): Recibe la información del servidor(Client)

