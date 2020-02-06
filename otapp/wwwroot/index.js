var api_key = null;
var user_id = null;
var session_id = null;
var session = null;
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
        if (session !== null) {
            session.disconnect();
            session = null;
        }
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
    open_session();
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
    open_session();
}

////////
var publisher;

function open_session() {
    if (session !== null) {
       session.disconnect();
    }


    session = OT.initSession(api_key, session_id);
    publisher = OT.initPublisher('publisher');

    // Attach event handlers
    session.on({

        // This function runs when session.connect() asynchronously completes
        sessionConnected: function (event) {
            // Publish the publisher we initialzed earlier (this will trigger 'streamCreated' on other
            // clients)
            session.publish(publisher, function (error) {
                if (error) {
                    console.error('Failed to publish', error);
                }
            });
        },

        // This function runs when another client publishes a stream (eg. session.publish())
        streamCreated: function (event) {
            // Create a container for a new Subscriber, assign it an id using the streamId, put it inside
            // the element with id="subscribers"
            var subContainer = document.createElement('div');
            subContainer.id = 'stream-' + event.stream.streamId;
            document.getElementById('subscribers').appendChild(subContainer);

            // Subscribe to the stream that caused this event, put it inside the container we just made
            session.subscribe(event.stream, subContainer, function (error) {
                if (error) {
                    console.error('Failed to subscribe', error);
                }
            });
        }

    });

    session.connect(token, function (error) {
        if (error) {
            console.error('Failed to connect', error);
        }
    });

}


