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
