CREATE TABLE IF NOT EXISTS client (
    client_id		    SERIAL		    NOT NULL,
    name		        VARCHAR(20)	    NOT NULL,
    password		    VARCHAR(50)	    ,
    session_key         VARCHAR(50)     ,
    room_id		        INT,	
    registration_time	DATE	    NOT NULL,
    PRIMARY KEY(client_id)
);

CREATE TABLE IF NOT EXISTS room (
    room_id	    INT		        NOT NULL,
    room_name	VARCHAR(50)             ,
    password	VARCHAR(100)	NOT NULL,
    admin_id	INT		        NOT NULL,
    PRIMARY KEY(room_id)
);

CREATE TABLE IF NOT EXISTS message (
    id          SERIAL      PRIMARY KEY,
    room_id     INT         NOT NULL,
    client_id   INT         NOT NULL,
    send_time   DATE        NOT NULL,
    message_data        TEXT        NOT NULL
);

ALTER TABLE client
ADD CONSTRAINT fk_room_id FOREIGN KEY (room_id) REFERENCES room(room_id);

ALTER TABLE room
ADD CONSTRAINT fk_admin_id FOREIGN KEY (admin_id) REFERENCES client(client_id);

ALTER TABLE message
ADD CONSTRAINT msg_room_rel FOREIGN KEY (room_id) REFERENCES room(room_id),
ADD CONSTRAINT msg_client_rel FOREIGN KEY (client_id) REFERENCES client(client_id);
