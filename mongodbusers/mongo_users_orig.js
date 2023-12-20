
print("Starting admin users creation");

db = db.getSiblingDB('admin');

if (!db.getUser("privado-dba")) {
   db.createUser(
     {
       user: "privado-dba",
       pwd:  "PRIVADO_DBA_PSW",
       roles: [ { role: "dbAdminAnyDatabase", db: "admin"}, { role: "readWriteAnyDatabase", db: "admin"}]
     }
   );
} else { print("Skipped creating user: 'privado-dba', user already exists"); }

db = db.getSiblingDB('privado-users')

if (!db.getUser("enterprise-default-user")) {
    db.createUser(
      {
        user: "enterprise-default-user",
        pwd:  "CONFIG_USERS_PSW",
        roles: [ { role: "readWrite", db: "enterprise-users" }, { role: "readWrite", db: "chat" }, { role: "readWrite", db: "idp" }]
      }
    );
} else { print("Skipped creating user: 'enterprise-default-user', user already exists"); }
