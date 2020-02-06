var api_key = null;
var user_id = null;
var session_id = null;
var token = null;

async function refresh_user_state() {
    let response = await fetch('/rest/v1/otapp/user/enter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({
            user_id: user_id
        })
    });
    return await response.json();
}

async function form_user_submit(value) {
    if (user_id === null) {
        if (value.length > 3) {
            user_id = value;
            return await refresh_user_state();
        }
    } else {
        await fetch('/rest/v1/otapp/user/exit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({
                user_id: user_id
            })
        });
    }
    api_key = null;
    user_id = null;
    session_id = null;
    token = null;
    return null;
}

async function callup(addressee) {
    let response = await fetch('/rest/v1/otapp/session/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({
            user_id: user_id,
        })
    });
    let data = await response.json();
    api_key = data.api_key;
    session_id = data.session_id;
    token = data.token;
    await fetch('/rest/v1/otapp/session/call', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({
            user_id: user_id,
            session_id: session_id,
            addressee: addressee
        })
    });
}

async function pickup(session_id_) {
    let response = await fetch('/rest/v1/otapp/session/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({
            user_id: user_id,
            session_id: session_id_,
        })
    });
    let data = await response.json();
    api_key = data.api_key;
    session_id = data.session_id;
    token = data.token;
}
