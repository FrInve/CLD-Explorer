CREATE DATABASE IF NOT EXISTS cld;
USE cld;
CREATE TABLE IF NOT EXISTS nodes_custom (
    cldID INT NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    pos_x DOUBLE,
    pos_y DOUBLE,
    PRIMARY KEY (cldID, node_name) -- Assuming a composite primary key
);

CREATE TABLE IF NOT EXISTS relationships_custom (
    relationshipID INT NOT NULL PRIMARY KEY,
    type TEXT,
    delay TEXT,
    cldID INT NOT NULL,
    FOREIGN KEY (cldID) REFERENCES nodes_custom(cldID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS routes_custom (
    cldID INT NOT NULL,
    routeID INT NOT NULL,
    start_node TEXT,
    end_node TEXT,
    route TEXT,
    route_length INT,
    state TEXT,
    PRIMARY KEY (cldID, routeID),
    FOREIGN KEY (cldID) REFERENCES nodes_custom(cldID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loops_custom (
    cldID INT NOT NULL,
    loopID INT NOT NULL,
    loop_path TEXT,
    state TEXT,
    loop_length INT,
    PRIMARY KEY (cldID, loopID),
    FOREIGN KEY (cldID) REFERENCES nodes_custom(cldID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bridge_nodes_loops_custom (
    cldID INT NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    loopID INT NOT NULL,
    PRIMARY KEY (cldID, node_name, loopID),
    FOREIGN KEY (cldID, node_name) REFERENCES nodes_custom(cldID, node_name) ON DELETE CASCADE,
    FOREIGN KEY (cldID, loopID) REFERENCES loops_custom(cldID, loopID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bridge_rel_loops_custom (
    cldID INT NOT NULL,
    relationshipID INT NOT NULL,
    loopID INT NOT NULL,
    type_rel VARCHAR(255),
    delay TEXT,
    PRIMARY KEY (cldID, relationshipID, loopID),
    FOREIGN KEY (cldID, relationshipID) REFERENCES relationships_custom(cldID, relationshipID) ON DELETE CASCADE,
    FOREIGN KEY (cldID, loopID) REFERENCES loops_custom(cldID, loopID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bridge_nodes_routes_custom (
    cldID INT NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    routeID INT NOT NULL,
    PRIMARY KEY (cldID, node_name, routeID),
    FOREIGN KEY (cldID, node_name) REFERENCES nodes_custom(cldID, node_name) ON DELETE CASCADE,
    FOREIGN KEY (cldID, routeID) REFERENCES routes_custom(cldID, routeID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bridge_rel_routes_custom (
    cldID INT NOT NULL,
    relationshipID INT NOT NULL,
    routeID INT NOT NULL,
    type_rel VARCHAR(255),
    delay TEXT,
    PRIMARY KEY (cldID, relationshipID, routeID),
    FOREIGN KEY (cldID, relationshipID) REFERENCES relationships_custom(cldID, relationshipID) ON DELETE CASCADE,
    FOREIGN KEY (cldID, routeID) REFERENCES routes_custom(cldID, routeID) ON DELETE CASCADE
);
