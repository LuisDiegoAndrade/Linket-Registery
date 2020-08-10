
    'use strict';


    let targetedUser = null;
    let pc = null;
    let me = null;
    let sending_channel = null;
    let receiving_channel = null;

    async function getUsername() {
      const res = await fetch("./getusername", {method:"post"});
      const json = await res.json();
      me = json.username;
    } getUsername();

    function messageServer(msgObj){
      socket.send(JSON.stringify(msgObj));
    }

    async function makePeerConnection() {
      console.log("Creating peer connection!");
      pc = new RTCPeerConnection( {"iceServers": [{"url": "stun:stun.l.google.com:19302"}]} );
      pc.onicecandidate = handleICECandidateEvent;
      pc.onnegotiationneeded = handleNegotiationNeededEvent;
      //pc.oniceconnectionstatechange = #Add E.H if needed;
      //pc.onicegatheringstatechange = # Add E.H if needed;

    }


    async function handleNegotiationNeededEvent() {
      try {

        console.log("handleNegotiationNeededEvent executing!")
        const offer = await pc.createOffer();

        if (pc.signalingState != "stable") {
          console.log("Connection is not stable yet.")
          return;
        }

        await pc.setLocalDescription(offer);

        messageServer( {type: "channel-offer", sender: me, target: targetedUser, sdp: pc.localDescription} );


      } catch(err){
        console.log(err);
      }
    }

    function handleICECandidateEvent(event) {
        if (event.candidate) {
          console.log("Handeling Ice candidate event: " + targetedUser);
          messageServer( {type: "new-ice-candidate", target: targetedUser, candidate: event.candidate} );
        }
    }

    async function handleChannelOffer(msg) {
      if (!window.confirm("Connect to " + msg.sender + "?")) {
        alert("Connection denied!");
        return;
      }
      if(!pc) {
        makePeerConnection();
        pc.ondatachannel = receiveChannelCallback;
      }


      let description = new RTCSessionDescription(msg.sdp);

      // If the connection isn't stable yet, wait for it...
      if (pc.signalingState != "stable") {
        console.log("Signaling state isn't stable, so triggering rollback.");

        // Set the local and remove descriptions for rollback; don't proceed
        // until both return.
        await Promise.all([
          pc.setLocalDescription({type: "rollback"}),
          pc.setRemoteDescription(description)
        ]);
        return;
      } else {
        console.log("Setting remote description!");
        await pc.setRemoteDescription(description);
      }

      console.log("Creating and sending answer to caller.");
      await pc.setLocalDescription(await pc.createAnswer());
      console.log("Handleing channel offer" + msg.sender);
      targetedUser = msg.sender;
      messageServer( {type: "channel-answer", sender: me, target: msg.sender, sdp: pc.localDescription} );


    }

    async function handleChannelAnswer(msg) {
      console.log("Call recipient has accepted our call! (" + msg.sender + ")");

      // Configure the remote description, which is the SDP payload
      // in our "channel-answer" message.

      let description = new RTCSessionDescription(msg.sdp);
      await pc.setRemoteDescription(description).catch((err) => console.log(err));


    }

    async function handleNewICECandidate(msg) {
      let candidate = new RTCIceCandidate(msg.candidate);

      console.log("Adding received ICE candidate: " + JSON.stringify(candidate));
      try {
        await pc.addIceCandidate(candidate)
      } catch(err) {
        console.log(err)
      }
    }

    function senderChannelStatusChange(event) {
      if (sending_channel){
        if(sending_channel.readyState === "open") {
          alert("Peer opened data channel!");
          document.getElementById('chat').style.display = 'block';
          document.getElementById('connect').style.display = 'none';

          let chat = document.getElementById('chat');
          chat.addEventListener('submit', (e) => {
            e.preventDefault();
            let data = new FormData(chat);
            sending_channel.send(data.get('msg'))
            let msg = document.createElement('p');
            msg.setAttribute('class', 'alert alert-info alert-dismissible');
            msg.textContent = data.get('msg');
            document.getElementById('chatBox').appendChild(msg);
            document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;
            chat.reset();

          });

        }
        else {
          alert("Peer closed data channel!");
        }
      }
    }

    function receiveChannelCallback(event) {
      receiving_channel = event.channel;
      receiving_channel.onmessage = receiveMessage;
      receiving_channel.onopen = handleReceiveChannelStatusChange;
      receiving_channel.onclose = handleReceiveChannelStatusChange;
    }

    function receiveMessage(event) {
      //alert("Peer says: " + event.data);
      let msg = document.createElement('p');
      msg.setAttribute('class', 'alert alert-danger');
      msg.textContent = event.data;
      document.getElementById('chatBox').appendChild(msg);
      document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;

    }

    function handleReceiveChannelStatusChange() {
      if(receiving_channel.readyState === "open") {
        alert("Ready to chat!");
        document.getElementById('chat').style.display = 'block';
        document.getElementById('connect').style.display = 'none';

        let chat = document.getElementById('chat');
        chat.addEventListener('submit', (e) => {
          e.preventDefault();
          let data = new FormData(chat);
          receiving_channel.send(data.get('msg'));
          let msg = document.createElement('p');
          msg.setAttribute('class', 'alert alert-info alert-dismissible');
          msg.textContent = data.get('msg');
          document.getElementById('chatBox').appendChild(msg);
          document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;
          chat.reset();

        });
      }
      else {
        alert("Peer closed data channel!");
      }
    }


    let socket = io(window.location.protocol + "//" + window.location.hostname + ":" + window.location.port);
    socket.on('connect', () => {
      console.log("Connected to WS server!");

      // Add UI to allow "active / inactive" status
      //For now all connections are in an "active" state
      //Let the server know who you are
      socket.emit("New Connection", JSON.stringify( {status: "active"} ) );
    });



    //Handle messages from ws server
    socket.on('message', (data) => {
      console.log("Message from signaling server!")
      data = JSON.parse(data);

      switch (data.type) {
        case 'channel-offer':
          handleChannelOffer(data);
          break;

        case 'channel-answer':
          handleChannelAnswer(data);
          break;

        case 'new-ice-candidate':
          handleNewICECandidate(data);
          break;

      }
    });


    let connect = document.getElementById('connect');
    connect.addEventListener('submit', (e) => {
      e.preventDefault();

      let data = new FormData(connect);
      targetedUser = data.get('target');
      makePeerConnection();
      sending_channel = pc.createDataChannel("data-channel");
      sending_channel.onmessage = receiveMessage;
      sending_channel.onopen = senderChannelStatusChange;
      sending_channel.onclose = senderChannelStatusChange;

    });
