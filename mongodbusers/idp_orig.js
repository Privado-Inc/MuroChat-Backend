
db = db.getSiblingDB('idp')
if (!db.idp_config.findOne({ type: 'OKTA'})) {
  db.idp_config.insertOne({
    'type': 'OKTA',
    'clientSecret': '',
    'clientId': 'OKTA_CLIENT_ID',
    'domain': 'OKTA_INTROSPECT_DOMAIN',
    'accountId': '',
    'status': 0,
    'createdAt': { "$type": "date" }
  })
} else { print("Skipped idp configuration insertion. Already exist."); }
