# chatus

# add mariadb
docker run --name mariadb -e ALLOW_EMPTY_PASSWORD=yes -v <path_to_local_directory>:/bitnami/mariadb -p 3306:3306 -d --restart unless-stopped bitnami/mariadb:10.3

docker exec -it mariadb mysql -uroot
CREATE DATABASE IF NOT EXISTS chat CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER chat IDENTIFIED BY 'chat';
GRANT ALL PRIVILEGES ON chat.* TO 'chat'@'%';

# add redis
docker run -p 6379:6379 -d redis:5
