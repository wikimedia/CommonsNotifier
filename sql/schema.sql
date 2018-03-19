CREATE TABLE commons_deletions (
    title VARCHAR(255) BINARY NOT NULL,
    deletion_type ENUM('speedy', 'discussion') NOT NULL,
    first_seen DATETIME NOT NULL DEFAULT now(),
    state ENUM('new', 'notifying', 'notified', 'maybe gone', 'gone') NOT NULL DEFAULT 'new',
    retries INT NOT NULL DEFAULT 0,
    touched TIMESTAMP NOT NULL DEFAULT now(),

    PRIMARY KEY (title, deletion_type),
    KEY(touched)
) ENGINE=InnoDB DEFAULT CHARSET=BINARY;
