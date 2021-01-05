            CREATE DATABASE bounty_data;
	    \c bounty_data;
	    CREATE TABLE IF NOT EXISTS bounty_programs (
                handle varchar(45) PRIMARY KEY,
                offers_bounties BOOLEAN,
                resolved_reports INTEGER, 
                avg_bounty INTEGER
            );
	    CREATE TABLE IF NOT EXISTS domains (
                asset_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                handle varchar(45) NOT NULL,
                asset_value varchar(200),
                asset_type varchar(20),
                CONSTRAINT fk_handle
                    FOREIGN KEY(handle)
                        REFERENCES bounty_programs(handle)
                        ON DELETE CASCADE 
            );
            CREATE TABLE IF NOT EXISTS hash_table (
                handle varchar(45) PRIMARY KEY,
                hash_value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_ids (
                user_id TEXT NOT NULL PRIMARY KEY,
                filtered INT DEFAULT 0
            );
