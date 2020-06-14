const express = require('express');
const { exec } = require("child_process");
const app = express();
app.get('/', (req, res) => res.send('Welcome to KVaaS!'));

let utils = {
    verify_token: (user_token)=>{ return !!user_token },
    drop_all_if_oom: ()=>{ if (JSON.stringify(db).length > 10000) db = {} }, // no vuln here, just to prevent db object from being too large
    // redis_host: `1.1.1.1`,
    // redis_set: `redis-cli -h ${utils.redis_host} set `,
    // redis_get: `redis-cli -h ${utils.redis_host} get `,
};

let db = {};

app.get('/set', (req, res) => {
    utils.drop_all_if_oom(); // prevent db object from getting too big
    const {user_token, key, value} = req.query;
    if (!utils.verify_token(user_token) || !value) return res.send("UNAUTHORIZED"); // not a correct query
    if (!db[user_token]) db[user_token] = {}; // create the user's space if not exist in db object
    db[user_token][key] = value; // set the value to the [user_token].[key]
    res.json({ is_success: true })
});

app.get('/get', (req, res) => {
    const {user_token, key} = req.query;
    if (!utils.verify_token(user_token)) return res.send("UNAUTHORIZED"); // not a correct query
    let result = db[user_token];
    if (result) result = result[key];
    res.json({ result: result === undefined ? "null" : result, is_success: result !== undefined })
});

// shou: DEPRECATED! don't use it!!!!!!
app.put('/backup', (req, res) => {
    let db_stream = Buffer.from(JSON.stringify(db)); // prevent RCE!
    const cmd = utils.redis_set + `db ${db_stream.toString('base64')}`;
    exec(cmd, (err,_,__) => {
        if (err) return res.json({ is_success: false });
        res.json({ is_success: true });
    });
});

app.listen(1003, () => console.log(`Started...`));
