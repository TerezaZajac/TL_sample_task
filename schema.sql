CREATE TABLE `container` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `status` varchar(7) NOT NULL,
  `cpu` smallint DEFAULT NULL,
  `addresses` text,
  `memory_usage` bigint DEFAULT NULL,
  `created_at_utc` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
