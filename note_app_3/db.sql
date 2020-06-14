CREATE DATABASE na3;
USE na3;
DROP TABLE IF EXISTS `notes`;

CREATE TABLE `notes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `content` longtext,
  `token` varchar(255) DEFAULT NULL,
  `author_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
);
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
ALTER TABLE users ADD UNIQUE (username);
INSERT INTO `users` VALUES (2,'mr.admin','2bAc44Kv4Ps4wA7y','2bAc44Kv4Ps4wA7y');
