-- ============================================================
--  BOOKSHELF — Base de datos completa
-- ============================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS bookshelf
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bookshelf;

-- ── Eliminar tablas si existen (orden por dependencias) ───
DROP TABLE IF EXISTS `user_books`;
DROP TABLE IF EXISTS `books`;
DROP TABLE IF EXISTS `users`;

-- ── Usuarios ──────────────────────────────────────────────
CREATE TABLE `users` (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `username`   VARCHAR(80)  NOT NULL,
  `email`      VARCHAR(120) NOT NULL,
  `password`   VARCHAR(64)  NOT NULL,
  `is_admin`   TINYINT(1)   NOT NULL DEFAULT 0,
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email`    (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Libros ────────────────────────────────────────────────
CREATE TABLE `books` (
  `id`          INT(11)      NOT NULL AUTO_INCREMENT,
  `title`       VARCHAR(200) NOT NULL,
  `author`      VARCHAR(150) NOT NULL,
  `synopsis`    TEXT         DEFAULT NULL,
  `genre`       VARCHAR(80)  DEFAULT NULL,
  `year`        SMALLINT(6)  DEFAULT NULL,
  `cover_color` VARCHAR(20)  NOT NULL DEFAULT '#7c6f64',
  `cover_image` VARCHAR(500) DEFAULT NULL,
  `created_by`  INT(11)      DEFAULT NULL,
  `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `orden`       INT(11)      DEFAULT 99,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Relación usuario-libro ────────────────────────────────
CREATE TABLE `user_books` (
  `id`         INT(11)    NOT NULL AUTO_INCREMENT,
  `user_id`    INT(11)    NOT NULL,
  `book_id`    INT(11)    NOT NULL,
  `status`     ENUM('quiero_leer','leyendo','leido') NOT NULL DEFAULT 'quiero_leer',
  `rating`     TINYINT(4) DEFAULT NULL,
  `liked`      TINYINT(4) DEFAULT NULL,
  `comment`    TEXT       DEFAULT NULL,
  `updated_at` DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_book` (`user_id`, `book_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `user_books_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  CONSTRAINT `user_books_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  DATOS
-- ============================================================

-- ── Admin por defecto (contraseña: admin123) ──────────────
INSERT INTO `users` (`id`, `username`, `email`, `password`, `is_admin`, `created_at`) VALUES
<<<<<<< HEAD
(1, 'admin', 'admin@bookshelf.com', '53a696c7307408c9bc49f8aef1330e987be4897e5b3c644b5b8f994544609296', 1, NOW());
=======
(1, 'admin', 'admin@bookshelf.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1, NOW());
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb

-- ── Libros ────────────────────────────────────────────────
INSERT INTO `books` (`id`, `title`, `author`, `synopsis`, `genre`, `year`, `cover_color`, `cover_image`, `created_by`, `orden`) VALUES

-- Mistborn (1-3)
(1, 'Mistborn: El Imperio Final',
    'Brandon Sanderson',
    'Durante mil años el Lord Legislador ha gobernado un mundo de cenizas y niebla. Una ladrona de élite y su banda de forajidos planean la revolución más imposible de la historia.',
    'Fantasía', 2006, '#1e3a5f',
    'https://covers.openlibrary.org/b/isbn/9780765311788-L.jpg',
    1, 1),

(2, 'El Pozo de la Ascensión',
    'Brandon Sanderson',
    'Segunda parte de la trilogía Mistborn. Vin y Elend intentan gobernar una ciudad asediada mientras mistborn enemigos y un antiguo mal despiertan en las brumas.',
    'Fantasía', 2007, '#1e3a8a',
    'https://covers.openlibrary.org/b/isbn/9780765316882-L.jpg',
    1, 2),

(3, 'El Héroe de las Eras',
    'Brandon Sanderson',
    'Conclusión de la trilogía Mistborn. Los secretos del Lord Legislador se revelan mientras el mundo se acerca al fin. Vin y Elend afrontan su destino final.',
    'Fantasía', 2008, '#172554',
    'https://covers.openlibrary.org/b/isbn/9780765356147-L.jpg',
    1, 3),

-- Otros autores intercalados (4-6)
(4, 'El Nombre del Viento',
    'Patrick Rothfuss',
    'La historia de Kvothe, un músico, alquimista y guerrero legendario, contada desde su propio punto de vista en tres días de confesión.',
    'Fantasía', 2007, '#7f4f24',
    'https://covers.openlibrary.org/b/isbn/9780756404741-L.jpg',
    1, 4),

(5, 'La Sombra del Viento',
    'Carlos Ruiz Zafón',
    'En la Barcelona de la posguerra, un joven descubre un libro que alguien parece querer destruir. El inicio de una búsqueda que revelará oscuros secretos.',
    'Misterio', 2001, '#991b1b',
    'https://covers.openlibrary.org/b/isbn/9780143034902-L.jpg',
    1, 5),

(6, 'La Casa de los Espíritus',
    'Isabel Allende',
    'Cuatro generaciones de mujeres de la familia Trueba en un país latinoamericano ficticio, entrelazando política, amor y magia.',
    'Realismo Mágico', 1982, '#7e1d5f',
    'https://covers.openlibrary.org/b/isbn/9780553273700-L.jpg',
    1, 6),

-- Stormlight Archive (7-9)
(7, 'El Camino de los Reyes',
    'Brandon Sanderson',
    'El inicio de la épica saga El Archivo de las Tormentas. En Roshar, un mundo devastado por las Tormentas de Alta, el esclavo Kaladin, la estudiosa Shallan y el soldado Dalinar se ven envueltos en una guerra que podría decidir el destino del mundo.',
    'Fantasía', 2010, '#5b4fcf',
    'https://covers.openlibrary.org/b/isbn/9780765326355-L.jpg',
    1, 7),

(8, 'Cien Años de Soledad',
    'Gabriel García Márquez',
    'La saga multigeneracional de la familia Buendía en el mítico pueblo de Macondo. Una obra cumbre del realismo mágico y de la literatura universal.',
    'Realismo Mágico', 1967, '#b45309',
    'https://covers.openlibrary.org/b/isbn/9780060883287-L.jpg',
    1, 8),

(9, 'Palabras de Luz',
    'Brandon Sanderson',
    'Segunda entrega de El Archivo de las Tormentas. Las tramas de Kaladin y Shallan convergen mientras Dalinar intenta unir a los reyes alezi. Los Caballeros Radiantes regresan con poderes que llevan siglos dormidos.',
    'Fantasía', 2014, '#7c3aed',
    'https://covers.openlibrary.org/b/isbn/9780765326362-L.jpg',
    1, 9),

-- Clásicos y resto (10-14)
(10, 'Don Quijote de la Mancha',
     'Miguel de Cervantes',
     'El ingenioso hidalgo don Quijote de la Mancha sale al mundo convencido de ser un caballero andante, acompañado de su fiel escudero Sancho Panza.',
     'Clásico', 1605, '#065f46',
     'https://covers.openlibrary.org/b/isbn/9780060934347-L.jpg',
     1, 10),

(11, 'El Juego de Ender',
     'Orson Scott Card',
     'En el futuro, la humanidad entrena a niños genio para combatir a los insectores alienígenas. Ender Wiggin podría ser la última esperanza de la humanidad.',
     'Ciencia Ficción', 1985, '#155e75',
     'https://covers.openlibrary.org/b/isbn/9780812550702-L.jpg',
     1, 11),

(12, 'Fundación',
     'Isaac Asimov',
     'El matemático Hari Seldon prevé la caída del Imperio Galáctico y crea la Fundación para reducir los siglos de barbarie que seguirán.',
     'Ciencia Ficción', 1951, '#1e3a5f',
     'https://covers.openlibrary.org/b/isbn/9780553293357-L.jpg',
     1, 12),

(13, 'Juramentada',
     'Brandon Sanderson',
     'Tercera entrega de El Archivo de las Tormentas. Dalinar afronta su pasado mientras Kaladin lucha con sus juramentos y Shallan se divide entre sus identidades. La Desolación ha llegado.',
     'Fantasía', 2017, '#4c1d95',
     'https://covers.openlibrary.org/b/isbn/9780765326379-L.jpg',
     1, 13),

(14, '1984',
     'George Orwell',
     'En un estado totalitario, Winston Smith trabaja reescribiendo la historia. Su rebelión silenciosa contra el Gran Hermano lo lleva a un destino inevitable.',
     'Distopía', 1949, '#374151',
     'https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg',
     1, 14),

(15, 'El Mar de las Trenzas Esmeraldas',
     'Brandon Sanderson',
     'En el mundo de Roshar, Lift es una joven con poderes únicos que puede convertir comida en energía espiritual. Esta novela corta explora su historia mientras se enfrenta a un misterioso inquisidor conocido como el Susurrador de Pesadillas en las calles de Yeddaw.',
     'Fantasía', 2016, '#0f4c3a',
     'https://covers.openlibrary.org/b/isbn/9780765387561-L.jpg',
     1, 15);

-- ── Restaurar AUTO_INCREMENT ──────────────────────────────
ALTER TABLE `books`      MODIFY `id` INT(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
ALTER TABLE `users`      MODIFY `id` INT(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
ALTER TABLE `user_books` MODIFY `id` INT(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

COMMIT;
