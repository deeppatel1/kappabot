module.exports = {
    query : async function(query) {
        const { Client } = require('pg');
        const client = new Client();
        await client.connect();
        await client.query(query)
            .then(res => console.log(res.rows[0]))
            .catch(e => console.error(e.stack));
        console.log(query);
        await client.end();
    },

    queryVod : async function(number, message) {
        const { Client } = require('pg');
        const client = new Client();

        var query = "select * from ice order by date desc limit " + number;

        await client.connect();
        await client.query(query)
            .then(res => {
                // console.log(res['rows']);
                const num = parseInt(number);
                var i = 0;
                var mToSend = "";
                
                while (i < num) {
                    mToSend += res['rows'][i]['url'] + "\t" + res['rows'][i]['date'] + "\n"
                    // console.log(res['rows'][i]['url']);
                    i++;
                }
                message.channel.send(mToSend);
            })
            .catch(e => console.error(e.stack));
        await client.end();
    }
 }