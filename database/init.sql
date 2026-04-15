
SET
  SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

SET
  time_zone = "+00:00";

-- Create database if it doesn't exist 
CREATE DATABASE IF NOT EXISTS `ai_recommender_db` DEFAULT CHARACTER
SET
  utf8mb4 COLLATE utf8mb4_hungarian_ci;

USE `ai_recommender_db`;


CREATE TABLE
  IF NOT EXISTS `accounts` (
    `id` int (11) NOT NULL AUTO_INCREMENT,
    `username` varchar(25) NOT NULL,
    `password` varchar(72) NOT NULL,
    `full_name` varchar(40) DEFAULT NULL,
    `email` varchar(40) NOT NULL,
    `phone_number` varchar(20) DEFAULT NULL,
    `date_of_birth` DATE DEFAULT NULL,
    `date_of_create` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `profile_picture` VARCHAR(255) DEFAULT NULL,
    `bio` TEXT DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`)
    UNIQUE KEY `email` (`email`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_hungarian_ci;


CREATE TABLE
  IF NOT EXISTS `posts` (
    `id` int (11) NOT NULL AUTO_INCREMENT,
    `user_id` int (11) NOT NULL,
    `image` blob DEFAULT NULL,
    `text` text DEFAULT NULL, 
    `date_of_post` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `user_id_fk` (`user_id`),
    CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_hungarian_ci;


CREATE TABLE
  IF NOT EXISTS `comments` (
    `id` int (11) NOT NULL AUTO_INCREMENT,
    `user_id` int (11) NOT NULL,
    `post_id` int (11) NOT NULL,
    `text` text NOT NULL,
    `date_of_comment` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `comments_user_id_fk` (`user_id`),
    KEY `comments_post_id_fk` (`post_id`),
    CONSTRAINT `comments_post_id_fk` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `comments_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_hungarian_ci;


CREATE TABLE
  IF NOT EXISTS `liked_posts` (
    `id` int (11) NOT NULL AUTO_INCREMENT,
    `user_id` int (11) NOT NULL,
    `post_id` int (11) NOT NULL,
    `date_of_like` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `liked_user_id_fk` (`user_id`),
    KEY `liked_post_id_fk` (`post_id`),
    CONSTRAINT `liked_post_id_fk` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `liked_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_hungarian_ci;


CREATE TABLE
  IF NOT EXISTS `follows` (
    `id` int (11) NOT NULL AUTO_INCREMENT,
    `following_id` int (11) NOT NULL,
    `follower_id` int (11) NOT NULL,
    `date_of_follow` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_follow` (`following_id`, `follower_id`),
    KEY `following_id_fk` (`following_id`),
    KEY `follower_id_fk` (`follower_id`),
    CONSTRAINT `following_id_fk` FOREIGN KEY (`following_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `follower_id_fk` FOREIGN KEY (`follower_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE
  tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
  );


CREATE TABLE
  post_tags (
    post_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
  );


ALTER TABLE `liked_posts` ADD UNIQUE KEY `unique_user_post_like` (`user_id`, `post_id`);

COMMIT;