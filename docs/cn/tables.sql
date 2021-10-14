CREATE TABLE `task` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` varchar(255) DEFAULT NULL,
  `code` int(11) DEFAULT NULL,
  `status` longtext,
  `data` longtext,
  `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP,
  `gmt_modified` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
