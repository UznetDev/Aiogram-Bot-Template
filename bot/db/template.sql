CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL UNIQUE,
    `initiator_user_id` BIGINT,
    `updater_user_id` BIGINT,
    `role` ENUM('admin', 'moderator') DEFAULT 'admin',
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` TIMESTAMP NULL DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `admin_rights` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `admin_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `value` BOOLEAN NOT NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    `description` TEXT,
    `initiator_user_id` BIGINT,
    `updater_user_id` BIGINT,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `deleted_at` TIMESTAMP NULL,
    UNIQUE KEY `uq_admin_feature` (`admin_id`,`name`),
    CONSTRAINT `fk_rights_admin`
        FOREIGN KEY (`admin_id`) REFERENCES `admins`(`id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;