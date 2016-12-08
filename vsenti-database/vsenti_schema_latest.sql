-- Note:
-- max int(10) = 4294967295

-- Storing media info
DROP TABLE IF EXISTS `media`;
CREATE TABLE `media` (
  `id` int(10) unsigned NOT NULL UNIQUE auto_increment,
  `name` varchar(255) collate utf8_unicode_ci NOT NULL UNIQUE,
  `website_url` varchar(255) collate utf8_unicode_ci NOT NULL UNIQUE,
  `logo_url` varchar(255) collate utf8_unicode_ci NOT NULL UNIQUE,
  `last_scraped_at` timestamp NOT NULL DEFAULT '1970-01-02 00:00:01',
  `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Storing product info
DROP TABLE IF EXISTS `product`;
CREATE TABLE `product` (
  `id` int(10) unsigned NOT NULL UNIQUE auto_increment,
  `name` varchar(255) collate utf8_unicode_ci NOT NULL UNIQUE,
  `website_url` varchar(255) collate utf8_unicode_ci UNIQUE,
  `logo_url` varchar(255) collate utf8_unicode_ci UNIQUE,
  `description` text collate utf8_unicode_ci,
  `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Storing sentiment types
DROP TABLE IF EXISTS `sentiment`;
CREATE TABLE `sentiment` (
  `id` int(10) unsigned NOT NULL UNIQUE auto_increment,
  `product_id` int(10) unsigned,
  CONSTRAINT `fk_sentiment_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES product(`id`)
    ON DELETE CASCADE,
  `name` varchar(255) collate utf8_unicode_ci NOT NULL UNIQUE,
  `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Storing product articles/comments/posts
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article` (
  `id` int(10) unsigned NOT NULL UNIQUE auto_increment,
  `media_id` int(10) unsigned NOT NULL,
  CONSTRAINT `fk_article_media_id`
    FOREIGN KEY (`media_id`)
    REFERENCES media(`id`)
    ON DELETE CASCADE,
  `content` text collate utf8_unicode_ci NOT NULL,
  `url` varchar(255) collate utf8_unicode_ci NOT NULL,
  `is_analyzed` bool DEFAULT false,
  `published_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Storing article sentiment
DROP TABLE IF EXISTS `article_sentiment`;
CREATE TABLE `article_sentiment` (
  `id` int (10) unsigned NOT NULL UNIQUE auto_increment,
  `article_id` int(10) unsigned NOT NULL,
  CONSTRAINT `fk_article_sentiment_article_id`
    FOREIGN KEY (`article_id`)
    REFERENCES article(`id`)
    ON DELETE CASCADE,
  `sentiment_id` int(10) unsigned NOT NULL,
  CONSTRAINT `fk_article_sentiment_sentiment_id`
    FOREIGN KEY (`sentiment_id`)
    REFERENCES sentiment(`id`)
    ON DELETE CASCADE,
  `confident_score_raw` double NOT NULL,
  `confident_score_scaled` double NOT NULL,
  `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`),
  UNIQUE (`article_id`, `sentiment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
